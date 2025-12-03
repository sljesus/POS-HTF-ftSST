"""
Ventana de Administración de Ubicaciones de Almacenamiento
Permite agregar, editar y eliminar ubicaciones del catálogo
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem,
    QCheckBox, QMessageBox, QScrollArea, QFrame,
    QLabel, QDialog, QPushButton
)
from PySide6.QtCore import Qt, Signal, QSize
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
    show_confirmation_dialog,
    StyledLabel
)


class UbicacionesWindow(QWidget):
    """Ventana para administrar ubicaciones de almacenamiento"""
    
    cerrar_solicitado = Signal()
    
    def __init__(self, pg_manager, user_data, parent=None):
        super().__init__(parent)
        self.pg_manager = pg_manager
        self.user_data = user_data
        self.ubicaciones = []
        
        self.setup_ui()
        self.cargar_ubicaciones()
    
    def setup_ui(self):
        """Configurar interfaz"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Contenido principal con scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        content = QWidget()
        content_layout = create_page_layout("ADMINISTRACIÓN DE UBICACIONES")
        content.setLayout(content_layout)
        
        # Panel de tabla
        table_panel = ContentPanel()
        table_layout = QVBoxLayout(table_panel)
        table_layout.setContentsMargins(20, 20, 20, 20)
        table_layout.setSpacing(15)
        
        # Tabla de ubicaciones
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Descripción", "Activa"])
        self.table.setMinimumHeight(400)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: white;
                gridline-color: {WindowsPhoneTheme.PRIMARY_BLUE};
                border: 1px solid {WindowsPhoneTheme.PRIMARY_BLUE};
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {WindowsPhoneTheme.LIGHT_GRAY};
            }}
            QHeaderView::section {{
                background-color: {WindowsPhoneTheme.PRIMARY_BLUE};
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }}
        """)
        
        # Configurar columnas
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 250)
        self.table.setColumnWidth(3, 80)
        
        self.table.itemSelectionChanged.connect(self.on_seleccion_cambio)
        
        table_layout.addWidget(self.table)
        content_layout.addWidget(table_panel)
        
        # Panel de formulario
        form_panel = ContentPanel()
        form_layout = QVBoxLayout(form_panel)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)
        
        form_title = SectionTitle("NUEVA UBICACIÓN / EDITAR")
        form_layout.addWidget(form_title)
        
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Nombre
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Ej: Bodega Principal")
        self.nombre_input.setMinimumHeight(40)
        form.addRow("Nombre *:", self.nombre_input)
        
        # Descripción
        self.descripcion_input = QTextEdit()
        self.descripcion_input.setPlaceholderText("Descripción de la ubicación (opcional)")
        self.descripcion_input.setMaximumHeight(80)
        form.addRow("Descripción:", self.descripcion_input)
        
        # Activa
        self.activa_check = QCheckBox("Ubicación activa")
        self.activa_check.setChecked(True)
        form.addRow("Estado:", self.activa_check)
        
        form_layout.addLayout(form)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        btn_guardar = TileButton("Guardar", "fa5s.save", WindowsPhoneTheme.TILE_GREEN)
        btn_guardar.setMaximumWidth(150)
        btn_guardar.clicked.connect(self.guardar_ubicacion)
        buttons_layout.addWidget(btn_guardar)
        
        btn_limpiar = TileButton("Limpiar", "fa5s.eraser", WindowsPhoneTheme.TILE_BLUE)
        btn_limpiar.setMaximumWidth(150)
        btn_limpiar.clicked.connect(self.limpiar_formulario)
        buttons_layout.addWidget(btn_limpiar)
        
        btn_eliminar = TileButton("Eliminar", "fa5s.trash", WindowsPhoneTheme.TILE_RED)
        btn_eliminar.setMaximumWidth(150)
        btn_eliminar.clicked.connect(self.eliminar_ubicacion)
        buttons_layout.addWidget(btn_eliminar)
        
        buttons_layout.addStretch()
        form_layout.addLayout(buttons_layout)
        
        content_layout.addWidget(form_panel)
        content_layout.addStretch()
        
        # Botón de cerrar
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        # Footer con botón cerrar
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(20, 10, 20, 10)
        btn_cerrar = TileButton("Volver", "fa5s.arrow-left", WindowsPhoneTheme.TILE_GRAY)
        btn_cerrar.setMaximumWidth(150)
        btn_cerrar.clicked.connect(self.cerrar_solicitado.emit)
        footer_layout.addStretch()
        footer_layout.addWidget(btn_cerrar)
        layout.addLayout(footer_layout)
    
    def cargar_ubicaciones(self):
        """Cargar ubicaciones desde la base de datos"""
        try:
            with self.pg_manager.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id_ubicacion, nombre, descripcion, activa
                    FROM ca_ubicaciones
                    ORDER BY nombre
                """)
                
                self.ubicaciones = cursor.fetchall()
                self.actualizar_tabla()
                
                logging.info(f"Cargadas {len(self.ubicaciones)} ubicaciones")
                
        except Exception as e:
            logging.error(f"Error cargando ubicaciones: {e}")
            show_error_dialog(self, "Error", "No se pudieron cargar las ubicaciones")
    
    def actualizar_tabla(self):
        """Actualizar tabla con ubicaciones"""
        self.table.setRowCount(0)
        
        for i, ubicacion in enumerate(self.ubicaciones):
            self.table.insertRow(i)
            
            # ID
            id_item = QTableWidgetItem(str(ubicacion['id_ubicacion']))
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(i, 0, id_item)
            
            # Nombre
            nombre_item = QTableWidgetItem(ubicacion['nombre'])
            nombre_item.setFlags(nombre_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(i, 1, nombre_item)
            
            # Descripción
            desc_item = QTableWidgetItem(ubicacion['descripcion'] or "")
            desc_item.setFlags(desc_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(i, 2, desc_item)
            
            # Activa
            activa_item = QTableWidgetItem("✓" if ubicacion['activa'] else "✗")
            activa_item.setFlags(activa_item.flags() & ~Qt.ItemIsEditable)
            activa_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 3, activa_item)
    
    def on_seleccion_cambio(self):
        """Cuando cambia la selección en la tabla"""
        selected_rows = self.table.selectedIndexes()
        
        if selected_rows:
            row = selected_rows[0].row()
            ubicacion = self.ubicaciones[row]
            
            # Cargar datos en formulario
            self.nombre_input.setText(ubicacion['nombre'])
            self.descripcion_input.setPlainText(ubicacion['descripcion'] or "")
            self.activa_check.setChecked(ubicacion['activa'])
            
            logging.info(f"Ubicación seleccionada: {ubicacion['nombre']}")
    
    def guardar_ubicacion(self):
        """Guardar o actualizar ubicación"""
        try:
            nombre = self.nombre_input.text().strip()
            descripcion = self.descripcion_input.toPlainText().strip() or None
            activa = self.activa_check.isChecked()
            
            # Validar
            if not nombre:
                show_warning_dialog(self, "Validación", "Debe ingresar un nombre para la ubicación")
                self.nombre_input.setFocus()
                return
            
            if len(nombre) < 3:
                show_warning_dialog(self, "Validación", "El nombre debe tener al menos 3 caracteres")
                self.nombre_input.setFocus()
                return
            
            selected_rows = self.table.selectedIndexes()
            
            with self.pg_manager.connection.cursor() as cursor:
                if selected_rows:
                    # Actualizar
                    row = selected_rows[0].row()
                    id_ubicacion = self.ubicaciones[row]['id_ubicacion']
                    
                    cursor.execute("""
                        UPDATE ca_ubicaciones
                        SET nombre = %s, descripcion = %s, activa = %s
                        WHERE id_ubicacion = %s
                    """, (nombre, descripcion, activa, id_ubicacion))
                    
                    msg_tipo = "actualizada"
                else:
                    # Crear nueva
                    cursor.execute("""
                        INSERT INTO ca_ubicaciones (nombre, descripcion, activa)
                        VALUES (%s, %s, %s)
                    """, (nombre, descripcion, activa))
                    
                    msg_tipo = "creada"
                
                self.pg_manager.connection.commit()
                
                show_info_dialog(
                    self,
                    "Éxito",
                    f"Ubicación {msg_tipo} correctamente: {nombre}"
                )
                
                self.limpiar_formulario()
                self.cargar_ubicaciones()
                
                logging.info(f"Ubicación {msg_tipo}: {nombre}")
                
        except Exception as e:
            logging.error(f"Error guardando ubicación: {e}")
            show_error_dialog(self, "Error", "No se pudo guardar la ubicación")
            self.pg_manager.connection.rollback()
    
    def eliminar_ubicacion(self):
        """Eliminar ubicación seleccionada"""
        selected_rows = self.table.selectedIndexes()
        
        if not selected_rows:
            show_warning_dialog(self, "Selección requerida", "Debe seleccionar una ubicación para eliminar")
            return
        
        row = selected_rows[0].row()
        ubicacion = self.ubicaciones[row]
        
        # Confirmar eliminación
        if not show_confirmation_dialog(
            self,
            "Confirmar eliminación",
            f"¿Desea eliminar la ubicación '{ubicacion['nombre']}'?",
            "Esta acción no se puede deshacer."
        ):
            return
        
        try:
            with self.pg_manager.connection.cursor() as cursor:
                # Verificar si se puede eliminar (sin productos)
                cursor.execute("""
                    SELECT COUNT(*) as count
                    FROM inventario
                    WHERE id_ubicacion = %s
                """, (ubicacion['id_ubicacion'],))
                
                result = cursor.fetchone()
                if result['count'] > 0:
                    show_warning_dialog(
                        self,
                        "No se puede eliminar",
                        f"La ubicación '{ubicacion['nombre']}' tiene {result['count']} productos asociados.\n"
                        "Primero debe reubicar los productos."
                    )
                    return
                
                # Eliminar
                cursor.execute("""
                    DELETE FROM ca_ubicaciones
                    WHERE id_ubicacion = %s
                """, (ubicacion['id_ubicacion'],))
                
                self.pg_manager.connection.commit()
                
                show_info_dialog(
                    self,
                    "Éxito",
                    f"Ubicación '{ubicacion['nombre']}' eliminada correctamente"
                )
                
                self.limpiar_formulario()
                self.cargar_ubicaciones()
                
                logging.info(f"Ubicación eliminada: {ubicacion['nombre']}")
                
        except Exception as e:
            logging.error(f"Error eliminando ubicación: {e}")
            show_error_dialog(self, "Error", "No se pudo eliminar la ubicación")
            self.pg_manager.connection.rollback()
    
    def limpiar_formulario(self):
        """Limpiar formulario"""
        self.nombre_input.clear()
        self.descripcion_input.clear()
        self.activa_check.setChecked(True)
        self.table.clearSelection()
        self.nombre_input.setFocus()
        logging.info("Formulario limpiado")
