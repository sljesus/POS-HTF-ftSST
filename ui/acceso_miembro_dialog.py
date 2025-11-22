"""
Diálogo de Acceso de Miembro para HTF POS
Muestra información del miembro con foto al registrar entrada
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QWidget
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QPixmap, QPainter, QPainterPath, QColor
import logging
from datetime import datetime
import os

from ui.components import (
    WindowsPhoneTheme,
    TileButton
)


class AccesoMiembroDialog(QDialog):
    """Diálogo para mostrar información del miembro al registrar acceso"""
    
    acceso_confirmado = Signal(dict)  # Emite los datos del miembro cuando se confirma
    
    def __init__(self, miembro_data, parent=None):
        super().__init__(parent)
        self.miembro_data = miembro_data
        self.setWindowTitle("Acceso al Gimnasio")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        self.setup_ui()
        self.aplicar_estilos()
    
    def setup_ui(self):
        """Configurar interfaz del diálogo"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # ===== ENCABEZADO =====
        header = QFrame()
        header.setObjectName("dialogHeader")
        header.setMinimumHeight(80)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(30, 20, 30, 20)
        
        title = QLabel("¡BIENVENIDO!")
        title.setObjectName("dialogTitle")
        title.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title)
        
        hora = QLabel(datetime.now().strftime("%d/%m/%Y - %H:%M:%S"))
        hora.setStyleSheet(f"color: white; font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;")
        hora.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(hora)
        
        layout.addWidget(header)
        
        # ===== CONTENIDO PRINCIPAL =====
        content = QWidget()
        content.setObjectName("dialogContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(40, 30, 40, 30)
        content_layout.setSpacing(25)
        
        # ===== FOTO DEL MIEMBRO =====
        foto_container = QHBoxLayout()
        foto_container.setAlignment(Qt.AlignCenter)
        
        self.foto_label = QLabel()
        self.foto_label.setFixedSize(200, 200)
        self.foto_label.setAlignment(Qt.AlignCenter)
        self.foto_label.setObjectName("fotoMiembro")
        
        # Cargar foto del miembro o usar placeholder
        self.cargar_foto()
        
        foto_container.addWidget(self.foto_label)
        content_layout.addLayout(foto_container)
        
        # ===== DATOS DEL MIEMBRO =====
        datos_container = QFrame()
        datos_container.setObjectName("datosContainer")
        datos_layout = QVBoxLayout(datos_container)
        datos_layout.setContentsMargins(20, 20, 20, 20)
        datos_layout.setSpacing(15)
        
        # Nombre completo
        nombre_completo = f"{self.miembro_data['nombres']} {self.miembro_data['apellido_paterno']} {self.miembro_data['apellido_materno']}"
        nombre_label = QLabel(nombre_completo.upper())
        nombre_label.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, 20, QFont.Bold))
        nombre_label.setAlignment(Qt.AlignCenter)
        nombre_label.setStyleSheet(f"color: {WindowsPhoneTheme.PRIMARY_BLUE};")
        datos_layout.addWidget(nombre_label)
        
        # Línea divisoria
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #e5e7eb; max-height: 1px;")
        datos_layout.addWidget(line)
        
        # Información adicional en grid
        info_layout = QVBoxLayout()
        info_layout.setSpacing(12)
        
        # ID Miembro
        self.agregar_info_row(info_layout, "ID Miembro:", f"#{self.miembro_data['id_miembro']}")
        
        # Fecha de registro
        fecha_registro = self.miembro_data.get('fecha_registro', 'N/A')
        self.agregar_info_row(info_layout, "Miembro desde:", fecha_registro)
        
        # Teléfono
        telefono = self.miembro_data.get('telefono', 'No registrado')
        self.agregar_info_row(info_layout, "Teléfono:", telefono)
        
        # Email
        email = self.miembro_data.get('email', 'No registrado')
        self.agregar_info_row(info_layout, "Email:", email)
        
        # Estado
        estado = "ACTIVO" if self.miembro_data.get('activo', False) else "INACTIVO"
        estado_color = WindowsPhoneTheme.TILE_GREEN if self.miembro_data.get('activo', False) else WindowsPhoneTheme.TILE_RED
        self.agregar_info_row(info_layout, "Estado:", estado, estado_color)
        
        datos_layout.addLayout(info_layout)
        content_layout.addWidget(datos_container)
        
        # Espaciador
        content_layout.addStretch()
        
        layout.addWidget(content)
        
        # ===== BOTONES DE ACCIÓN =====
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(40, 20, 40, 30)
        buttons_layout.setSpacing(20)
        
        # Verificar si el miembro está activo
        if self.miembro_data.get('activo', False):
            btn_confirmar = TileButton(
                "REGISTRAR ENTRADA",
                "fa5s.check-circle",
                WindowsPhoneTheme.TILE_GREEN
            )
            btn_confirmar.setMinimumHeight(100)
            btn_confirmar.clicked.connect(self.confirmar_acceso)
            buttons_layout.addWidget(btn_confirmar, 2)
        else:
            # Mostrar mensaje de miembro inactivo
            mensaje_inactivo = QLabel("⚠️ MIEMBRO INACTIVO - Contactar recepción")
            mensaje_inactivo.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, 14, QFont.Bold))
            mensaje_inactivo.setStyleSheet(f"color: {WindowsPhoneTheme.TILE_RED}; padding: 15px;")
            mensaje_inactivo.setAlignment(Qt.AlignCenter)
            buttons_layout.addWidget(mensaje_inactivo, 2)
        
        btn_cancelar = TileButton(
            "CANCELAR",
            "fa5s.times-circle",
            WindowsPhoneTheme.TILE_RED
        )
        btn_cancelar.setMinimumHeight(100)
        btn_cancelar.clicked.connect(self.reject)
        buttons_layout.addWidget(btn_cancelar, 1)
        
        layout.addLayout(buttons_layout)
    
    def agregar_info_row(self, layout, etiqueta, valor, color_valor=None):
        """Agregar una fila de información"""
        row = QHBoxLayout()
        row.setSpacing(10)
        
        # Etiqueta
        label_etiqueta = QLabel(etiqueta)
        label_etiqueta.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL, QFont.Bold))
        label_etiqueta.setStyleSheet("color: #6b7280;")
        label_etiqueta.setMinimumWidth(150)
        row.addWidget(label_etiqueta)
        
        # Valor
        label_valor = QLabel(valor)
        label_valor.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL))
        if color_valor:
            label_valor.setStyleSheet(f"color: {color_valor}; font-weight: bold;")
        else:
            label_valor.setStyleSheet("color: #1f2937;")
        row.addWidget(label_valor)
        row.addStretch()
        
        layout.addLayout(row)
    
    def cargar_foto(self):
        """Cargar foto del miembro o mostrar placeholder"""
        # Intentar cargar foto si existe
        foto_path = self.miembro_data.get('foto')
        
        if foto_path and os.path.exists(foto_path):
            pixmap = QPixmap(foto_path)
            if not pixmap.isNull():
                # Escalar manteniendo proporción
                pixmap = pixmap.scaled(
                    200, 200,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                # Crear imagen circular
                pixmap = self.crear_imagen_circular(pixmap)
                self.foto_label.setPixmap(pixmap)
                return
        
        # Si no hay foto, mostrar placeholder
        self.mostrar_placeholder()
    
    def crear_imagen_circular(self, pixmap):
        """Crear una imagen circular a partir de un pixmap"""
        # Crear un pixmap cuadrado del tamaño de la imagen
        size = min(pixmap.width(), pixmap.height())
        rounded = QPixmap(size, size)
        rounded.fill(Qt.transparent)
        
        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Crear path circular
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)
        
        # Dibujar imagen centrada
        x = (size - pixmap.width()) // 2
        y = (size - pixmap.height()) // 2
        painter.drawPixmap(x, y, pixmap)
        painter.end()
        
        return rounded
    
    def mostrar_placeholder(self):
        """Mostrar placeholder cuando no hay foto"""
        # Crear placeholder con iniciales
        iniciales = self.obtener_iniciales()
        
        placeholder = QPixmap(200, 200)
        placeholder.fill(Qt.transparent)
        
        painter = QPainter(placeholder)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Círculo de fondo
        painter.setBrush(QColor(WindowsPhoneTheme.TILE_BLUE))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 200, 200)
        
        # Iniciales
        painter.setPen(Qt.white)
        painter.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, 60, QFont.Bold))
        painter.drawText(0, 0, 200, 200, Qt.AlignCenter, iniciales)
        
        painter.end()
        
        self.foto_label.setPixmap(placeholder)
    
    def obtener_iniciales(self):
        """Obtener iniciales del nombre del miembro"""
        nombres = self.miembro_data.get('nombres', 'X').strip()
        apellido = self.miembro_data.get('apellido_paterno', 'X').strip()
        
        inicial_nombre = nombres[0].upper() if nombres else 'X'
        inicial_apellido = apellido[0].upper() if apellido else 'X'
        
        return f"{inicial_nombre}{inicial_apellido}"
    
    def confirmar_acceso(self):
        """Confirmar y registrar el acceso"""
        logging.info(f"Acceso confirmado para miembro ID: {self.miembro_data['id_miembro']}")
        self.acceso_confirmado.emit(self.miembro_data)
        self.accept()
    
    def aplicar_estilos(self):
        """Aplicar estilos personalizados al diálogo"""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: white;
            }}
            
            #dialogHeader {{
                background-color: {WindowsPhoneTheme.PRIMARY_BLUE};
            }}
            
            #dialogTitle {{
                color: white;
            }}
            
            #dialogContent {{
                background-color: white;
            }}
            
            #datosContainer {{
                background-color: {WindowsPhoneTheme.BG_LIGHT};
                border: 2px solid {WindowsPhoneTheme.PRIMARY_BLUE};
                border-radius: 0px;
            }}
            
            #fotoMiembro {{
                border: 4px solid {WindowsPhoneTheme.PRIMARY_BLUE};
                border-radius: 100px;
                background-color: white;
            }}
        """)
