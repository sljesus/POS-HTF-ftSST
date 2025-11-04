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
    
    def __init__(self, db_manager, supabase_service, user_data, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
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
            
            ventas = self.db_manager.get_sales_by_date_range(fecha_desde, fecha_hasta)
            
            self.history_table.setRowCount(len(ventas))
            
            for row, venta in enumerate(ventas):
                # ID
                self.history_table.setItem(row, 0, QTableWidgetItem(str(venta['id_venta'])))
                
                # Fecha
                fecha = venta['fecha_venta'].strftime("%d/%m/%Y") if isinstance(venta['fecha_venta'], datetime) else str(venta['fecha_venta'])
                self.history_table.setItem(row, 1, QTableWidgetItem(fecha))
                
                # Hora
                hora = venta['fecha_venta'].strftime("%H:%M") if isinstance(venta['fecha_venta'], datetime) else "N/A"
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
            logging.error(f"Error buscando ventas: {e}")
            show_warning_dialog(self, "Error", f"Error al buscar ventas: {e}")
            
    def ver_detalles(self, venta_id):
        """Ver detalles de una venta"""
        # TODO: Implementar ventana de detalles de venta
        show_info_dialog(self, "Detalles", f"Ver detalles de venta ID: {venta_id}")
        
    def exportar_datos(self):
        """Exportar datos a archivo"""
        show_info_dialog(self, "Exportar", "Función de exportación por implementar")
