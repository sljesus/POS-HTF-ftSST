"""
Ventana de Historial de Ventas para HTF POS
Usando componentes reutilizables del sistema de diseño
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QDateEdit, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QDate
import logging
from datetime import datetime

# Importar componentes del sistema de diseño
from ui.components import (
    WindowsPhoneTheme,
    TileButton,
    create_page_layout,
    ContentPanel,
    StyledLabel,
    show_info_dialog,
    show_warning_dialog
)


class HistorialVentasWindow(QWidget):
    """Widget para ver historial de ventas"""
    
    cerrar_solicitado = Signal()
    
    def __init__(self, pg_manager, supabase_service, user_data, parent=None):
        super().__init__(parent)
        self.pg_manager = pg_manager
        self.supabase_service = supabase_service
        self.user_data = user_data
        
        # Configurar política de tamaño
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar interfaz de historial"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Contenido
        content = QWidget()
        content_layout = create_page_layout("HISTORIAL COMPLETO")
        content.setLayout(content_layout)
        
        # Filtros
        self.create_filters(content_layout)
        
        # Tabla
        self.create_history_table(content_layout)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        btn_buscar = TileButton("Buscar", "fa5s.search", WindowsPhoneTheme.TILE_BLUE)
        btn_buscar.clicked.connect(self.buscar_ventas)
        
        btn_exportar = TileButton("Exportar", "fa5s.download", WindowsPhoneTheme.TILE_GREEN)
        btn_exportar.clicked.connect(self.exportar_datos)
        
        btn_cerrar = TileButton("Cerrar", "fa5s.times", WindowsPhoneTheme.TILE_RED)
        btn_cerrar.clicked.connect(self.cerrar_solicitado.emit)
        
        buttons_layout.addWidget(btn_buscar)
        buttons_layout.addWidget(btn_exportar)
        buttons_layout.addWidget(btn_cerrar)
        
        content_layout.addLayout(buttons_layout)
        layout.addWidget(content)
        
        # Cargar datos iniciales
        self.buscar_ventas()
        
    def create_filters(self, parent_layout):
        """Crear filtros de búsqueda"""
        filters_panel = ContentPanel()
        filters_layout = QHBoxLayout(filters_panel)
        
        # Fecha desde
        filters_layout.addWidget(StyledLabel("Desde:", bold=True))
        self.fecha_desde = QDateEdit()
        self.fecha_desde.setDate(QDate.currentDate().addDays(-30))
        self.fecha_desde.setCalendarPopup(True)
        filters_layout.addWidget(self.fecha_desde)
        
        # Fecha hasta
        filters_layout.addWidget(StyledLabel("Hasta:", bold=True))
        self.fecha_hasta = QDateEdit()
        self.fecha_hasta.setDate(QDate.currentDate())
        self.fecha_hasta.setCalendarPopup(True)
        filters_layout.addWidget(self.fecha_hasta)
        
        filters_layout.addStretch()
        parent_layout.addWidget(filters_panel)
        
    def create_history_table(self, parent_layout):
        """Crear tabla de historial"""
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            "ID", "Fecha", "Hora", "Total", "Usuario", "Detalles"
        ])
        
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        parent_layout.addWidget(self.history_table)
        
    def buscar_ventas(self):
        """Buscar ventas por rango de fechas"""
        try:
            fecha_desde = self.fecha_desde.date().toPython()
            fecha_hasta = self.fecha_hasta.date().toPython()
            
            self.cargar_historial(fecha_desde, fecha_hasta)
            
        except Exception as e:
            logging.error(f"Error buscando ventas: {e}")
            show_warning_dialog(self, "Error", f"Error al buscar ventas: {e}")
            
    def cargar_historial(self, fecha_desde, fecha_hasta):
        """Cargar historial de ventas desde la base de datos"""
        try:
            cursor = self.pg_manager.connection.cursor()
            cursor.execute("""
                SELECT 
                    v.id_venta, 
                    v.fecha, 
                    v.total, 
                    u.nombre_completo as usuario
                FROM ventas v
                JOIN usuarios u ON v.id_usuario = u.id_usuario
                WHERE DATE(v.fecha) BETWEEN %s AND %s
                ORDER BY v.fecha DESC
            """, (fecha_desde, fecha_hasta))
            
            ventas = cursor.fetchall()
            
            self.history_table.setRowCount(len(ventas))
            
            for row, venta in enumerate(ventas):
                # ID
                self.history_table.setItem(row, 0, QTableWidgetItem(str(venta['id_venta'])))
                
                # Fecha
                fecha = venta['fecha'].strftime("%d/%m/%Y") if isinstance(venta['fecha'], datetime) else str(venta['fecha'])
                self.history_table.setItem(row, 1, QTableWidgetItem(fecha))
                
                # Hora
                hora = venta['fecha'].strftime("%H:%M") if isinstance(venta['fecha'], datetime) else "N/A"
                self.history_table.setItem(row, 2, QTableWidgetItem(hora))
                
                # Total
                total_item = QTableWidgetItem(f"${venta['total']:.2f}")
                total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.history_table.setItem(row, 3, total_item)
                
                # Usuario
                self.history_table.setItem(row, 4, QTableWidgetItem(venta.get('usuario', 'N/A')))
                
                # Botón detalles
                btn_detalles = QPushButton("Ver")
                btn_detalles.setObjectName("tileButton")
                btn_detalles.setProperty("tileColor", WindowsPhoneTheme.TILE_BLUE)
                btn_detalles.clicked.connect(lambda checked, vid=venta['id_venta']: self.ver_detalles(vid))
                self.history_table.setCellWidget(row, 5, btn_detalles)
                
        except Exception as e:
            logging.error(f"Error cargando historial de ventas: {e}")
            show_warning_dialog(self, "Error", f"No se pudo cargar el historial: {e}")
            
    def ver_detalles(self, venta_id):
        """Ver detalles de una venta"""
        try:
            cursor = self.pg_manager.connection.cursor()
            cursor.execute("""
                SELECT 
                    dv.codigo_interno,
                    dv.tipo_producto,
                    dv.cantidad,
                    dv.precio_unitario,
                    dv.subtotal_linea,
                    dv.nombre_producto,
                    dv.descripcion_producto
                FROM detalles_venta dv
                WHERE dv.id_venta = %s
            """, (venta_id,))
            
            detalles = cursor.fetchall()
            
            if not detalles:
                show_info_dialog(self, "Detalles", f"No se encontraron detalles para la venta ID: {venta_id}")
                return
                
            # Crear mensaje con los detalles
            mensaje = f"Detalles de la venta ID: {venta_id}\n\n"
            mensaje += "Producto\t\tCantidad\tPrecio\tSubtotal\n"
            mensaje += "------------------------------------------------\n"
            
            for detalle in detalles:
                nombre = detalle['nombre_producto'][:20] + "..." if len(detalle['nombre_producto']) > 20 else detalle['nombre_producto']
                mensaje += f"{nombre}\t{detalle['cantidad']}\t${detalle['precio_unitario']:.2f}\t${detalle['subtotal_linea']:.2f}\n"
            
            show_info_dialog(self, "Detalles de Venta", mensaje)
            
        except Exception as e:
            logging.error(f"Error obteniendo detalles de venta: {e}")
            show_warning_dialog(self, "Error", f"No se pudieron obtener los detalles: {e}")
        
    def exportar_datos(self):
        """Exportar datos a archivo"""
        try:
            from datetime import datetime
            import os
            
            # Verificar si openpyxl está disponible
            try:
                from openpyxl import Workbook
                from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
            except ImportError:
                show_warning_dialog(
                    self,
                    "Biblioteca requerida",
                    "Para exportar a Excel necesitas instalar openpyxl",
                    detail="Ejecuta: pip install openpyxl"
                )
                return
            
            # Obtener rango de fechas
            fecha_desde = self.fecha_desde.date().toPython()
            fecha_hasta = self.fecha_hasta.date().toPython()
            
            # Obtener datos de ventas
            cursor = self.pg_manager.connection.cursor()
            cursor.execute("""
                SELECT 
                    v.id_venta, 
                    v.fecha, 
                    v.total, 
                    u.nombre_completo as usuario
                FROM ventas v
                JOIN usuarios u ON v.id_usuario = u.id_usuario
                WHERE DATE(v.fecha) BETWEEN %s AND %s
                ORDER BY v.fecha DESC
            """, (fecha_desde, fecha_hasta))
            
            ventas = cursor.fetchall()
            
            # Crear libro de Excel
            wb = Workbook()
            ws = wb.active
            ws.title = "Historial de Ventas"
            
            # Estilos
            header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
            header_font = Font(bold=True, color="FFFFFF", size=12)
            header_alignment = Alignment(horizontal="center", vertical="center")
            
            border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            # Encabezados
            headers = ["ID Venta", "Fecha", "Hora", "Total", "Usuario"]
            
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = header_alignment
                cell.border = border
            
            # Datos
            for row, venta in enumerate(ventas, 2):
                ws.cell(row=row, column=1, value=venta['id_venta']).border = border
                
                # Fecha
                fecha = venta['fecha'].strftime("%d/%m/%Y") if isinstance(venta['fecha'], datetime) else str(venta['fecha'])
                ws.cell(row=row, column=2, value=fecha).border = border
                
                # Hora
                hora = venta['fecha'].strftime("%H:%M") if isinstance(venta['fecha'], datetime) else "N/A"
                ws.cell(row=row, column=3, value=hora).border = border
                
                # Total
                total_cell = ws.cell(row=row, column=4, value=venta['total'])
                total_cell.number_format = '$#,##0.00'
                total_cell.border = border
                
                # Usuario
                ws.cell(row=row, column=5, value=venta.get('usuario', 'N/A')).border = border
            
            # Ajustar anchos de columna
            ws.column_dimensions['A'].width = 12
            ws.column_dimensions['B'].width = 15
            ws.column_dimensions['C'].width = 10
            ws.column_dimensions['D'].width = 15
            ws.column_dimensions['E'].width = 25
            
            # Guardar archivo
            fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            filename = os.path.join(desktop, f"historial_ventas_{fecha_str}.xlsx")
            
            wb.save(filename)
            
            show_info_dialog(
                self,
                "Exportación completada",
                f"El historial de ventas ha sido exportado exitosamente",
                detail=f"Archivo guardado en:\n{filename}"
            )
            
            logging.info(f"Historial de ventas exportado: {filename}")
            
        except Exception as e:
            logging.error(f"Error exportando datos: {e}")
            show_warning_dialog(
                self,
                "Error al exportar",
                "No se pudo exportar el historial de ventas",
                detail=str(e)
            )