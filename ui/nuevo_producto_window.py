import logging
import qtawesome as qta
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDateEdit, QFrame,
                               QGridLayout, QHBoxLayout, QLabel, QLineEdit,
                               QPushButton, QSpacerItem, QTextEdit,
                               QVBoxLayout, QWidget)

from ui.components import (SectionTitle, StyledLabel, WindowsPhoneTheme, 
                           show_error_dialog, show_success_dialog)


class NuevoProductoWindow(QFrame):
    """
    Ventana de formulario para agregar nuevos productos (Varios o Suplementos).
    """
    cerrar_solicitado = Signal()
    producto_guardado = Signal()

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setObjectName("contentPanel")
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        self._setup_ui()

    def _setup_ui(self):
        # Título de la sección
        title = SectionTitle("Registrar Nuevo Producto")
        self.main_layout.addWidget(title)

        # Selector de tipo de producto
        type_selector_layout = QHBoxLayout()
        type_selector_layout.addWidget(StyledLabel("Tipo de Producto:", bold=True))
        self.tipo_producto_combo = QComboBox()
        self.tipo_producto_combo.addItems(["Producto Normal (Varios)", "Suplemento"])
        self.tipo_producto_combo.currentIndexChanged.connect(self._toggle_product_fields)
        type_selector_layout.addWidget(self.tipo_producto_combo)
        type_selector_layout.addStretch()
        self.main_layout.addLayout(type_selector_layout)

        # Layout de grid para los campos del formulario
        self.form_grid_layout = QGridLayout()
        self.form_grid_layout.setSpacing(10)
        
        # Campos comunes
        self.codigo_interno_input = self._add_form_row("Código Interno*:", QLineEdit(), 0)
        self.nombre_input = self._add_form_row("Nombre*:", QLineEdit(), 1)
        self.descripcion_input = self._add_form_row("Descripción:", QTextEdit(), 2)
        self.descripcion_input.setFixedHeight(80)
        self.precio_venta_input = self._add_form_row("Precio de Venta*:", QLineEdit(), 3)
        self.activo_check = QCheckBox("Activo")
        self.activo_check.setChecked(True)
        self.form_grid_layout.addWidget(self.activo_check, 4, 1)

        # Contenedores para campos específicos
        self._create_varios_fields()
        self._create_suplementos_fields()

        self.main_layout.addLayout(self.form_grid_layout)
        self.main_layout.addWidget(self.varios_group)
        self.main_layout.addWidget(self.suplementos_group)
        
        self.main_layout.addStretch()

        # Botones de acción
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setObjectName("dialogSecondaryButton")
        self.cancel_button.clicked.connect(self.cerrar_solicitado.emit)
        buttons_layout.addWidget(self.cancel_button)

        self.save_button = QPushButton("Guardar Producto")
        self.save_button.setObjectName("dialogPrimaryButton")
        self.save_button.setIcon(qta.icon("fa5s.save", color="white"))
        self.save_button.clicked.connect(self._save_product)
        buttons_layout.addWidget(self.save_button)
        
        self.main_layout.addLayout(buttons_layout)

        self._toggle_product_fields()

    def _add_form_row(self, label_text, widget, row):
        label = StyledLabel(label_text)
        self.form_grid_layout.addWidget(label, row, 0, Qt.AlignTop)
        self.form_grid_layout.addWidget(widget, row, 1)
        return widget

    def _create_varios_fields(self):
        self.varios_group = QWidget()
        layout = QGridLayout(self.varios_group)
        layout.setContentsMargins(0, 15, 0, 0)
        layout.setSpacing(10)
        
        self.codigo_barras_input = QLineEdit()
        layout.addWidget(StyledLabel("Código de Barras:"), 0, 0)
        layout.addWidget(self.codigo_barras_input, 0, 1)

        self.categoria_input = QLineEdit("General")
        layout.addWidget(StyledLabel("Categoría:"), 1, 0)
        layout.addWidget(self.categoria_input, 1, 1)

        self.peso_gr_input = QLineEdit()
        layout.addWidget(StyledLabel("Peso (gramos):"), 2, 0)
        layout.addWidget(self.peso_gr_input, 2, 1)

        self.refrigeracion_check = QCheckBox("Requiere Refrigeración")
        layout.addWidget(self.refrigeracion_check, 3, 1)

    def _create_suplementos_fields(self):
        self.suplementos_group = QWidget()
        layout = QGridLayout(self.suplementos_group)
        layout.setContentsMargins(0, 15, 0, 0)
        layout.setSpacing(10)

        self.marca_input = QLineEdit()
        layout.addWidget(StyledLabel("Marca*:"), 0, 0)
        layout.addWidget(self.marca_input, 0, 1)

        self.tipo_suplemento_combo = QComboBox()
        self.tipo_suplemento_combo.addItems([
            "Proteína", "Creatina", "Pre-entreno", "Post-entreno", "BCAA", 
            "Glutamina", "Vitaminas", "Aminoácidos", "Quemador", 
            "Ganador de Masa", "Otro"
        ])
        layout.addWidget(StyledLabel("Tipo de Suplemento*:"), 1, 0)
        layout.addWidget(self.tipo_suplemento_combo, 1, 1)

        self.sabor_input = QLineEdit()
        layout.addWidget(StyledLabel("Sabor:"), 2, 0)
        layout.addWidget(self.sabor_input, 2, 1)

        self.presentacion_input = QLineEdit()
        layout.addWidget(StyledLabel("Presentación:"), 3, 0)
        layout.addWidget(self.presentacion_input, 3, 1)

        self.peso_neto_input = QLineEdit()
        layout.addWidget(StyledLabel("Peso Neto (gramos):"), 4, 0)
        layout.addWidget(self.peso_neto_input, 4, 1)

        self.porciones_input = QLineEdit()
        layout.addWidget(StyledLabel("Porciones Totales:"), 5, 0)
        layout.addWidget(self.porciones_input, 5, 1)

        self.calorias_input = QLineEdit()
        layout.addWidget(StyledLabel("Calorías por porción:"), 6, 0)
        layout.addWidget(self.calorias_input, 6, 1)

        self.proteina_input = QLineEdit()
        layout.addWidget(StyledLabel("Proteína por porción (gr):"), 7, 0)
        layout.addWidget(self.proteina_input, 7, 1)

        self.fecha_vencimiento_input = QDateEdit()
        self.fecha_vencimiento_input.setCalendarPopup(True)
        self.fecha_vencimiento_input.setDisplayFormat("yyyy-MM-dd")
        layout.addWidget(StyledLabel("Fecha de Vencimiento:"), 8, 0)
        layout.addWidget(self.fecha_vencimiento_input, 8, 1)

    def _toggle_product_fields(self):
        is_suplemento = self.tipo_producto_combo.currentText() == "Suplemento"
        self.suplementos_group.setVisible(is_suplemento)
        self.varios_group.setVisible(not is_suplemento)

    def _clear_form(self):
        # Limpiar campos comunes
        self.codigo_interno_input.clear()
        self.nombre_input.clear()
        self.descripcion_input.clear()
        self.precio_venta_input.clear()
        self.activo_check.setChecked(True)

        # Limpiar campos de productos varios
        self.codigo_barras_input.clear()
        self.categoria_input.setText("General")
        self.peso_gr_input.clear()
        self.refrigeracion_check.setChecked(False)

        # Limpiar campos de suplementos
        self.marca_input.clear()
        self.tipo_suplemento_combo.setCurrentIndex(0)
        self.sabor_input.clear()
        self.presentacion_input.clear()
        self.peso_neto_input.clear()
        self.porciones_input.clear()
        self.calorias_input.clear()
        self.proteina_input.clear()
        self.fecha_vencimiento_input.setDate(QDate.currentDate())

    def _save_product(self):
        """Valida y guarda el nuevo producto en la base de datos."""
        try:
            codigo_interno = self.codigo_interno_input.text().strip().upper()
            nombre = self.nombre_input.text().strip()
            precio_venta_str = self.precio_venta_input.text().strip()

            if not codigo_interno or not nombre or not precio_venta_str:
                show_error_dialog(self, "Error de Validación", "Los campos con * son obligatorios.")
                return

            try:
                precio_venta = float(precio_venta_str)
                if precio_venta <= 0:
                    raise ValueError()
            except ValueError:
                show_error_dialog(self, "Error de Validación", "El precio de venta debe ser un número positivo.")
                return

            if self.db_manager.check_codigo_interno_exists(codigo_interno):
                show_error_dialog(self, "Error de Duplicado", f"El código interno '{codigo_interno}' ya existe.")
                return

            is_suplemento = self.tipo_producto_combo.currentText() == "Suplemento"

            if is_suplemento:
                self._save_suplemento(codigo_interno, nombre, precio_venta)
            else:
                self._save_producto_varios(codigo_interno, nombre, precio_venta)

        except Exception as e:
            logging.error(f"Error al guardar producto: {e}")
            show_error_dialog(self, "Error Inesperado", f"Ocurrió un error al guardar:\n{e}")

    def _save_producto_varios(self, codigo_interno, nombre, precio_venta):
        """Guarda un producto de tipo 'Varios'."""
        producto_data = {
            'codigo_interno': codigo_interno,
            'nombre': nombre,
            'descripcion': self.descripcion_input.toPlainText().strip(),
            'precio_venta': precio_venta,
            'activo': self.activo_check.isChecked(),
            'codigo_barras': self.codigo_barras_input.text().strip() or None,
            'categoria': self.categoria_input.text().strip(),
            'peso_gr': float(self.peso_gr_input.text()) if self.peso_gr_input.text() else None,
            'requiere_refrigeracion': self.refrigeracion_check.isChecked()
        }
        
        self.db_manager.insertar_producto_varios(producto_data)
        self._create_inventory_record(codigo_interno, 'varios')
        
        show_success_dialog(self, "Éxito", f"Producto '{nombre}' guardado correctamente.")
        self._clear_form()
        self.producto_guardado.emit()

    def _save_suplemento(self, codigo_interno, nombre, precio_venta):
        """Guarda un producto de tipo 'Suplemento'."""
        marca = self.marca_input.text().strip()
        if not marca:
            show_error_dialog(self, "Error de Validación", "La marca es obligatoria para los suplementos.")
            return

        suplemento_data = {
            'codigo_interno': codigo_interno,
            'nombre': nombre,
            'descripcion': self.descripcion_input.toPlainText().strip(),
            'precio_venta': precio_venta,
            'activo': self.activo_check.isChecked(),
            'marca': marca,
            'tipo': self.tipo_suplemento_combo.currentText(),
            'sabor': self.sabor_input.text().strip() or None,
            'presentacion': self.presentacion_input.text().strip() or None,
            'peso_neto_gr': float(self.peso_neto_input.text()) if self.peso_neto_input.text() else None,
            'porciones_totales': int(self.porciones_input.text()) if self.porciones_input.text() else None,
            'calorias_por_porcion': float(self.calorias_input.text()) if self.calorias_input.text() else None,
            'proteina_por_porcion_gr': float(self.proteina_input.text()) if self.proteina_input.text() else None,
            'fecha_vencimiento': self.fecha_vencimiento_input.date().toString("yyyy-MM-dd")
        }

        self.db_manager.insertar_suplemento(suplemento_data)
        self._create_inventory_record(codigo_interno, 'suplemento')

        show_success_dialog(self, "Éxito", f"Suplemento '{nombre}' guardado correctamente.")
        self._clear_form()
        self.producto_guardado.emit()

    def _create_inventory_record(self, codigo_interno, tipo_producto):
        """Crea el registro de inventario para el nuevo producto."""
        inventario_data = {
            'codigo_interno': codigo_interno,
            'tipo_producto': tipo_producto,
            'stock_actual': 0,
            'stock_minimo': 5 if tipo_producto == 'varios' else 2,
            'ubicacion': 'Recepción'
        }
        self.db_manager.crear_inventario(inventario_data)
