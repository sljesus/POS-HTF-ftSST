"""
Formularios de Movimientos de Inventario para HTF POS
Registro de entradas y salidas
Usando componentes reutilizables del sistema de diseño
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLineEdit, QSpinBox, QTextEdit,
    QLabel, QComboBox, QDateEdit, QScrollArea,
    QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QDate, QEvent, QTimer
from PySide6.QtGui import QFont
import logging
from datetime import datetime

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
    show_error_dialog,
    show_success_dialog
)


class MovimientoInventarioWindow(QWidget):
    """Formulario para registrar entrada o salida de inventario"""
    
    cerrar_solicitado = Signal()
    movimiento_registrado = Signal(dict)
    
    def __init__(self, tipo_movimiento, db_manager, supabase_service, user_data, parent=None):
        super().__init__(parent)
        self.tipo_movimiento = tipo_movimiento  # "entrada" o "salida"
        self.db_manager = db_manager
        self.supabase_service = supabase_service
        self.user_data = user_data
        self.producto_seleccionado = None
        
        # Timer para detectar entrada del escáner
        self.scanner_timer = QTimer()
        self.scanner_timer.setSingleShot(True)
        self.scanner_timer.setInterval(300)  # 300ms después de que deje de escribir
        self.scanner_timer.timeout.connect(self.buscar_producto)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar interfaz del formulario"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Título según el tipo
        titulo = "REGISTRAR ENTRADA" if self.tipo_movimiento == "entrada" else "REGISTRAR SALIDA"
        color = WindowsPhoneTheme.TILE_GREEN if self.tipo_movimiento == "entrada" else WindowsPhoneTheme.TILE_RED
        
        # Contenedor principal
        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(
            WindowsPhoneTheme.MARGIN_MEDIUM,
            WindowsPhoneTheme.MARGIN_SMALL,
            WindowsPhoneTheme.MARGIN_MEDIUM,
            WindowsPhoneTheme.MARGIN_SMALL
        )
        main_layout.setSpacing(WindowsPhoneTheme.MARGIN_SMALL)
        
        # Título
        title_label = StyledLabel(titulo, bold=True, size=WindowsPhoneTheme.FONT_SIZE_TITLE)
        title_label.setStyleSheet(f"color: {color}; padding: 10px 0;")
        main_layout.addWidget(title_label)
        
        # Scroll Area para el formulario
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Widget de contenido del scroll
        scroll_content = QWidget()
        form_layout = QVBoxLayout(scroll_content)
        form_layout.setContentsMargins(0, 0, 10, 0)
        form_layout.setSpacing(WindowsPhoneTheme.MARGIN_SMALL)
        
        # Panel del formulario
        form_panel = ContentPanel()
        panel_layout = QVBoxLayout(form_panel)
        panel_layout.setContentsMargins(
            WindowsPhoneTheme.MARGIN_MEDIUM,
            WindowsPhoneTheme.MARGIN_SMALL,
            WindowsPhoneTheme.MARGIN_MEDIUM,
            WindowsPhoneTheme.MARGIN_SMALL
        )
        panel_layout.setSpacing(WindowsPhoneTheme.MARGIN_SMALL)
        
        # Búsqueda de producto
        search_label = StyledLabel("Buscar Producto", bold=True, size=WindowsPhoneTheme.FONT_SIZE_SUBTITLE)
        panel_layout.addWidget(search_label)
        
        self.search_bar = SearchBar("Código interno o código de barras...")
        self.search_bar.search_input.installEventFilter(self)
        self.search_bar.search_input.returnPressed.connect(self.buscar_producto)
        self.search_bar.search_input.textChanged.connect(self._on_search_text_changed)
        self.search_bar.search_button.clicked.connect(self.buscar_producto)
        panel_layout.addWidget(self.search_bar)
        
        # Información del producto encontrado
        self.producto_info_label = StyledLabel("", size=WindowsPhoneTheme.FONT_SIZE_NORMAL)
        self.producto_info_label.setWordWrap(True)
        self.producto_info_label.setStyleSheet(f"color: {WindowsPhoneTheme.PRIMARY_BLUE}; padding: 10px; background-color: {WindowsPhoneTheme.BG_LIGHT}; border-radius: 4px;")
        self.producto_info_label.hide()
        panel_layout.addWidget(self.producto_info_label)
        
        # Cantidad
        cantidad_label = StyledLabel("Cantidad *", bold=True, size=WindowsPhoneTheme.FONT_SIZE_SUBTITLE)
        panel_layout.addWidget(cantidad_label)
        
        self.cantidad_spin = QSpinBox()
        self.cantidad_spin.setRange(1, 9999)
        self.cantidad_spin.setValue(1)
        self.cantidad_spin.setMinimumHeight(46)
        self.cantidad_spin.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL))
        panel_layout.addWidget(self.cantidad_spin)
        
        # Tipo de movimiento (solo para entradas)
        if self.tipo_movimiento == "entrada":
            tipo_label = StyledLabel("Tipo de Entrada *", bold=True, size=WindowsPhoneTheme.FONT_SIZE_SUBTITLE)
            panel_layout.addWidget(tipo_label)
            
            self.tipo_combo = QComboBox()
            self.tipo_combo.addItems([
                "Compra",
                "Devolución",
                "Ajuste de inventario",
                "Donación",
                "Otro"
            ])
            self.tipo_combo.setMinimumHeight(46)
            self.tipo_combo.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL))
            panel_layout.addWidget(self.tipo_combo)
        else:
            # Motivo de salida
            motivo_label = StyledLabel("Motivo de Salida *", bold=True, size=WindowsPhoneTheme.FONT_SIZE_SUBTITLE)
            panel_layout.addWidget(motivo_label)
            
            self.motivo_combo = QComboBox()
            self.motivo_combo.addItems([
                "Venta",
                "Merma",
                "Vencimiento",
                "Donación",
                "Ajuste de inventario",
                "Otro"
            ])
            self.motivo_combo.setMinimumHeight(46)
            self.motivo_combo.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL))
            panel_layout.addWidget(self.motivo_combo)
        
        # Fecha
        fecha_label = StyledLabel("Fecha", bold=True, size=WindowsPhoneTheme.FONT_SIZE_SUBTITLE)
        panel_layout.addWidget(fecha_label)
        
        self.fecha_input = QDateEdit()
        self.fecha_input.setDate(QDate.currentDate())
        self.fecha_input.setCalendarPopup(True)
        self.fecha_input.setDisplayFormat("dd/MM/yyyy")
        self.fecha_input.setMinimumHeight(46)
        self.fecha_input.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL))
        panel_layout.addWidget(self.fecha_input)
        
        # Observaciones
        obs_label = StyledLabel("Observaciones", bold=True, size=WindowsPhoneTheme.FONT_SIZE_SUBTITLE)
        panel_layout.addWidget(obs_label)
        
        self.observaciones_input = QTextEdit()
        self.observaciones_input.setPlaceholderText("Notas adicionales sobre el movimiento (opcional)")
        self.observaciones_input.setMaximumHeight(80)
        self.observaciones_input.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL))
        panel_layout.addWidget(self.observaciones_input)
        
        # Agregar panel al layout del scroll
        form_layout.addWidget(form_panel)
        form_layout.addStretch()
        
        # Configurar scroll
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        
        # Botones de acción (fuera del scroll)
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(WindowsPhoneTheme.TILE_SPACING)
        
        btn_guardar = TileButton(
            "Registrar " + ("Entrada" if self.tipo_movimiento == "entrada" else "Salida"),
            "fa5s.check",
            WindowsPhoneTheme.TILE_GREEN  # Siempre verde
        )
        btn_guardar.clicked.connect(self.registrar_movimiento)
        
        btn_cancelar = TileButton("Cancelar", "fa5s.times", WindowsPhoneTheme.TILE_RED)
        btn_cancelar.clicked.connect(self.cerrar_solicitado.emit)
        
        buttons_layout.addWidget(btn_guardar)
        buttons_layout.addWidget(btn_cancelar)
        
        main_layout.addLayout(buttons_layout)
        layout.addWidget(main_container)
    
    def eventFilter(self, obj, event):
        """Filtrar eventos para detectar Enter del scanner en búsqueda de producto"""
        if obj == self.search_bar.search_input and event.type() == QEvent.KeyPress:
            key_event = event
            # Solo loguear si es Enter, para no saturar el log
            if key_event.key() in (Qt.Key_Return, Qt.Key_Enter):
                logging.info("[SCANNER] Enter detectado - buscando producto")
                self.buscar_producto()
                return True  # Evento manejado
        
        return super().eventFilter(obj, event)
    
    def _on_search_text_changed(self):
        """Detectar cuando se ingresa texto (para capturar escáner)"""
        texto = self.search_bar.search_input.text().strip()
        
        # Reiniciar el timer cada vez que cambia el texto
        self.scanner_timer.stop()
        
        # Si el texto tiene longitud suficiente para ser un código
        if len(texto) >= 6:  # Códigos típicamente tienen 6+ caracteres
            logging.info(f"[SCANNER] Código detectado (longitud {len(texto)}), iniciando timer...")
            # Iniciar timer para buscar después de 300ms de inactividad
            self.scanner_timer.start()
    
    def buscar_producto(self):
        """Buscar producto por código"""
        codigo = self.search_bar.search_input.text().strip()
        
        if not codigo:
            show_warning_dialog(
                self,
                "Código requerido",
                "Ingresa un código interno o código de barras"
            )
            return
        
        try:
            # Buscar primero por código interno
            producto = self.db_manager.get_product_by_code(codigo)
            
            # Si no se encuentra, buscar por código de barras
            if not producto:
                producto = self.db_manager.get_product_by_barcode(codigo)
            
            if producto:
                self.producto_seleccionado = producto
                
                # Mostrar información del producto
                stock_actual = producto['stock_actual'] if producto['stock_actual'] else 0
                info_text = (
                    f"✓ Producto encontrado\n"
                    f"Código: {producto['codigo_interno']}\n"
                    f"Nombre: {producto['nombre']}\n"
                    f"Stock actual: {stock_actual} unidades"
                )
                
                self.producto_info_label.setText(info_text)
                self.producto_info_label.show()
                self.cantidad_spin.setFocus()
                
                logging.info(f"Producto encontrado: {producto['codigo_interno']} - {producto['nombre']}")
            else:
                self.producto_seleccionado = None
                self.producto_info_label.hide()
                show_warning_dialog(
                    self,
                    "Producto no encontrado",
                    f"No se encontró ningún producto con el código '{codigo}'"
                )
        
        except Exception as e:
            logging.error(f"Error buscando producto: {e}")
            show_error_dialog(
                self,
                "Error de búsqueda",
                "No se pudo buscar el producto",
                detail=str(e)
            )
    
    def registrar_movimiento(self):
        """Registrar el movimiento de inventario"""
        if not self.producto_seleccionado:
            show_warning_dialog(
                self,
                "Producto requerido",
                "Primero debes buscar y seleccionar un producto"
            )
            self.search_input.setFocus()
            return
        
        cantidad = self.cantidad_spin.value()
        if cantidad <= 0:
            show_warning_dialog(
                self,
                "Cantidad inválida",
                "La cantidad debe ser mayor a 0"
            )
            return
        
        # Validar stock suficiente para salidas
        if self.tipo_movimiento == "salida":
            stock_actual = self.producto_seleccionado['stock_actual'] if self.producto_seleccionado['stock_actual'] else 0
            if cantidad > stock_actual:
                show_warning_dialog(
                    self,
                    "Stock insuficiente",
                    f"No hay suficiente stock disponible\n\nStock actual: {stock_actual}\nCantidad solicitada: {cantidad}"
                )
                return
        
        try:
            # Preparar datos del movimiento
            tipo = self.tipo_combo.currentText() if self.tipo_movimiento == "entrada" else self.motivo_combo.currentText()
            fecha = self.fecha_input.date().toPython().strftime("%Y-%m-%d")
            observaciones = self.observaciones_input.toPlainText().strip() or None
            
            # Actualizar stock en inventario
            cursor = self.db_manager.connection.cursor()
            
            # Obtener stock actual antes del movimiento
            cursor.execute("SELECT stock_actual FROM inventario WHERE codigo_interno = ?", 
                          (self.producto_seleccionado['codigo_interno'],))
            stock_anterior = cursor.fetchone()[0]
            
            if self.tipo_movimiento == "entrada":
                # Incrementar stock
                nuevo_stock = stock_anterior + cantidad
                cursor.execute("""
                    UPDATE inventario 
                    SET stock_actual = ?,
                        fecha_ultima_entrada = CURRENT_TIMESTAMP
                    WHERE codigo_interno = ?
                """, (nuevo_stock, self.producto_seleccionado['codigo_interno']))
            else:
                # Decrementar stock
                nuevo_stock = stock_anterior - cantidad
                cursor.execute("""
                    UPDATE inventario 
                    SET stock_actual = ?,
                        fecha_ultima_salida = CURRENT_TIMESTAMP
                    WHERE codigo_interno = ?
                """, (nuevo_stock, self.producto_seleccionado['codigo_interno']))
            
            # Registrar el movimiento en la tabla de movimientos
            cursor.execute("""
                INSERT INTO movimientos_inventario (
                    codigo_interno,
                    tipo_producto,
                    tipo_movimiento,
                    cantidad,
                    stock_anterior,
                    stock_nuevo,
                    motivo,
                    fecha,
                    id_usuario
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.producto_seleccionado['codigo_interno'],
                self.producto_seleccionado['tipo'],
                self.tipo_movimiento,
                cantidad if self.tipo_movimiento == "entrada" else -cantidad,  # Positivo para entrada, negativo para salida
                stock_anterior,
                nuevo_stock,
                tipo,
                fecha,
                self.user_data.get('id') or self.user_data.get('id_usuario')  # Soportar ambas claves
            ))
            
            self.db_manager.connection.commit()
            
            # Obtener nuevo stock
            cursor.execute("SELECT stock_actual FROM inventario WHERE codigo_interno = ?", 
                          (self.producto_seleccionado['codigo_interno'],))
            nuevo_stock = cursor.fetchone()[0]
            
            show_success_dialog(
                self,
                "Movimiento registrado",
                f"El movimiento de inventario ha sido registrado exitosamente",
                detail=(
                    f"Producto: {self.producto_seleccionado['nombre']}\n"
                    f"Cantidad: {cantidad}\n"
                    f"Stock nuevo: {nuevo_stock} unidades"
                )
            )
            
            # Emitir señal con información del movimiento
            self.movimiento_registrado.emit({
                'tipo': self.tipo_movimiento,
                'producto': self.producto_seleccionado['nombre'],
                'cantidad': cantidad,
                'stock_nuevo': nuevo_stock
            })
            
            logging.info(
                f"Movimiento registrado: {self.tipo_movimiento} - "
                f"{self.producto_seleccionado['codigo_interno']} - Cantidad: {cantidad}"
            )
            
            # Limpiar formulario
            self.limpiar_formulario()
            
        except Exception as e:
            self.db_manager.connection.rollback()
            logging.error(f"Error registrando movimiento: {e}")
            show_error_dialog(
                self,
                "Error al registrar",
                "No se pudo registrar el movimiento de inventario",
                detail=str(e)
            )
    
    def limpiar_formulario(self):
        """Limpiar el formulario después de registrar"""
        self.search_input.clear()
        self.cantidad_spin.setValue(1)
        self.observaciones_input.clear()
        self.producto_info_label.hide()
        self.producto_seleccionado = None
        self.search_input.setFocus()
        
        if self.tipo_movimiento == "entrada":
            self.tipo_combo.setCurrentIndex(0)
        else:
            self.motivo_combo.setCurrentIndex(0)
