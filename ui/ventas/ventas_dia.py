"""
Ventana de Ventas del Día para HTF POS
Usando componentes reutilizables del sistema de diseño
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QTableWidget, QTableWidgetItem,
    QHeaderView, QSizePolicy, QDialog, QPushButton, QLabel
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import logging
from datetime import datetime, date

# Importar componentes del sistema de diseño
from ui.components import (
    WindowsPhoneTheme,
    TileButton,
    InfoTile,
    create_page_layout,
    show_info_dialog,
    show_warning_dialog,
    SectionTitle,
    ContentPanel
)


class VentasDiaWindow(QWidget):
    """Widget para ver ventas del día"""
    
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
        """Configurar interfaz de ventas del día"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Contenido
        content = QWidget()
        content_layout = create_page_layout("RESUMEN DE VENTAS - " + date.today().strftime("%d/%m/%Y"))
        content.setLayout(content_layout)
        
        # Widgets de resumen (sin promedio)
        self.create_summary_widgets(content_layout)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(WindowsPhoneTheme.TILE_SPACING)
        
        btn_detalle = TileButton("Ver Detalle", "fa5s.list", WindowsPhoneTheme.TILE_BLUE)
        btn_detalle.clicked.connect(self.ver_detalle_ventas)
        
        btn_imprimir = TileButton("Imprimir", "fa5s.print", WindowsPhoneTheme.TILE_GREEN)
        btn_imprimir.clicked.connect(self.imprimir_reporte)
        
        btn_cerrar = TileButton("Cerrar", "fa5s.times", WindowsPhoneTheme.TILE_RED)
        btn_cerrar.clicked.connect(self.cerrar_solicitado.emit)
        
        buttons_layout.addWidget(btn_detalle)
        buttons_layout.addWidget(btn_imprimir)
        buttons_layout.addWidget(btn_cerrar)
        
        content_layout.addLayout(buttons_layout)
        layout.addWidget(content)
        
        # Cargar datos iniciales
        self.actualizar_datos()
        
    def create_summary_widgets(self, parent_layout):
        """Crear widgets de resumen"""
        widgets_layout = QHBoxLayout()
        widgets_layout.setSpacing(WindowsPhoneTheme.TILE_SPACING)
        
        # Total vendido
        self.total_tile = InfoTile("TOTAL VENDIDO", "fa5s.dollar-sign", WindowsPhoneTheme.TILE_GREEN)
        self.total_value = self.total_tile.add_main_value("$0.00")
        widgets_layout.addWidget(self.total_tile)
        
        # Número de ventas
        self.ventas_tile = InfoTile("COMANDAS", "fa5s.shopping-cart", WindowsPhoneTheme.TILE_BLUE)
        self.ventas_count = self.ventas_tile.add_main_value("0")
        self.ventas_tile.add_secondary_value("comandas del día")
        widgets_layout.addWidget(self.ventas_tile)
        
        parent_layout.addLayout(widgets_layout)
        
    def actualizar_datos(self):
        """Actualizar datos de ventas del día"""
        try:
            # Obtener ventas del día
            ventas = self.db_manager.get_sales_by_date(date.today())
            
            # Calcular resumen
            total_vendido = sum(venta['total'] for venta in ventas)
            num_ventas = len(ventas)
            
            # Actualizar widgets
            self.total_value.setText(f"${total_vendido:.2f}")
            self.ventas_count.setText(str(num_ventas))
                
        except Exception as e:
            logging.error(f"Error actualizando datos: {e}")
            show_warning_dialog(self, "Error", f"Error al cargar datos: {e}")
    
    def ver_detalle_ventas(self):
        """Abrir ventana de detalle de ventas del día"""
        dialog = DetalleVentasDiaDialog(self.db_manager, date.today(), self)
        dialog.exec()
            
    def imprimir_reporte(self):
        """Imprimir reporte de ventas del día"""
        show_info_dialog(self, "Imprimir", "Función de impresión por implementar")


class DetalleVentasDiaDialog(QDialog):
    """Diálogo para ver el detalle de todas las ventas del día"""
    
    def __init__(self, db_manager, fecha, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.fecha = fecha
        
        self.setWindowTitle(f"Detalle de Ventas - {fecha.strftime('%d/%m/%Y')}")
        self.setMinimumSize(900, 600)
        
        self.setup_ui()
        self.cargar_ventas()
        
    def setup_ui(self):
        """Configurar interfaz del diálogo"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(WindowsPhoneTheme.MARGIN_MEDIUM,
                                 WindowsPhoneTheme.MARGIN_MEDIUM,
                                 WindowsPhoneTheme.MARGIN_MEDIUM,
                                 WindowsPhoneTheme.MARGIN_MEDIUM)
        layout.setSpacing(WindowsPhoneTheme.MARGIN_SMALL)
        
        # Título
        title = SectionTitle(f"COMANDAS DEL DÍA - {self.fecha.strftime('%d/%m/%Y')}")
        layout.addWidget(title)
        
        # Tabla de comandas
        self.tabla_ventas = QTableWidget()
        self.tabla_ventas.setColumnCount(6)
        self.tabla_ventas.setHorizontalHeaderLabels([
            "ID", "Hora", "Total", "Usuario", "Estado", "Acción"
        ])
        
        header = self.tabla_ventas.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        header.resizeSection(5, 120)
        
        layout.addWidget(self.tabla_ventas)
        
        # Botón cerrar
        btn_cerrar = TileButton("Cerrar", "fa5s.times", WindowsPhoneTheme.TILE_RED)
        btn_cerrar.setMaximumWidth(200)
        btn_cerrar.clicked.connect(self.accept)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cerrar)
        layout.addLayout(btn_layout)
        
    def cargar_ventas(self):
        """Cargar ventas del día"""
        try:
            ventas = self.db_manager.get_sales_by_date(self.fecha)
            
            self.tabla_ventas.setRowCount(len(ventas))
            
            for row, venta in enumerate(ventas):
                # ID
                self.tabla_ventas.setItem(row, 0, QTableWidgetItem(str(venta['id_venta'])))
                
                # Hora
                hora = venta['fecha_venta'].strftime("%H:%M") if isinstance(venta['fecha_venta'], datetime) else str(venta['fecha_venta'])
                self.tabla_ventas.setItem(row, 1, QTableWidgetItem(hora))
                
                # Total
                total_item = QTableWidgetItem(f"${venta['total']:.2f}")
                total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.tabla_ventas.setItem(row, 2, total_item)
                
                # Usuario
                self.tabla_ventas.setItem(row, 3, QTableWidgetItem(venta.get('usuario', 'N/A')))
                
                # Estado
                self.tabla_ventas.setItem(row, 4, QTableWidgetItem("Completada"))
                
                # Botón ver detalle
                btn_ver = QPushButton("Ver Detalle")
                btn_ver.setObjectName("tileButton")
                btn_ver.setProperty("tileColor", WindowsPhoneTheme.TILE_BLUE)
                btn_ver.clicked.connect(lambda checked, v_id=venta['id_venta']: self.ver_detalle_comanda(v_id))
                self.tabla_ventas.setCellWidget(row, 5, btn_ver)
                
        except Exception as e:
            logging.error(f"Error cargando ventas: {e}")
            show_warning_dialog(self, "Error", f"Error al cargar ventas: {e}")
            
    def ver_detalle_comanda(self, venta_id):
        """Abrir ventana con detalle de una comanda específica"""
        dialog = DetalleComandaDialog(self.db_manager, venta_id, self)
        dialog.exec()


class DetalleComandaDialog(QDialog):
    """Diálogo para ver el detalle de una comanda individual"""
    
    def __init__(self, db_manager, venta_id, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.venta_id = venta_id
        
        self.setWindowTitle(f"Detalle de Comanda #{venta_id}")
        self.setMinimumSize(700, 500)
        
        self.setup_ui()
        self.cargar_detalle()
        
    def setup_ui(self):
        """Configurar interfaz del diálogo"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(WindowsPhoneTheme.MARGIN_MEDIUM,
                                 WindowsPhoneTheme.MARGIN_MEDIUM,
                                 WindowsPhoneTheme.MARGIN_MEDIUM,
                                 WindowsPhoneTheme.MARGIN_MEDIUM)
        layout.setSpacing(WindowsPhoneTheme.MARGIN_SMALL)
        
        # Título
        self.title_label = SectionTitle(f"COMANDA #{self.venta_id}")
        layout.addWidget(self.title_label)
        
        # Panel de información de cabecera
        info_panel = ContentPanel()
        info_layout = QVBoxLayout(info_panel)
        info_layout.setContentsMargins(20, 20, 20, 20)
        info_layout.setSpacing(10)
        
        self.fecha_label = QLabel("Fecha: -")
        self.fecha_label.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL))
        
        self.usuario_label = QLabel("Usuario: -")
        self.usuario_label.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL))
        
        self.total_label = QLabel("Total: $0.00")
        self.total_label.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_LARGE, QFont.Bold))
        
        info_layout.addWidget(self.fecha_label)
        info_layout.addWidget(self.usuario_label)
        info_layout.addWidget(self.total_label)
        
        layout.addWidget(info_panel)
        
        # Tabla de productos
        productos_title = QLabel("PRODUCTOS")
        productos_title.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_SUBTITLE, QFont.Bold))
        layout.addWidget(productos_title)
        
        self.tabla_productos = QTableWidget()
        self.tabla_productos.setColumnCount(4)
        self.tabla_productos.setHorizontalHeaderLabels([
            "Producto", "Cantidad", "Precio Unit.", "Subtotal"
        ])
        
        header = self.tabla_productos.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.tabla_productos)
        
        # Botón cerrar
        btn_cerrar = TileButton("Cerrar", "fa5s.times", WindowsPhoneTheme.TILE_RED)
        btn_cerrar.setMaximumWidth(200)
        btn_cerrar.clicked.connect(self.accept)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cerrar)
        layout.addLayout(btn_layout)
        
    def cargar_detalle(self):
        """Cargar detalle de la comanda"""
        try:
            # Obtener información de la venta
            venta = self.db_manager.get_sale_by_id(self.venta_id)
            
            if not venta:
                show_warning_dialog(self, "Error", f"No se encontró la venta #{self.venta_id}")
                return
            
            # Actualizar información de cabecera
            fecha_str = venta['fecha_venta'].strftime("%d/%m/%Y %H:%M") if isinstance(venta['fecha_venta'], datetime) else str(venta['fecha_venta'])
            self.fecha_label.setText(f"Fecha: {fecha_str}")
            self.usuario_label.setText(f"Usuario: {venta.get('usuario', 'N/A')}")
            self.total_label.setText(f"Total: ${venta['total']:.2f}")
            
            # Obtener items de la venta
            items = self.db_manager.get_sale_items(self.venta_id)
            
            self.tabla_productos.setRowCount(len(items))
            
            for row, item in enumerate(items):
                # Producto
                self.tabla_productos.setItem(row, 0, QTableWidgetItem(item['nombre']))
                
                # Cantidad
                cantidad_item = QTableWidgetItem(str(item['cantidad']))
                cantidad_item.setTextAlignment(Qt.AlignCenter)
                self.tabla_productos.setItem(row, 1, cantidad_item)
                
                # Precio unitario
                precio_item = QTableWidgetItem(f"${item['precio_unitario']:.2f}")
                precio_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.tabla_productos.setItem(row, 2, precio_item)
                
                # Subtotal
                subtotal_item = QTableWidgetItem(f"${item['subtotal']:.2f}")
                subtotal_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.tabla_productos.setItem(row, 3, subtotal_item)
                
        except Exception as e:
            logging.error(f"Error cargando detalle: {e}")
            show_warning_dialog(self, "Error", f"Error al cargar detalle: {e}")
