"""
Formulario de Nuevo Producto para HTF POS
Permite agregar productos normales (varios) y suplementos
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QComboBox, QCheckBox,
    QDoubleSpinBox, QSpinBox, QDateEdit, QScrollArea,
    QLabel, QFrame
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont
import logging

from ui.components import (
    WindowsPhoneTheme,
    TileButton,
    create_page_layout,
    ContentPanel,
    SectionTitle,
    show_info_dialog,
    show_warning_dialog,
    show_error_dialog,
    show_confirmation_dialog
)


class NuevoProductoWindow(QWidget):
    """Formulario unificado para agregar productos normales y suplementos"""
    
    cerrar_solicitado = Signal()
    producto_guardado = Signal()
    
    def __init__(self, db_manager, supabase_service, user_data, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.supabase_service = supabase_service
        self.user_data = user_data
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar interfaz del formulario"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Contenido principal con scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        content = QWidget()
        content_layout = create_page_layout("NUEVO PRODUCTO")
        content.setLayout(content_layout)
        
        # Panel del formulario
        form_panel = ContentPanel()
        form_layout = QVBoxLayout(form_panel)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(25)
        
        # ===== SELECTOR DE TIPO DE PRODUCTO =====
        tipo_section = QVBoxLayout()
        tipo_section.setSpacing(10)
        
        tipo_label = QLabel("TIPO DE PRODUCTO *")
        tipo_label.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_SUBTITLE, QFont.Bold))
        tipo_label.setStyleSheet(f"color: {WindowsPhoneTheme.PRIMARY_BLUE};")
        tipo_section.addWidget(tipo_label)
        
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Producto Normal (Varios)", "Suplemento"])
        self.tipo_combo.setMinimumHeight(45)
        self.tipo_combo.currentIndexChanged.connect(self.on_tipo_changed)
        tipo_section.addWidget(self.tipo_combo)
        
        form_layout.addLayout(tipo_section)
        
        # Línea divisoria
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet(f"background-color: {WindowsPhoneTheme.PRIMARY_BLUE}; max-height: 2px;")
        form_layout.addWidget(line)
        
        # ===== CAMPOS COMUNES =====
        comunes_title = SectionTitle("INFORMACIÓN GENERAL")
        form_layout.addWidget(comunes_title)
        
        comunes_form = QFormLayout()
        comunes_form.setSpacing(15)
        comunes_form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Código Interno
        self.codigo_interno_input = QLineEdit()
        self.codigo_interno_input.setPlaceholderText("Ej: PROD001")
        self.codigo_interno_input.setMinimumHeight(40)
        self.codigo_interno_input.textChanged.connect(lambda text: self.codigo_interno_input.setText(text.upper()))
        comunes_form.addRow("Código Interno *:", self.codigo_interno_input)
        
        # Nombre
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre completo del producto")
        self.nombre_input.setMinimumHeight(40)
        comunes_form.addRow("Nombre *:", self.nombre_input)
        
        # Descripción
        self.descripcion_input = QTextEdit()
        self.descripcion_input.setPlaceholderText("Descripción detallada (opcional)")
        self.descripcion_input.setMaximumHeight(100)
        comunes_form.addRow("Descripción:", self.descripcion_input)
        
        # Precio de Venta
        self.precio_input = QDoubleSpinBox()
        self.precio_input.setPrefix("$ ")
        self.precio_input.setDecimals(2)
        self.precio_input.setMaximum(999999.99)
        self.precio_input.setMinimumHeight(40)
        comunes_form.addRow("Precio de Venta *:", self.precio_input)
        
        # Activo
        self.activo_check = QCheckBox("Producto activo")
        self.activo_check.setChecked(True)
        comunes_form.addRow("Estado:", self.activo_check)
        
        form_layout.addLayout(comunes_form)
        
        # ===== CAMPOS DE PRODUCTOS NORMALES =====
        self.normales_widget = QWidget()
        normales_layout = QVBoxLayout(self.normales_widget)
        normales_layout.setContentsMargins(0, 0, 0, 0)
        normales_layout.setSpacing(15)
        
        normales_title = SectionTitle("DATOS DE PRODUCTO NORMAL")
        normales_layout.addWidget(normales_title)
        
        normales_form = QFormLayout()
        normales_form.setSpacing(15)
        normales_form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Código de Barras
        self.codigo_barras_input = QLineEdit()
        self.codigo_barras_input.setPlaceholderText("Ej: 7501234567890")
        self.codigo_barras_input.setMinimumHeight(40)
        normales_form.addRow("Código de Barras:", self.codigo_barras_input)
        
        # Categoría
        self.categoria_input = QLineEdit()
        self.categoria_input.setPlaceholderText("Ej: Bebidas, Snacks, Accesorios")
        self.categoria_input.setText("General")
        self.categoria_input.setMinimumHeight(40)
        normales_form.addRow("Categoría:", self.categoria_input)
        
        # Requiere Refrigeración
        self.refrigeracion_check = QCheckBox("Requiere refrigeración")
        normales_form.addRow("Refrigeración:", self.refrigeracion_check)
        
        # Peso
        self.peso_input = QDoubleSpinBox()
        self.peso_input.setSuffix(" gr")
        self.peso_input.setDecimals(2)
        self.peso_input.setMaximum(999999.99)
        self.peso_input.setMinimumHeight(40)
        normales_form.addRow("Peso:", self.peso_input)
        
        normales_layout.addLayout(normales_form)
        form_layout.addWidget(self.normales_widget)
        
        # ===== CAMPOS DE SUPLEMENTOS =====
        self.suplementos_widget = QWidget()
        suplementos_layout = QVBoxLayout(self.suplementos_widget)
        suplementos_layout.setContentsMargins(0, 0, 0, 0)
        suplementos_layout.setSpacing(15)
        
        suplementos_title = SectionTitle("DATOS DE SUPLEMENTO")
        suplementos_layout.addWidget(suplementos_title)
        
        suplementos_form = QFormLayout()
        suplementos_form.setSpacing(15)
        suplementos_form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Marca
        self.marca_input = QLineEdit()
        self.marca_input.setPlaceholderText("Ej: Optimum Nutrition, Dymatize")
        self.marca_input.setMinimumHeight(40)
        suplementos_form.addRow("Marca *:", self.marca_input)
        
        # Tipo de Suplemento
        self.tipo_suplemento_combo = QComboBox()
        self.tipo_suplemento_combo.addItems([
            "Proteína",
            "Creatina",
            "Pre-entreno",
            "Post-entreno",
            "BCAA",
            "Glutamina",
            "Vitaminas",
            "Aminoácidos",
            "Quemador",
            "Ganador de Masa",
            "Otro"
        ])
        self.tipo_suplemento_combo.setMinimumHeight(45)
        suplementos_form.addRow("Tipo de Suplemento *:", self.tipo_suplemento_combo)
        
        # Sabor
        self.sabor_input = QLineEdit()
        self.sabor_input.setPlaceholderText("Ej: Chocolate, Vainilla, Fresa")
        self.sabor_input.setMinimumHeight(40)
        suplementos_form.addRow("Sabor:", self.sabor_input)
        
        # Presentación
        self.presentacion_input = QLineEdit()
        self.presentacion_input.setPlaceholderText("Ej: Bote, Bolsa, Cápsula")
        self.presentacion_input.setMinimumHeight(40)
        suplementos_form.addRow("Presentación:", self.presentacion_input)
        
        # Peso Neto
        self.peso_neto_input = QDoubleSpinBox()
        self.peso_neto_input.setSuffix(" gr")
        self.peso_neto_input.setDecimals(2)
        self.peso_neto_input.setMaximum(999999.99)
        self.peso_neto_input.setMinimumHeight(40)
        suplementos_form.addRow("Peso Neto:", self.peso_neto_input)
        
        # Porciones Totales
        self.porciones_input = QSpinBox()
        self.porciones_input.setMaximum(9999)
        self.porciones_input.setMinimumHeight(40)
        suplementos_form.addRow("Porciones Totales:", self.porciones_input)
        
        # Calorías por Porción
        self.calorias_input = QDoubleSpinBox()
        self.calorias_input.setSuffix(" kcal")
        self.calorias_input.setDecimals(2)
        self.calorias_input.setMaximum(9999.99)
        self.calorias_input.setMinimumHeight(40)
        suplementos_form.addRow("Calorías/Porción:", self.calorias_input)
        
        # Proteína por Porción
        self.proteina_input = QDoubleSpinBox()
        self.proteina_input.setSuffix(" gr")
        self.proteina_input.setDecimals(2)
        self.proteina_input.setMaximum(9999.99)
        self.proteina_input.setMinimumHeight(40)
        suplementos_form.addRow("Proteína/Porción:", self.proteina_input)
        
        # Fecha de Vencimiento
        self.fecha_vencimiento_input = QDateEdit()
        self.fecha_vencimiento_input.setCalendarPopup(True)
        self.fecha_vencimiento_input.setDate(QDate.currentDate().addYears(1))
        self.fecha_vencimiento_input.setMinimumHeight(40)
        self.fecha_vencimiento_input.setDisplayFormat("dd/MM/yyyy")
        suplementos_form.addRow("Fecha Vencimiento:", self.fecha_vencimiento_input)
        
        suplementos_layout.addLayout(suplementos_form)
        form_layout.addWidget(self.suplementos_widget)
        
        # Agregar panel al contenido
        content_layout.addWidget(form_panel)
        
        # ===== BOTONES DE ACCIÓN =====
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(WindowsPhoneTheme.TILE_SPACING)
        
        btn_guardar = TileButton("Guardar Producto", "fa5s.save", WindowsPhoneTheme.TILE_GREEN)
        btn_guardar.clicked.connect(self.guardar_producto)
        
        btn_limpiar = TileButton("Limpiar Formulario", "fa5s.eraser", WindowsPhoneTheme.TILE_ORANGE)
        btn_limpiar.clicked.connect(self.limpiar_formulario)
        
        btn_cancelar = TileButton("Cancelar", "fa5s.times", WindowsPhoneTheme.TILE_RED)
        btn_cancelar.clicked.connect(self.confirmar_cancelar)
        
        buttons_layout.addWidget(btn_guardar)
        buttons_layout.addWidget(btn_limpiar)
        buttons_layout.addWidget(btn_cancelar)
        
        content_layout.addLayout(buttons_layout)
        
        # Configurar scroll
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        # Mostrar/ocultar campos según tipo inicial
        self.on_tipo_changed(0)
    
    def on_tipo_changed(self, index):
        """Manejar cambio de tipo de producto"""
        is_normal = (index == 0)
        
        # Mostrar/ocultar widgets correspondientes
        self.normales_widget.setVisible(is_normal)
        self.suplementos_widget.setVisible(not is_normal)
    
    def limpiar_formulario(self):
        """Limpiar todos los campos del formulario"""
        # Campos comunes
        self.codigo_interno_input.clear()
        self.nombre_input.clear()
        self.descripcion_input.clear()
        self.precio_input.setValue(0.0)
        self.activo_check.setChecked(True)
        
        # Campos de productos normales
        self.codigo_barras_input.clear()
        self.categoria_input.setText("General")
        self.refrigeracion_check.setChecked(False)
        self.peso_input.setValue(0.0)
        
        # Campos de suplementos
        self.marca_input.clear()
        self.tipo_suplemento_combo.setCurrentIndex(0)
        self.sabor_input.clear()
        self.presentacion_input.clear()
        self.peso_neto_input.setValue(0.0)
        self.porciones_input.setValue(0)
        self.calorias_input.setValue(0.0)
        self.proteina_input.setValue(0.0)
        self.fecha_vencimiento_input.setDate(QDate.currentDate().addYears(1))
        
        # Enfocar primer campo
        self.codigo_interno_input.setFocus()
        
        logging.info("Formulario limpiado")
    
    def confirmar_cancelar(self):
        """Confirmar antes de cancelar"""
        if show_confirmation_dialog(
            self,
            "Cancelar",
            "¿Desea cancelar y volver sin guardar?",
            "Se perderán todos los cambios no guardados."
        ):
            self.cerrar_solicitado.emit()
    
    def validar_campos(self):
        """Validar campos del formulario"""
        is_normal = (self.tipo_combo.currentIndex() == 0)
        
        # Validar campos comunes
        if not self.codigo_interno_input.text().strip():
            show_warning_dialog(self, "Campo requerido", "Debe ingresar un código interno.")
            self.codigo_interno_input.setFocus()
            return False
        
        if not self.nombre_input.text().strip():
            show_warning_dialog(self, "Campo requerido", "Debe ingresar un nombre.")
            self.nombre_input.setFocus()
            return False
        
        if self.precio_input.value() <= 0:
            show_warning_dialog(self, "Precio inválido", "El precio debe ser mayor a cero.")
            self.precio_input.setFocus()
            return False
        
        # Validar campos específicos de suplementos
        if not is_normal:
            if not self.marca_input.text().strip():
                show_warning_dialog(self, "Campo requerido", "Debe ingresar una marca para el suplemento.")
                self.marca_input.setFocus()
                return False
        
        # Verificar código interno único
        codigo = self.codigo_interno_input.text().strip().upper()
        if self.db_manager.producto_existe(codigo):
            show_error_dialog(
                self,
                "Código duplicado",
                f"El código '{codigo}' ya existe en el sistema.",
                "Por favor, use un código diferente."
            )
            self.codigo_interno_input.setFocus()
            return False
        
        return True
    
    def guardar_producto(self):
        """Guardar el producto en la base de datos"""
        try:
            # Validar campos
            if not self.validar_campos():
                return
            
            is_normal = (self.tipo_combo.currentIndex() == 0)
            
            # Preparar datos comunes
            codigo_interno = self.codigo_interno_input.text().strip().upper()
            nombre = self.nombre_input.text().strip()
            descripcion = self.descripcion_input.toPlainText().strip() or None
            precio = self.precio_input.value()
            activo = self.activo_check.isChecked()
            
            if is_normal:
                # Guardar producto normal
                producto_data = {
                    'codigo_interno': codigo_interno,
                    'codigo_barras': self.codigo_barras_input.text().strip() or None,
                    'nombre': nombre,
                    'descripcion': descripcion,
                    'precio_venta': precio,
                    'categoria': self.categoria_input.text().strip() or 'General',
                    'requiere_refrigeracion': self.refrigeracion_check.isChecked(),
                    'peso_gr': self.peso_input.value() if self.peso_input.value() > 0 else None,
                    'activo': activo,
                    'needs_sync': 1
                }
                
                success = self.db_manager.insertar_producto_varios(producto_data)
                tipo_msg = "producto normal"
            else:
                # Guardar suplemento
                suplemento_data = {
                    'codigo_interno': codigo_interno,
                    'nombre': nombre,
                    'descripcion': descripcion,
                    'marca': self.marca_input.text().strip(),
                    'tipo': self.tipo_suplemento_combo.currentText(),
                    'sabor': self.sabor_input.text().strip() or None,
                    'presentacion': self.presentacion_input.text().strip() or None,
                    'peso_neto_gr': self.peso_neto_input.value() if self.peso_neto_input.value() > 0 else None,
                    'porciones_totales': self.porciones_input.value() if self.porciones_input.value() > 0 else None,
                    'calorias_por_porcion': self.calorias_input.value() if self.calorias_input.value() > 0 else None,
                    'proteina_por_porcion_gr': self.proteina_input.value() if self.proteina_input.value() > 0 else None,
                    'precio_venta': precio,
                    'activo': activo,
                    'fecha_vencimiento': self.fecha_vencimiento_input.date().toString("yyyy-MM-dd"),
                    'needs_sync': 1
                }
                
                success = self.db_manager.insertar_suplemento(suplemento_data)
                tipo_msg = "suplemento"
            
            if success:
                # Crear registro en inventario
                inventario_data = {
                    'codigo_interno': codigo_interno,
                    'tipo_producto': 'varios' if is_normal else 'suplemento',
                    'stock_actual': 0,
                    'stock_minimo': 5,
                    'ubicacion': 'Recepción',
                    'activo': activo,
                    'needs_sync': 1
                }
                
                self.db_manager.crear_inventario(inventario_data)
                
                # Mostrar mensaje de éxito
                show_info_dialog(
                    self,
                    "Producto guardado",
                    f"El {tipo_msg} '{nombre}' se guardó correctamente.",
                    f"Código: {codigo_interno}\nInventario inicial: 0 unidades"
                )
                
                # Limpiar formulario y emitir señal
                self.limpiar_formulario()
                self.producto_guardado.emit()
                
                logging.info(f"Producto guardado: {codigo_interno} - {nombre}")
            else:
                show_error_dialog(
                    self,
                    "Error al guardar",
                    "No se pudo guardar el producto.",
                    "Verifique los datos e intente nuevamente."
                )
        
        except Exception as e:
            logging.error(f"Error guardando producto: {e}")
            show_error_dialog(
                self,
                "Error",
                "Ocurrió un error al guardar el producto",
                detail=str(e)
            )
