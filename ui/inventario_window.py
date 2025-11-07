"""
Ventana de Grid de Inventario para HTF POS
Usando componentes reutilizables del sistema de diseño
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QSizePolicy, QFrame
)
from PySide6.QtCore import Qt, Signal
import logging

# Importar componentes del sistema de diseño
from ui.components import (
    WindowsPhoneTheme,
    TileButton,
    create_page_layout,
    ContentPanel,
    StyledLabel,
    SearchBar,
    show_info_dialog,
    show_warning_dialog,
    show_error_dialog
)


class InventarioWindow(QWidget):
    """Widget para ver el grid completo de inventario"""
    
    cerrar_solicitado = Signal()
    
    def __init__(self, db_manager, supabase_service, user_data, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.supabase_service = supabase_service
        self.user_data = user_data
        self.productos_data = []
        
        self.setup_ui()
        self.cargar_inventario()
    
    def setup_ui(self):
        """Configurar interfaz de inventario"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Contenido
        content = QWidget()
        content_layout = create_page_layout("INVENTARIO COMPLETO")
        content.setLayout(content_layout)
        
        # Buscador
        self.search_bar = SearchBar("Buscar por código, nombre o categoría...")
        self.search_bar.connect_search(self.filtrar_inventario)
        content_layout.addWidget(self.search_bar)
        
        # Panel para la tabla
        table_panel = ContentPanel()
        table_layout = QVBoxLayout(table_panel)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tabla de inventario
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(8)
        self.inventory_table.setHorizontalHeaderLabels([
            "Código", "Nombre", "Categoría", "Precio", "Stock", "Stock Min", "Ubicación", "Estado"
        ])
        
        # Configurar header
        header = self.inventory_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        
        self.inventory_table.verticalHeader().setVisible(False)
        self.inventory_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.inventory_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.inventory_table.setAlternatingRowColors(True)
        self.inventory_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Aplicar estilos a la tabla
        self.inventory_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: white;
                border: none;
                gridline-color: #e5e7eb;
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid #e5e7eb;
            }}
            QTableWidget::item:selected {{
                background-color: {WindowsPhoneTheme.TILE_BLUE};
                color: white;
            }}
            QHeaderView::section {{
                background-color: {WindowsPhoneTheme.BG_LIGHT};
                color: {WindowsPhoneTheme.PRIMARY_BLUE};
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid {WindowsPhoneTheme.TILE_BLUE};
                font-weight: bold;
                font-family: '{WindowsPhoneTheme.FONT_FAMILY}';
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
            }}
        """)
        
        table_layout.addWidget(self.inventory_table)
        content_layout.addWidget(table_panel)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(WindowsPhoneTheme.TILE_SPACING)
        
        btn_actualizar = TileButton("Actualizar", "fa5s.sync", WindowsPhoneTheme.TILE_BLUE)
        btn_actualizar.clicked.connect(self.cargar_inventario)
        
        btn_reporte = TileButton("Generar Reporte", "fa5s.file-excel", WindowsPhoneTheme.TILE_GREEN)
        btn_reporte.clicked.connect(self.generar_reporte)
        
        btn_bajo_stock = TileButton("Ver Bajo Stock", "fa5s.exclamation-triangle", WindowsPhoneTheme.TILE_ORANGE)
        btn_bajo_stock.clicked.connect(self.filtrar_bajo_stock)
        
        btn_cerrar = TileButton("Cerrar", "fa5s.times", WindowsPhoneTheme.TILE_RED)
        btn_cerrar.clicked.connect(self.cerrar_solicitado.emit)
        
        buttons_layout.addWidget(btn_actualizar)
        buttons_layout.addWidget(btn_reporte)
        buttons_layout.addWidget(btn_bajo_stock)
        buttons_layout.addWidget(btn_cerrar)
        
        content_layout.addLayout(buttons_layout)
        layout.addWidget(content)
    
    def cargar_inventario(self):
        """Cargar datos de inventario desde la base de datos"""
        try:
            logging.info("Cargando inventario completo...")
            
            # Consultar inventario con datos de productos
            cursor = self.db_manager.connection.cursor()
            cursor.execute("""
                SELECT 
                    i.codigo_interno,
                    COALESCE(pv.nombre, s.nombre) as nombre,
                    COALESCE(pv.categoria, 'Suplemento') as categoria,
                    COALESCE(pv.precio_venta, s.precio_venta) as precio,
                    i.stock_actual,
                    i.stock_minimo,
                    i.ubicacion,
                    i.activo,
                    i.tipo_producto
                FROM inventario i
                LEFT JOIN ca_productos_varios pv ON i.codigo_interno = pv.codigo_interno
                LEFT JOIN ca_suplementos s ON i.codigo_interno = s.codigo_interno
                ORDER BY i.codigo_interno
            """)
            
            # Convertir a lista de diccionarios
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            self.productos_data = [dict(zip(columns, row)) for row in rows]
            
            self.mostrar_inventario(self.productos_data)
            
            logging.info(f"Inventario cargado: {len(self.productos_data)} productos")
            
        except Exception as e:
            logging.error(f"Error cargando inventario: {e}")
            show_error_dialog(
                self,
                "Error al cargar",
                "No se pudo cargar el inventario",
                detail=str(e)
            )
    
    def mostrar_inventario(self, productos):
        """Mostrar productos en la tabla"""
        self.inventory_table.setRowCount(0)
        
        for row, producto in enumerate(productos):
            self.inventory_table.insertRow(row)
            
            # Código
            self.inventory_table.setItem(row, 0, QTableWidgetItem(producto['codigo_interno']))
            
            # Nombre
            self.inventory_table.setItem(row, 1, QTableWidgetItem(producto['nombre']))
            
            # Categoría
            self.inventory_table.setItem(row, 2, QTableWidgetItem(producto['categoria']))
            
            # Precio
            precio_item = QTableWidgetItem(f"${producto['precio']:.2f}")
            precio_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.inventory_table.setItem(row, 3, precio_item)
            
            # Stock actual
            stock_item = QTableWidgetItem(str(producto['stock_actual']))
            stock_item.setTextAlignment(Qt.AlignCenter)
            
            # Colorear si está bajo en stock
            if producto['stock_actual'] <= producto['stock_minimo']:
                stock_item.setForeground(Qt.red)
            
            self.inventory_table.setItem(row, 4, stock_item)
            
            # Stock mínimo
            stock_min_item = QTableWidgetItem(str(producto['stock_minimo']))
            stock_min_item.setTextAlignment(Qt.AlignCenter)
            self.inventory_table.setItem(row, 5, stock_min_item)
            
            # Ubicación
            ubicacion = producto.get('ubicacion', 'N/A')
            self.inventory_table.setItem(row, 6, QTableWidgetItem(ubicacion))
            
            # Estado
            estado = "Activo" if producto['activo'] else "Inactivo"
            estado_item = QTableWidgetItem(estado)
            if not producto['activo']:
                estado_item.setForeground(Qt.gray)
            self.inventory_table.setItem(row, 7, estado_item)
    
    def filtrar_inventario(self):
        """Filtrar inventario según búsqueda"""
        texto_busqueda = self.search_bar.get_text().lower()
        
        if not texto_busqueda:
            self.mostrar_inventario(self.productos_data)
            return
        
        productos_filtrados = [
            p for p in self.productos_data
            if texto_busqueda in p['codigo_interno'].lower()
            or texto_busqueda in p['nombre'].lower()
            or texto_busqueda in p['categoria'].lower()
        ]
        
        self.mostrar_inventario(productos_filtrados)
        logging.info(f"Filtrado: {len(productos_filtrados)} productos encontrados")
    
    def filtrar_bajo_stock(self):
        """Filtrar productos con stock bajo o menor al mínimo"""
        productos_bajo_stock = [
            p for p in self.productos_data
            if p['stock_actual'] <= p['stock_minimo']
        ]
        
        if productos_bajo_stock:
            self.mostrar_inventario(productos_bajo_stock)
            show_info_dialog(
                self,
                "Productos bajo stock",
                f"Se encontraron {len(productos_bajo_stock)} productos con stock bajo o menor al mínimo"
            )
        else:
            show_info_dialog(
                self,
                "Stock saludable",
                "No hay productos con stock bajo en este momento"
            )
    
    def generar_reporte(self):
        """Generar reporte de inventario en Excel"""
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
                    "Para generar reportes en Excel necesitas instalar openpyxl",
                    detail="Ejecuta: pip install openpyxl"
                )
                return
            
            # Crear libro de Excel
            wb = Workbook()
            ws = wb.active
            ws.title = "Inventario"
            
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
            headers = ["Código", "Nombre", "Categoría", "Precio", "Stock Actual", "Stock Mín", "Ubicación", "Estado"]
            
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = header_alignment
                cell.border = border
            
            # Datos
            for row, producto in enumerate(self.productos_data, 2):
                ws.cell(row=row, column=1, value=producto['codigo_interno']).border = border
                ws.cell(row=row, column=2, value=producto['nombre']).border = border
                ws.cell(row=row, column=3, value=producto['categoria']).border = border
                
                precio_cell = ws.cell(row=row, column=4, value=producto['precio'])
                precio_cell.number_format = '$#,##0.00'
                precio_cell.border = border
                
                stock_cell = ws.cell(row=row, column=5, value=producto['stock_actual'])
                stock_cell.alignment = Alignment(horizontal="center")
                stock_cell.border = border
                
                # Resaltar bajo stock
                if producto['stock_actual'] <= producto['stock_minimo']:
                    stock_cell.font = Font(color="FF0000", bold=True)
                
                stock_min_cell = ws.cell(row=row, column=6, value=producto['stock_minimo'])
                stock_min_cell.alignment = Alignment(horizontal="center")
                stock_min_cell.border = border
                
                ws.cell(row=row, column=7, value=producto.get('ubicacion', 'N/A')).border = border
                ws.cell(row=row, column=8, value="Activo" if producto['activo'] else "Inactivo").border = border
            
            # Ajustar anchos de columna
            ws.column_dimensions['A'].width = 15
            ws.column_dimensions['B'].width = 35
            ws.column_dimensions['C'].width = 15
            ws.column_dimensions['D'].width = 12
            ws.column_dimensions['E'].width = 12
            ws.column_dimensions['F'].width = 12
            ws.column_dimensions['G'].width = 15
            ws.column_dimensions['H'].width = 12
            
            # Guardar archivo
            fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            filename = os.path.join(desktop, f"Inventario_HTF_{fecha_str}.xlsx")
            
            wb.save(filename)
            
            show_info_dialog(
                self,
                "Reporte generado",
                f"El reporte de inventario ha sido generado exitosamente",
                detail=f"Archivo guardado en:\n{filename}"
            )
            
            logging.info(f"Reporte de inventario generado: {filename}")
            
        except Exception as e:
            logging.error(f"Error generando reporte: {e}")
            show_error_dialog(
                self,
                "Error al generar reporte",
                "No se pudo crear el archivo de Excel",
                detail=str(e)
            )
