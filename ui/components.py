"""
Componentes UI reutilizables - Estilo Windows Phone
Sistema de diseño unificado para toda la aplicación HTF POS
"""

from PySide6.QtWidgets import (
    QPushButton, QLabel, QFrame, QVBoxLayout, QHBoxLayout, QWidget, QDialog
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QCursor
import qtawesome as qta


class WindowsPhoneTheme:
    """Paleta de colores y configuración del tema Windows Phone"""
    
    # Colores principales
    PRIMARY_BLUE = "#1e3a8a"  # Azul HTF (app principal)
    
    # Colores de tiles vibrantes
    TILE_RED = "#e51400"
    TILE_GREEN = "#00a300"
    TILE_ORANGE = "#ff8c00"
    TILE_PURPLE = "#9b59b6"
    TILE_BLUE = "#0078d7"
    TILE_TEAL = "#00aba9"
    TILE_MAGENTA = "#e3008c"
    
    # Colores de fondo
    BG_BLACK = "#000000"
    BG_LIGHT = "#f5f5f5"
    
    # Fuente
    FONT_FAMILY = "Segoe UI"
    
    # Tamaños de fuente
    FONT_SIZE_TITLE = 20
    FONT_SIZE_SUBTITLE = 16
    FONT_SIZE_NORMAL = 13
    FONT_SIZE_SMALL = 11
    FONT_SIZE_LARGE = 18
    FONT_SIZE_XLARGE = 36
    
    # Tamaños de iconos
    ICON_SIZE_SMALL = 48
    ICON_SIZE_MEDIUM = 56
    ICON_SIZE_LARGE = 64
    ICON_SIZE_XLARGE = 80
    
    # Dimensiones de tiles
    TILE_MIN_HEIGHT = 160
    TILE_MIN_WIDTH = 200
    TILE_SPACING = 8
    
    # Alturas de barras
    TOP_BAR_HEIGHT = 70
    NAV_BAR_HEIGHT = 140
    
    # Márgenes estándar
    MARGIN_SMALL = 10
    MARGIN_MEDIUM = 20
    MARGIN_LARGE = 30


class TileButton(QPushButton):
    """Botón grande estilo Windows Phone Tile"""
    
    def __init__(self, text, icon_name=None, color=WindowsPhoneTheme.TILE_BLUE, parent=None):
        super().__init__(parent)
        
        self.setMinimumHeight(WindowsPhoneTheme.TILE_MIN_HEIGHT)
        self.setMinimumWidth(WindowsPhoneTheme.TILE_MIN_WIDTH)
        self.setObjectName("tileButton")
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setProperty("tileColor", color)
        
        # Layout vertical para icono + texto
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 25, 20, 25)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignCenter)
        
        # Icono grande si se proporciona
        if icon_name:
            icon_label = QLabel()
            icon_label.setAlignment(Qt.AlignCenter)
            try:
                icon_label.setPixmap(
                    qta.icon(icon_name, color='white').pixmap(
                        QSize(WindowsPhoneTheme.ICON_SIZE_LARGE, WindowsPhoneTheme.ICON_SIZE_LARGE)
                    )
                )
            except Exception as e:
                # Fallback: usar emoji si qtawesome falla
                icon_label.setText("⚙")
                icon_label.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, 48))
                icon_label.setStyleSheet("color: white;")
            icon_label.setObjectName("tileIcon")
            layout.addWidget(icon_label)
        
        # Texto debajo
        text_label = QLabel(text)
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL, QFont.Bold))
        text_label.setWordWrap(True)
        text_label.setObjectName("tileText")
        text_label.setStyleSheet("color: white;")
        layout.addWidget(text_label)


class InfoTile(QFrame):
    """Tile informativo estilo Windows Phone con icono, título y datos"""
    
    def __init__(self, title, icon_name=None, color=WindowsPhoneTheme.TILE_BLUE, parent=None):
        super().__init__(parent)
        
        self.setObjectName("infoTile")
        self.setProperty("tileColor", color)
        self.setMinimumHeight(180)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(25, 30, 25, 30)
        self.main_layout.setSpacing(18)
        self.main_layout.setAlignment(Qt.AlignCenter)
        
        # Icono grande (opcional)
        if icon_name:
            self.icon_label = QLabel()
            self.icon_label.setAlignment(Qt.AlignCenter)
            try:
                self.icon_label.setPixmap(
                    qta.icon(icon_name, color='white').pixmap(
                        QSize(WindowsPhoneTheme.ICON_SIZE_LARGE, WindowsPhoneTheme.ICON_SIZE_LARGE)
                    )
                )
            except:
                # Si falla el icono, mostrar emoji
                self.icon_label.setText("💰")
                self.icon_label.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, 48))
                self.icon_label.setStyleSheet("color: white;")
            self.main_layout.addWidget(self.icon_label, 0, Qt.AlignCenter)
        
        # Título del tile
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_SUBTITLE, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("color: white;")
        self.main_layout.addWidget(self.title_label, 0, Qt.AlignCenter)
    
    def add_main_value(self, value):
        """Agregar valor principal grande"""
        value_label = QLabel(str(value))
        value_label.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_XLARGE, QFont.Bold))
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet("color: white;")
        self.main_layout.addWidget(value_label, 0, Qt.AlignCenter)
        return value_label
    
    def add_secondary_value(self, text):
        """Agregar valor secundario pequeño"""
        secondary_label = QLabel(text)
        secondary_label.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL))
        secondary_label.setAlignment(Qt.AlignCenter)
        secondary_label.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
        self.main_layout.addWidget(secondary_label, 0, Qt.AlignCenter)
        return secondary_label
    
    def add_stretch(self):
        """Agregar espacio flexible al final"""
        self.main_layout.addStretch()


class SectionTitle(QLabel):
    """Título de sección estilo Windows Phone"""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        
        self.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_TITLE, QFont.Bold))
        self.setObjectName("sectionTitle")


class TabButton(QPushButton):
    """Botón de navegación para pestañas inferiores"""
    
    def __init__(self, name, icon_name, color, parent=None):
        super().__init__(parent)
        
        self.setCheckable(True)
        self.setObjectName("tabButton")
        self.setProperty("tileColor", color)
        
        # Layout vertical para icono + texto
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 15, 10, 15)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignCenter)
        
        # Icono
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setPixmap(
            qta.icon(icon_name, color='white').pixmap(
                QSize(WindowsPhoneTheme.ICON_SIZE_SMALL, WindowsPhoneTheme.ICON_SIZE_SMALL)
            )
        )
        icon_label.setObjectName("tabIcon")
        layout.addWidget(icon_label)
        
        # Texto
        text_label = QLabel(name)
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_SMALL, QFont.Bold))
        text_label.setObjectName("tabText")
        text_label.setStyleSheet("color: white;")
        layout.addWidget(text_label)


class TopBar(QFrame):
    """Barra superior con título y información de usuario"""
    
    def __init__(self, title, user_name, user_role, parent=None):
        super().__init__(parent)
        
        self.setObjectName("topBar")
        self.setFixedHeight(WindowsPhoneTheme.TOP_BAR_HEIGHT)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(WindowsPhoneTheme.MARGIN_LARGE, WindowsPhoneTheme.MARGIN_SMALL, 
                                 WindowsPhoneTheme.MARGIN_LARGE, WindowsPhoneTheme.MARGIN_SMALL)
        
        # Título
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_LARGE, QFont.Bold))
        self.title_label.setObjectName("titleLabel")
        layout.addWidget(self.title_label)
        
        layout.addStretch()
        
        # Información de usuario
        user_info = QLabel(f"👤 {user_name} | {user_role}")
        user_info.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_SMALL))
        user_info.setObjectName("userInfo")
        layout.addWidget(user_info)
        
    def set_title(self, new_title):
        """Actualizar el título de la barra superior"""
        self.title_label.setText(new_title)


class StyledLabel(QLabel):
    """Label con estilo Windows Phone consistente"""
    
    def __init__(self, text="", bold=False, size=WindowsPhoneTheme.FONT_SIZE_NORMAL, parent=None):
        super().__init__(text, parent)
        
        weight = QFont.Bold if bold else QFont.Normal
        self.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, size, weight))
        self.setObjectName("styledLabel")


class ContentPanel(QFrame):
    """Panel de contenido con estilo Windows Phone"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setObjectName("contentPanel")
        self.setFrameShape(QFrame.NoFrame)


class SearchBar(QWidget):
    """Barra de búsqueda estilo Windows Phone con icono"""
    
    def __init__(self, placeholder="Buscar...", parent=None):
        super().__init__(parent)
        
        from PySide6.QtWidgets import QLineEdit
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Input de búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(placeholder)
        self.search_input.setMinimumHeight(45)
        layout.addWidget(self.search_input)
        
        # Botón de búsqueda con icono Font Awesome
        self.search_button = QPushButton(" Buscar")
        self.search_button.setObjectName("tileButton")
        self.search_button.setProperty("tileColor", WindowsPhoneTheme.TILE_BLUE)
        self.search_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.search_button.setMinimumWidth(120)
        self.search_button.setMaximumWidth(120)
        self.search_button.setMinimumHeight(45)
        self.search_button.setMaximumHeight(45)
        self.search_button.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, 11, QFont.Bold))
        self.search_button.setStyleSheet("color: white;")
        
        # Icono Font Awesome
        try:
            self.search_button.setIcon(qta.icon('fa5s.search', color='white'))
            self.search_button.setIconSize(QSize(16, 16))
        except:
            pass  # Si falla, solo mostrar texto
        
        layout.addWidget(self.search_button)
    
    def text(self):
        """Obtener texto del input"""
        return self.search_input.text()
    
    def connect_search(self, slot):
        """Conectar señal de búsqueda"""
        self.search_input.textChanged.connect(slot)
        self.search_button.clicked.connect(slot)


def apply_windows_phone_stylesheet(widget):
    """
    Aplicar la hoja de estilos Windows Phone a cualquier widget
    Debe llamarse desde la ventana principal o widget raíz
    """
    theme = WindowsPhoneTheme
    
    stylesheet = f"""
        QMainWindow {{
            background-color: {theme.BG_BLACK};
        }}
        
        /* Barra superior */
        #topBar {{
            background: {theme.PRIMARY_BLUE};
            border: none;
        }}
        
        #titleLabel {{
            color: white;
            font-family: '{theme.FONT_FAMILY}';
            font-weight: bold;
            background: transparent;
        }}
        
        #userInfo {{
            color: white;
            background-color: rgba(255, 255, 255, 0.15);
            padding: 8px 20px;
            border-radius: 0px;
            font-family: '{theme.FONT_FAMILY}';
        }}
        
        /* Títulos de sección */
        #sectionTitle {{
            color: {theme.PRIMARY_BLUE};
            padding: 10px 0px;
            border: none;
            font-family: '{theme.FONT_FAMILY}';
            font-weight: bold;
        }}
        
        /* Barra de navegación inferior */
        #navBar {{
            background-color: {theme.BG_BLACK};
            border: none;
        }}
        
        /* Botones de pestaña */
        QPushButton#tabButton {{
            background-color: palette(button);
            border: none;
            border-radius: 0px;
        }}
        
        QPushButton#tabButton[tileColor="{theme.TILE_RED}"] {{
            background-color: {theme.TILE_RED};
        }}
        
        QPushButton#tabButton[tileColor="{theme.TILE_GREEN}"] {{
            background-color: {theme.TILE_GREEN};
        }}
        
        QPushButton#tabButton[tileColor="{theme.TILE_ORANGE}"] {{
            background-color: {theme.TILE_ORANGE};
        }}
        
        QPushButton#tabButton[tileColor="{theme.TILE_PURPLE}"] {{
            background-color: {theme.TILE_PURPLE};
        }}
        
        QPushButton#tabButton:hover {{
            opacity: 0.9;
        }}
        
        QPushButton#tabButton:checked {{
            border-bottom: 6px solid white;
        }}
        
        #tabIcon, #tabText {{
            background: transparent;
        }}
        
        /* Botones Tile */
        QPushButton#tileButton {{
            background-color: palette(button);
            border: none;
            border-radius: 0px;
        }}
        
        QPushButton#tileButton[tileColor="{theme.TILE_RED}"] {{
            background-color: {theme.TILE_RED};
        }}
        
        QPushButton#tileButton[tileColor="{theme.TILE_GREEN}"] {{
            background-color: {theme.TILE_GREEN};
        }}
        
        QPushButton#tileButton[tileColor="{theme.TILE_ORANGE}"] {{
            background-color: {theme.TILE_ORANGE};
        }}
        
        QPushButton#tileButton[tileColor="{theme.TILE_PURPLE}"] {{
            background-color: {theme.TILE_PURPLE};
        }}
        
        QPushButton#tileButton[tileColor="{theme.TILE_BLUE}"] {{
            background-color: {theme.TILE_BLUE};
        }}
        
        QPushButton#tileButton[tileColor="{theme.TILE_TEAL}"] {{
            background-color: {theme.TILE_TEAL};
        }}
        
        QPushButton#tileButton[tileColor="{theme.TILE_MAGENTA}"] {{
            background-color: {theme.TILE_MAGENTA};
        }}
        
        QPushButton#tileButton:hover {{
            opacity: 0.85;
        }}
        
        QPushButton#tileButton:pressed {{
            opacity: 0.7;
        }}
        
        #tileIcon, #tileText {{
            background: transparent;
        }}
        
        /* Tiles de información */
        QFrame#infoTile {{
            background-color: palette(button);
            border: none;
            border-radius: 0px;
        }}
        
        QFrame#infoTile[tileColor="{theme.TILE_RED}"] {{
            background-color: {theme.TILE_RED};
        }}
        
        QFrame#infoTile[tileColor="{theme.TILE_GREEN}"] {{
            background-color: {theme.TILE_GREEN};
        }}
        
        QFrame#infoTile[tileColor="{theme.TILE_ORANGE}"] {{
            background-color: {theme.TILE_ORANGE};
        }}
        
        QFrame#infoTile[tileColor="{theme.TILE_PURPLE}"] {{
            background-color: {theme.TILE_PURPLE};
        }}
        
        QFrame#infoTile[tileColor="{theme.TILE_BLUE}"] {{
            background-color: {theme.TILE_BLUE};
        }}
        
        QFrame#infoTile[tileColor="{theme.TILE_TEAL}"] {{
            background-color: {theme.TILE_TEAL};
        }}
        
        QFrame#infoTile[tileColor="{theme.TILE_MAGENTA}"] {{
            background-color: {theme.TILE_MAGENTA};
        }}
        
        QFrame#infoTile[tileColor="{theme.PRIMARY_BLUE}"] {{
            background-color: {theme.PRIMARY_BLUE};
        }}
        
        QFrame#infoTile QLabel {{
            font-family: '{theme.FONT_FAMILY}';
            background: transparent;
        }}
        
        /* Área de contenido */
        QWidget {{
            background-color: {theme.BG_LIGHT};
        }}
        
        /* Panels de contenido */
        QFrame#contentPanel {{
            background-color: white;
            border: none;
            border-radius: 0px;
        }}
        
        /* Labels estilizados */
        QLabel#styledLabel {{
            color: #333333;
            background: transparent;
        }}
        
        /* Diálogos y ventanas emergentes */
        #alertDialog {{
            background-color: white;
            border: 4px solid rgba(15, 23, 42, 0.15);
        }}

        #dialogHeader {{
            background-color: {theme.PRIMARY_BLUE};
        }}

        #dialogTitle {{
            color: white;
            font-family: '{theme.FONT_FAMILY}';
            font-weight: bold;
            background: transparent;
        }}

        #dialogMessage {{
            color: #1f2937;
            background: transparent;
            font-family: '{theme.FONT_FAMILY}';
        }}

        #dialogDetail {{
            color: #374151;
            background: transparent;
            font-family: '{theme.FONT_FAMILY}';
            font-size: {theme.FONT_SIZE_SMALL}px;
            border-left: 4px solid rgba(30, 58, 138, 0.25);
            padding-left: 12px;
        }}

        #dialogPrimaryButton {{
            background-color: {theme.PRIMARY_BLUE};
            color: white;
            border: none;
            border-radius: 0px;
            padding: 12px 28px;
            font-family: '{theme.FONT_FAMILY}';
            font-weight: bold;
        }}

        #dialogPrimaryButton:hover {{
            opacity: 0.88;
        }}

        #dialogPrimaryButton:pressed {{
            opacity: 0.78;
        }}

        #dialogSecondaryButton {{
            background-color: transparent;
            color: {theme.PRIMARY_BLUE};
            border: 3px solid rgba(30, 58, 138, 0.35);
            border-radius: 0px;
            padding: 11px 26px;
            font-family: '{theme.FONT_FAMILY}';
            font-weight: bold;
        }}

        #dialogSecondaryButton:hover {{
            background-color: rgba(30, 58, 138, 0.08);
        }}

        QDialog {{
            background-color: {theme.BG_LIGHT};
        }}
        
        /* Labels generales */
        QLabel {{
            font-family: '{theme.FONT_FAMILY}';
        }}
        
        /* Inputs y campos de texto */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: white;
            border: 2px solid #cccccc;
            border-radius: 0px;
            padding: 8px;
            font-family: '{theme.FONT_FAMILY}';
            font-size: {theme.FONT_SIZE_NORMAL}px;
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border: 2px solid {theme.PRIMARY_BLUE};
        }}
        
        /* ComboBox */
        QComboBox {{
            background-color: white;
            border: 2px solid #cccccc;
            border-radius: 0px;
            padding: 8px;
            font-family: '{theme.FONT_FAMILY}';
            font-size: {theme.FONT_SIZE_NORMAL}px;
        }}
        
        QComboBox:focus {{
            border: 2px solid {theme.PRIMARY_BLUE};
        }}
        
        /* Tablas */
        QTableWidget {{
            background-color: white;
            border: none;
            gridline-color: #e0e0e0;
            font-family: '{theme.FONT_FAMILY}';
        }}
        
        QTableWidget::item {{
            padding: 8px;
        }}
        
        QTableWidget::item:selected {{
            background-color: {theme.PRIMARY_BLUE};
            color: white;
        }}
        
        QHeaderView::section {{
            background-color: {theme.PRIMARY_BLUE};
            color: white;
            padding: 8px;
            border: none;
            font-weight: bold;
            font-family: '{theme.FONT_FAMILY}';
        }}
        
        /* ScrollBars */
        QScrollBar:vertical {{
            background: #f0f0f0;
            width: 12px;
            border-radius: 0px;
        }}
        
        QScrollBar::handle:vertical {{
            background: {theme.PRIMARY_BLUE};
            border-radius: 0px;
            min-height: 30px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: {theme.TILE_BLUE};
        }}
        
        QScrollBar:horizontal {{
            background: #f0f0f0;
            height: 12px;
            border-radius: 0px;
        }}
        
        QScrollBar::handle:horizontal {{
            background: {theme.PRIMARY_BLUE};
            border-radius: 0px;
            min-width: 30px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background: {theme.TILE_BLUE};
        }}
    """
    
    widget.setStyleSheet(stylesheet)


# Funciones helper para crear layouts estándar

def create_page_layout(title_text):
    """Crear layout estándar de página con título"""
    layout = QVBoxLayout()
    layout.setContentsMargins(WindowsPhoneTheme.MARGIN_MEDIUM, WindowsPhoneTheme.MARGIN_MEDIUM, 
                             WindowsPhoneTheme.MARGIN_MEDIUM, WindowsPhoneTheme.MARGIN_MEDIUM)
    layout.setSpacing(15)
    
    # Título
    title = SectionTitle(title_text)
    layout.addWidget(title)
    
    return layout


def create_tile_grid_layout():
    """Crear layout de grid para tiles"""
    from PySide6.QtWidgets import QGridLayout
    
    grid = QGridLayout()
    grid.setSpacing(WindowsPhoneTheme.TILE_SPACING)
    grid.setContentsMargins(0, WindowsPhoneTheme.MARGIN_SMALL, 0, 0)
    
    return grid


class AlertDialog(QDialog):
    """Diálogo de alerta personalizado con estética Windows Phone"""

    ICON_MAP = {
        "info": ("fa5s.info-circle", WindowsPhoneTheme.TILE_BLUE),
        "success": ("fa5s.check-circle", WindowsPhoneTheme.TILE_GREEN),
        "warning": ("fa5s.exclamation-triangle", WindowsPhoneTheme.TILE_ORANGE),
        "error": ("fa5s.times-circle", WindowsPhoneTheme.TILE_RED),
        "question": ("fa5s.question-circle", WindowsPhoneTheme.TILE_BLUE),
    }

    def __init__(
        self,
        title,
        message,
        dialog_type="info",
        parent=None,
        detail=None,
        primary_text="Aceptar",
        secondary_text=None
    ):
        super().__init__(parent)
        self.setObjectName("alertDialog")
        self.setModal(True)
        self.setWindowTitle(title)
        self.setMinimumWidth(420)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self._dialog_type = dialog_type

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        header_frame = QFrame()
        header_frame.setObjectName("dialogHeader")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(28, 24, 28, 24)
        header_layout.setSpacing(18)

        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(60, 60)

        icon_name, color = self.ICON_MAP.get(dialog_type, self.ICON_MAP["info"])
        try:
            icon_label.setPixmap(
                qta.icon(icon_name, color="white").pixmap(QSize(48, 48))
            )
        except Exception:
            icon_label.setText("⚠")
            icon_label.setStyleSheet("color: white; font-size: 42px;")

        header_layout.addWidget(icon_label, 0, Qt.AlignCenter)

        title_label = QLabel(title.upper())
        title_label.setObjectName("dialogTitle")
        title_label.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_LARGE, QFont.Bold))
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        root_layout.addWidget(header_frame)

        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(32, 28, 32, 28)
        content_layout.setSpacing(16)

        message_label = QLabel(message)
        message_label.setObjectName("dialogMessage")
        message_label.setWordWrap(True)
        message_label.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL))
        content_layout.addWidget(message_label)

        if detail:
            detail_label = QLabel(detail)
            detail_label.setObjectName("dialogDetail")
            detail_label.setWordWrap(True)
            content_layout.addWidget(detail_label)

        content_layout.addStretch()

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(14)
        buttons_layout.addStretch()

        if secondary_text:
            secondary_button = QPushButton(secondary_text)
            secondary_button.setObjectName("dialogSecondaryButton")
            secondary_button.clicked.connect(self.reject)
            buttons_layout.addWidget(secondary_button)
        else:
            secondary_button = None

        primary_button = QPushButton(primary_text)
        primary_button.setObjectName("dialogPrimaryButton")
        primary_button.clicked.connect(self.accept)
        buttons_layout.addWidget(primary_button)

        content_layout.addLayout(buttons_layout)
        root_layout.addWidget(content_frame)

        self._primary_button = primary_button
        self._secondary_button = secondary_button
        self._header_frame = header_frame

        self._apply_type_styles(dialog_type, color)

    def _apply_type_styles(self, dialog_type, color):
        """Aplicar color de acento según el tipo de diálogo"""
        accent_color = color
        self._primary_button.setStyleSheet(
            f"background-color: {accent_color}; color: white;"
        )
        if self._secondary_button:
            self._secondary_button.setStyleSheet(
                f"color: {accent_color}; border-color: rgba(30, 58, 138, 0.35);"
            )
        self._header_frame.setStyleSheet(f"background-color: {accent_color};")

    @classmethod
    def show_info(cls, parent, title, message, detail=None, button_text="Entendido"):
        cls(title, message, "info", parent, detail, button_text).exec()

    @classmethod
    def show_success(cls, parent, title, message, detail=None, button_text="Perfecto"):
        cls(title, message, "success", parent, detail, button_text).exec()

    @classmethod
    def show_warning(cls, parent, title, message, detail=None, button_text="Revisar"):
        cls(title, message, "warning", parent, detail, button_text).exec()

    @classmethod
    def show_error(cls, parent, title, message, detail=None, button_text="Cerrar"):
        cls(title, message, "error", parent, detail, button_text).exec()

    @classmethod
    def ask_confirmation(
        cls,
        parent,
        title,
        message,
        detail=None,
        confirm_text="Sí",
        cancel_text="No"
    ):
        dialog = cls(
            title,
            message,
            "question",
            parent,
            detail,
            confirm_text,
            cancel_text
        )
        return dialog.exec() == QDialog.Accepted


def show_info_dialog(parent, title, message, detail=None, button_text="Entendido"):
    AlertDialog.show_info(parent, title, message, detail, button_text)


def show_success_dialog(parent, title, message, detail=None, button_text="Perfecto"):
    AlertDialog.show_success(parent, title, message, detail, button_text)


def show_warning_dialog(parent, title, message, detail=None, button_text="Revisar"):
    AlertDialog.show_warning(parent, title, message, detail, button_text)


def show_error_dialog(parent, title, message, detail=None, button_text="Cerrar"):
    AlertDialog.show_error(parent, title, message, detail, button_text)


def show_confirmation_dialog(
    parent,
    title,
    message,
    detail=None,
    confirm_text="Sí",
    cancel_text="No"
):
    return AlertDialog.ask_confirmation(
        parent,
        title,
        message,
        detail,
        confirm_text,
        cancel_text
    )


def show_input_dialog(parent, title, message, placeholder=""):
    """Mostrar diálogo para solicitar entrada de texto"""
    from PySide6.QtWidgets import QInputDialog
    
    text, ok = QInputDialog.getText(
        parent,
        title,
        message,
        text=placeholder
    )
    
    return text, ok
