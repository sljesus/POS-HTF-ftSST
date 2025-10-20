"""
Ventana Principal del POS HTF Gimnasio
Interfaz sencilla con pestañas en la parte inferior
Para rol: Recepcionista
Usando componentes reutilizables del sistema de diseño
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QStackedWidget, QFrame,
    QGridLayout, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QPalette, QColor
import logging

# Importar componentes del sistema de diseño
from ui.components import (
    WindowsPhoneTheme,
    TileButton,
    InfoTile,
    SectionTitle,
    TabButton,
    TopBar,
    apply_windows_phone_stylesheet,
    create_page_layout,
    create_tile_grid_layout
)


class MainPOSWindow(QMainWindow):
    """Ventana principal del sistema POS"""
    
    logout_requested = Signal()
    
    def __init__(self, user_data, db_manager, supabase_service):
        super().__init__()
        self.user_data = user_data
        self.db_manager = db_manager
        self.supabase_service = supabase_service
        
        self.setWindowTitle("HTF Gimnasio - Sistema POS")
        self.setGeometry(100, 50, 1400, 900)
        
        # Variables de estado
        self.current_tab = 0
        
        # Aplicar estilos Windows Phone
        apply_windows_phone_stylesheet(self)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar interfaz principal"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal vertical
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Barra superior con información de usuario (usando componente)
        top_bar = TopBar(
            title="HTF POS",
            user_name=self.user_data['nombre_completo'],
            user_role=self.user_data['rol']
        )
        main_layout.addWidget(top_bar)
        
        # Área de contenido (cambia según la pestaña)
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Crear las páginas de cada pestaña
        self.create_sales_page()
        self.create_inventory_page()
        self.create_members_page()
        self.create_settings_page()
        
        # Barra de navegación inferior con pestañas
        self.create_bottom_nav(main_layout)
        
        # Mostrar la primera pestaña (Ventas)
        self.stacked_widget.setCurrentIndex(0)
        
    def create_bottom_nav(self, parent_layout):
        """Crear barra de navegación inferior usando TabButton"""
        nav_bar = QFrame()
        nav_bar.setObjectName("navBar")
        nav_bar.setFixedHeight(WindowsPhoneTheme.NAV_BAR_HEIGHT)
        
        nav_layout = QHBoxLayout(nav_bar)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(0)
        
        # Definir pestañas con iconos y colores
        tabs = [
            {"name": "Ventas", "icon": "fa5s.shopping-cart", "color": WindowsPhoneTheme.TILE_RED, "index": 0},
            {"name": "Inventario", "icon": "fa5s.boxes", "color": WindowsPhoneTheme.TILE_GREEN, "index": 1},
            {"name": "Miembros", "icon": "fa5s.users", "color": WindowsPhoneTheme.TILE_ORANGE, "index": 2},
            {"name": "Configuración", "icon": "fa5s.cog", "color": WindowsPhoneTheme.TILE_PURPLE, "index": 3},
        ]
        
        # Crear botones usando componente TabButton
        self.tab_buttons = []
        for tab in tabs:
            btn = TabButton(tab['name'], tab['icon'], tab['color'])
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.clicked.connect(lambda checked, idx=tab['index']: self.switch_tab(idx))
            nav_layout.addWidget(btn)
            self.tab_buttons.append(btn)
        
        # Activar primera pestaña
        self.tab_buttons[0].setChecked(True)
        
        parent_layout.addWidget(nav_bar)
        
    def switch_tab(self, index):
        """Cambiar de pestaña"""
        self.current_tab = index
        self.stacked_widget.setCurrentIndex(index)
        
        # Actualizar estado visual de botones
        for i, btn in enumerate(self.tab_buttons):
            btn.setChecked(i == index)
            
        logging.info(f"Cambio a pestaña: {index}")
        
    # ========== PÁGINAS DE CONTENIDO ==========
    
    def create_sales_page(self):
        """Página de ventas usando TileButton"""
        page = QWidget()
        layout = create_page_layout("PUNTO DE VENTA")
        page.setLayout(layout)
        
        # Grid de tiles
        grid = create_tile_grid_layout()
        
        # Botones de acciones usando componente TileButton
        actions = [
            {"text": "Nueva Venta", "icon": "fa5s.cash-register", "color": WindowsPhoneTheme.TILE_RED},
            {"text": "Ventas del Día", "icon": "fa5s.list-alt", "color": WindowsPhoneTheme.TILE_ORANGE},
            {"text": "Cobrar Membresía", "icon": "fa5s.id-card", "color": WindowsPhoneTheme.TILE_BLUE},
            {"text": "Venta Rápida", "icon": "fa5s.bolt", "color": WindowsPhoneTheme.TILE_TEAL},
            {"text": "Historial", "icon": "fa5s.history", "color": WindowsPhoneTheme.TILE_PURPLE},
            {"text": "Cierre de Caja", "icon": "fa5s.lock", "color": WindowsPhoneTheme.TILE_MAGENTA},
        ]
        
        for i, action in enumerate(actions):
            btn = TileButton(action["text"], action["icon"], action["color"])
            row = i // 3
            col = i % 3
            grid.addWidget(btn, row, col)
        
        layout.addLayout(grid)
        layout.addStretch()
        
        self.stacked_widget.addWidget(page)
        
    def create_inventory_page(self):
        """Página de inventario usando TileButton"""
        page = QWidget()
        layout = create_page_layout("MOVIMIENTOS DE INVENTARIO")
        page.setLayout(layout)
        
        # Grid de tiles
        grid = create_tile_grid_layout()
        
        actions = [
            {"text": "Registrar Entrada", "icon": "fa5s.plus-circle", "color": WindowsPhoneTheme.TILE_GREEN},
            {"text": "Registrar Salida", "icon": "fa5s.minus-circle", "color": WindowsPhoneTheme.TILE_RED},
            {"text": "Ver Inventario", "icon": "fa5s.warehouse", "color": WindowsPhoneTheme.TILE_BLUE},
            {"text": "Buscar Producto", "icon": "fa5s.search", "color": WindowsPhoneTheme.TILE_ORANGE},
            {"text": "Bajo Stock", "icon": "fa5s.exclamation-triangle", "color": WindowsPhoneTheme.TILE_MAGENTA},
            {"text": "Reporte", "icon": "fa5s.chart-line", "color": WindowsPhoneTheme.TILE_PURPLE},
        ]
        
        for i, action in enumerate(actions):
            btn = TileButton(action["text"], action["icon"], action["color"])
            row = i // 3
            col = i % 3
            grid.addWidget(btn, row, col)
        
        layout.addLayout(grid)
        layout.addStretch()
        
        self.stacked_widget.addWidget(page)
        
    def create_members_page(self):
        """Página de miembros usando InfoTile"""
        page = QWidget()
        layout = create_page_layout("MIEMBROS Y LOCKERS")
        page.setLayout(layout)
        
        # Widgets informativos
        widgets_layout = QHBoxLayout()
        widgets_layout.setSpacing(WindowsPhoneTheme.TILE_SPACING)
        
        # Widget de miembros usando InfoTile
        members_tile = InfoTile("MIEMBROS", "fa5s.users", WindowsPhoneTheme.TILE_TEAL)
        try:
            total_members = self.db_manager.get_total_members()
            active_today = self.db_manager.get_active_members_today()
        except:
            total_members = 0
            active_today = 0
        
        members_tile.add_main_value(total_members)
        members_tile.add_secondary_value(f"Activos Hoy: {active_today}")
        members_tile.add_stretch()
        widgets_layout.addWidget(members_tile)
        
        # Widget de lockers usando InfoTile
        lockers_tile = InfoTile("LOCKERS", "fa5s.key", WindowsPhoneTheme.TILE_MAGENTA)
        total_lockers = 50
        occupied_lockers = 12
        available_lockers = total_lockers - occupied_lockers
        lockers_tile.add_main_value(available_lockers)
        lockers_tile.add_secondary_value(f"Ocupados: {occupied_lockers}/{total_lockers}")
        lockers_tile.add_stretch()
        widgets_layout.addWidget(lockers_tile)
        
        layout.addLayout(widgets_layout)
        
        # Botones de acción
        actions_grid = create_tile_grid_layout()
        
        btn_search = TileButton("Buscar Miembro", "fa5s.search", WindowsPhoneTheme.TILE_ORANGE)
        btn_register = TileButton("Registrar Entrada", "fa5s.sign-in-alt", WindowsPhoneTheme.TILE_GREEN)
        btn_lockers = TileButton("Gestionar Lockers", "fa5s.key", WindowsPhoneTheme.TILE_BLUE)
        
        actions_grid.addWidget(btn_search, 0, 0)
        actions_grid.addWidget(btn_register, 0, 1)
        actions_grid.addWidget(btn_lockers, 0, 2)
        
        layout.addLayout(actions_grid)
        layout.addStretch()
        
        self.stacked_widget.addWidget(page)
        
    def create_settings_page(self):
        """Página de configuración usando TileButton"""
        page = QWidget()
        layout = create_page_layout("CONFIGURACIÓN")
        page.setLayout(layout)
        
        # Grid de configuración
        config_grid = create_tile_grid_layout()
        
        btn_change_password = TileButton("Cambiar Contraseña", "fa5s.lock", WindowsPhoneTheme.TILE_ORANGE)
        btn_sync = TileButton("Sincronizar", "fa5s.sync", WindowsPhoneTheme.TILE_BLUE)
        btn_backup = TileButton("Respaldar Datos", "fa5s.database", WindowsPhoneTheme.TILE_TEAL)
        btn_logout = TileButton("Cerrar Sesión", "fa5s.sign-out-alt", WindowsPhoneTheme.TILE_RED)
        btn_logout.clicked.connect(self.handle_logout)
        
        config_grid.addWidget(btn_change_password, 0, 0)
        config_grid.addWidget(btn_sync, 0, 1)
        config_grid.addWidget(btn_backup, 1, 0)
        config_grid.addWidget(btn_logout, 1, 1)
        
        layout.addLayout(config_grid)
        layout.addStretch()
        
        self.stacked_widget.addWidget(page)
        
    def handle_logout(self):
        """Manejar cierre de sesión"""
        logging.info(f"Usuario {self.user_data['username']} cerró sesión")
        self.logout_requested.emit()
        self.close()

