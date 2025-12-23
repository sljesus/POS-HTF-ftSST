"""
Componente de Grid Editable para Catálogo de Productos
Permite editar información de suplementos y productos varios
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QTabWidget, QSizePolicy, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush
import logging

from ui.components import WindowsPhoneTheme, TileButton, StyledLabel, show_info_dialog, show_warning_dialog, show_error_dialog, create_page_layout, ContentPanel


class EditableCatalogGrid(QWidget):
    """Widget con grid editable para catálogo de productos"""
    
    catalogo_actualizado = Signal()
    
    def __init__(self, postgres_manager, parent=None):
        super().__init__(parent)
        self.pg_manager = postgres_manager
        self.productos_varios = []
        self.suplementos = []
        self.cambios_pendientes = {}  # {codigo_interno: {campo: valor_nuevo, ...}}
        
        self.setup_ui()
        self.cargar_datos()
    
    def setup_ui(self):
        """Configurar interfaz del grid editable"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        content = QWidget()
        content_layout = create_page_layout("CATÁLOGO DE PRODUCTOS - EDICIÓN")
        content.setLayout(content_layout)
        
        # Panel de información
        info_panel = ContentPanel()
        info_layout = QHBoxLayout(info_panel)
        info_label = StyledLabel("Seleccione productos para editar. Los cambios se guardarán en la base de datos.", 
                                 size=WindowsPhoneTheme.FONT_SIZE_SMALL)
        info_layout.addWidget(info_label, stretch=1)
        content_layout.addWidget(info_panel)
        
        # Tabs para tipos de productos
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {WindowsPhoneTheme.BORDER_COLOR};
            }}
            QTabBar::tab {{
                background-color: {WindowsPhoneTheme.BG_LIGHT};
                color: {WindowsPhoneTheme.TEXT_PRIMARY};
                padding: 8px 16px;
                border: 1px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-bottom: none;
            }}
            QTabBar::tab:selected {{
                background-color: white;
                border-bottom: 2px solid {WindowsPhoneTheme.TILE_BLUE};
            }}
            QTabBar::tab:hover {{
                background-color: #f0f0f0;
            }}
        """)
        
        # Tab Productos Varios
        self.tab_varios = QWidget()
        tab_varios_layout = QVBoxLayout(self.tab_varios)
        tab_varios_layout.setContentsMargins(0, 0, 0, 0)
        self.tabla_varios = self.crear_tabla_productos_varios()
        tab_varios_layout.addWidget(self.tabla_varios)
        self.tab_widget.addTab(self.tab_varios, "Productos Varios")
        
        # Tab Suplementos
        self.tab_suplementos = QWidget()
        tab_suplementos_layout = QVBoxLayout(self.tab_suplementos)
        tab_suplementos_layout.setContentsMargins(0, 0, 0, 0)
        self.tabla_suplementos = self.crear_tabla_suplementos()
        tab_suplementos_layout.addWidget(self.tabla_suplementos)
        self.tab_widget.addTab(self.tab_suplementos, "Suplementos")
        
        # Panel con tabla
        table_panel = ContentPanel()
        table_layout = QVBoxLayout(table_panel)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.addWidget(self.tab_widget)
        content_layout.addWidget(table_panel)
        
        # Panel de información de cambios
        info_cambios_panel = ContentPanel()
        info_cambios_layout = QHBoxLayout(info_cambios_panel)
        
        self.label_cambios = StyledLabel("", size=WindowsPhoneTheme.FONT_SIZE_SMALL)
        self.label_cambios.setStyleSheet(f"color: {WindowsPhoneTheme.TILE_ORANGE}; font-weight: bold;")
        info_cambios_layout.addWidget(self.label_cambios, stretch=1)
        
        content_layout.addWidget(info_cambios_panel)
        
        # Panel de botones
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(WindowsPhoneTheme.TILE_SPACING)
        
        btn_guardar = TileButton("Guardar Cambios", "fa5s.save", WindowsPhoneTheme.TILE_GREEN)
        btn_guardar.clicked.connect(self.guardar_cambios)
        botones_layout.addWidget(btn_guardar)
        
        btn_descartar = TileButton("Descartar", "fa5s.undo", WindowsPhoneTheme.TILE_ORANGE)
        btn_descartar.clicked.connect(self.descartar_cambios)
        botones_layout.addWidget(btn_descartar)
        
        btn_recargar = TileButton("Recargar", "fa5s.sync", WindowsPhoneTheme.TILE_BLUE)
        btn_recargar.clicked.connect(self.cargar_datos)
        botones_layout.addWidget(btn_recargar)
        
        content_layout.addLayout(botones_layout)
        
        layout.addWidget(content)
    
    def crear_tabla_productos_varios(self):
        """Crear tabla editable para productos varios"""
        tabla = QTableWidget()
        tabla.setColumnCount(7)
        tabla.setHorizontalHeaderLabels([
            "Código", "Nombre", "Descripción", "Precio", "Categoría", "Código Barras", "Activo"
        ])
        
        # Configurar header
        header = tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        
        tabla.verticalHeader().setVisible(False)
        tabla.verticalHeader().setDefaultSectionSize(60)
        tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        tabla.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        tabla.setAlternatingRowColors(True)
        tabla.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Aplicar estilos
        tabla.setStyleSheet(f"""
            QTableWidget {{
                background-color: white;
                border: none;
                gridline-color: #e5e7eb;
            }}
            QTableWidget::item {{
                padding: 10px;
                border-bottom: 1px solid #e5e7eb;
            }}
            QTableWidget::item:selected {{
                background-color: {WindowsPhoneTheme.TILE_BLUE};
                color: white;
            }}
            QHeaderView::section {{
                background-color: {WindowsPhoneTheme.BG_LIGHT};
                color: {WindowsPhoneTheme.PRIMARY_BLUE};
                padding: 10px 6px;
                border: none;
                border-bottom: 2px solid {WindowsPhoneTheme.TILE_BLUE};
                font-weight: bold;
                font-family: '{WindowsPhoneTheme.FONT_FAMILY}';
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
            }}
        """)
        
        tabla.itemChanged.connect(self.on_item_changed)
        
        return tabla
    
    def crear_tabla_suplementos(self):
        """Crear tabla editable para suplementos"""
        tabla = QTableWidget()
        tabla.setColumnCount(7)
        tabla.setHorizontalHeaderLabels([
            "Código", "Nombre", "Marca", "Tipo", "Precio", "Código Barras", "Activo"
        ])
        
        # Configurar header
        header = tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        
        tabla.verticalHeader().setVisible(False)
        tabla.verticalHeader().setDefaultSectionSize(60)
        tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        tabla.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        tabla.setAlternatingRowColors(True)
        tabla.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Aplicar estilos
        tabla.setStyleSheet(f"""
            QTableWidget {{
                background-color: white;
                border: none;
                gridline-color: #e5e7eb;
            }}
            QTableWidget::item {{
                padding: 10px;
                border-bottom: 1px solid #e5e7eb;
            }}
            QTableWidget::item:selected {{
                background-color: {WindowsPhoneTheme.TILE_BLUE};
                color: white;
            }}
            QHeaderView::section {{
                background-color: {WindowsPhoneTheme.BG_LIGHT};
                color: {WindowsPhoneTheme.PRIMARY_BLUE};
                padding: 10px 6px;
                border: none;
                border-bottom: 2px solid {WindowsPhoneTheme.TILE_BLUE};
                font-weight: bold;
                font-family: '{WindowsPhoneTheme.FONT_FAMILY}';
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
            }}
        """)
        
        tabla.itemChanged.connect(self.on_item_changed)
        
        return tabla
    
    def cargar_datos(self):
        """Cargar datos de productos desde la base de datos"""
        try:
            logging.info("Cargando catálogo de productos...")
            
            # Obtener productos varios
            response_varios = self.pg_manager.client.table('ca_productos_varios').select('*').execute()
            self.productos_varios = response_varios.data or []
            
            # Obtener suplementos
            response_suplementos = self.pg_manager.client.table('ca_suplementos').select('*').execute()
            self.suplementos = response_suplementos.data or []
            
            # Poblar tablas
            self.poblar_tabla_productos_varios()
            self.poblar_tabla_suplementos()
            
            self.cambios_pendientes = {}
            self.actualizar_label_cambios()
            
            logging.info(f"Catálogo cargado: {len(self.productos_varios)} productos varios, {len(self.suplementos)} suplementos")
            
        except Exception as e:
            logging.error(f"Error cargando catálogo: {e}")
            show_error_dialog(self, "Error al cargar", "No se pudo cargar el catálogo de productos", detail=str(e))
    
    def poblar_tabla_productos_varios(self):
        """Poblar tabla de productos varios"""
        tabla = self.tabla_varios
        tabla.setRowCount(0)
        
        for row, producto in enumerate(self.productos_varios):
            tabla.insertRow(row)
            
            # Código (no editable)
            item_codigo = QTableWidgetItem(str(producto.get('codigo_interno', '')))
            item_codigo.setFlags(item_codigo.flags() & ~Qt.ItemFlag.ItemIsEditable)
            tabla.setItem(row, 0, item_codigo)
            
            # Nombre (editable)
            tabla.setItem(row, 1, QTableWidgetItem(str(producto.get('nombre', ''))))
            
            # Descripción (editable)
            tabla.setItem(row, 2, QTableWidgetItem(str(producto.get('descripcion', ''))))
            
            # Precio (editable)
            item_precio = QTableWidgetItem(f"{float(producto.get('precio_venta', 0)):.2f}")
            tabla.setItem(row, 3, item_precio)
            
            # Categoría (editable)
            tabla.setItem(row, 4, QTableWidgetItem(str(producto.get('categoria', ''))))
            
            # Código Barras (editable)
            tabla.setItem(row, 5, QTableWidgetItem(str(producto.get('codigo_barras', '') or '')))
            
            # Activo (editable)
            item_activo = QTableWidgetItem("Sí" if producto.get('activo', True) else "No")
            tabla.setItem(row, 6, item_activo)
    
    def poblar_tabla_suplementos(self):
        """Poblar tabla de suplementos"""
        tabla = self.tabla_suplementos
        tabla.setRowCount(0)
        
        for row, suplemento in enumerate(self.suplementos):
            tabla.insertRow(row)
            
            # Código (no editable)
            item_codigo = QTableWidgetItem(str(suplemento.get('codigo_interno', '')))
            item_codigo.setFlags(item_codigo.flags() & ~Qt.ItemFlag.ItemIsEditable)
            tabla.setItem(row, 0, item_codigo)
            
            # Nombre (editable)
            tabla.setItem(row, 1, QTableWidgetItem(str(suplemento.get('nombre', ''))))
            
            # Marca (editable)
            tabla.setItem(row, 2, QTableWidgetItem(str(suplemento.get('marca', ''))))
            
            # Tipo (editable)
            tabla.setItem(row, 3, QTableWidgetItem(str(suplemento.get('tipo', ''))))
            
            # Precio (editable)
            item_precio = QTableWidgetItem(f"{float(suplemento.get('precio_venta', 0)):.2f}")
            tabla.setItem(row, 4, item_precio)
            
            # Código Barras (editable)
            tabla.setItem(row, 5, QTableWidgetItem(str(suplemento.get('codigo_barras', '') or '')))
            
            # Activo (editable)
            item_activo = QTableWidgetItem("Sí" if suplemento.get('activo', True) else "No")
            tabla.setItem(row, 6, item_activo)
    
    def on_item_changed(self, item):
        """Manejar cambio en un item de la tabla"""
        # Obtener código del producto
        tabla = self.tabla_varios if self.tab_widget.currentIndex() == 0 else self.tabla_suplementos
        row = item.row()
        codigo_item = tabla.item(row, 0)
        
        if codigo_item:
            codigo = codigo_item.text()
            col = item.column()
            
            # Determinar el nombre del campo según la tabla
            if self.tab_widget.currentIndex() == 0:  # Productos varios
                campos = ['codigo_interno', 'nombre', 'descripcion', 'precio_venta', 'categoria', 'codigo_barras', 'activo']
            else:  # Suplementos
                campos = ['codigo_interno', 'nombre', 'marca', 'tipo', 'precio_venta', 'codigo_barras', 'activo']
            
            if col < len(campos):
                campo = campos[col]
                
                # No registrar cambios en código
                if campo == 'codigo_interno':
                    return
                
                # Inicializar entrada si no existe
                if codigo not in self.cambios_pendientes:
                    self.cambios_pendientes[codigo] = {}
                
                valor = item.text()
                
                # Resaltar celda modificada
                item.setBackground(QBrush(QColor("#fff3cd")))
                
                self.cambios_pendientes[codigo][campo] = valor
                self.actualizar_label_cambios()
    
    def actualizar_label_cambios(self):
        """Actualizar etiqueta de cambios pendientes"""
        total_cambios = sum(len(v) for v in self.cambios_pendientes.values())
        if total_cambios > 0:
            self.label_cambios.setText(f"[!] {total_cambios} cambios pendientes de guardar")
            self.label_cambios.setStyleSheet("color: #ff8c00; font-weight: bold;")
        else:
            self.label_cambios.setText("")
            self.label_cambios.setStyleSheet("")
    
    def guardar_cambios(self):
        """Guardar cambios en la base de datos"""
        if not self.cambios_pendientes:
            show_info_dialog(self, "Sin cambios", "No hay cambios pendientes para guardar")
            return
        
        try:
            total_guardados = 0
            errores = []
            
            for codigo, cambios in self.cambios_pendientes.items():
                try:
                    # Determinar si es producto varios o suplemento
                    es_producto_varios = any(p.get('codigo_interno') == codigo for p in self.productos_varios)
                    tabla_nombre = 'ca_productos_varios' if es_producto_varios else 'ca_suplementos'
                    
                    # Convertir valores booleanos
                    for campo in ['activo']:
                        if campo in cambios:
                            cambios[campo] = cambios[campo].lower() in ['sí', 'si', 'true', '1']
                    
                    # Convertir precio a float
                    if 'precio_venta' in cambios:
                        cambios['precio_venta'] = float(cambios['precio_venta'])
                    
                    # Actualizar en base de datos
                    self.pg_manager.client.table(tabla_nombre).update(cambios).eq('codigo_interno', codigo).execute()
                    total_guardados += 1
                    
                except Exception as e:
                    errores.append(f"{codigo}: {str(e)}")
                    logging.error(f"Error actualizando {codigo}: {e}")
            
            # Limpiar cambios y recargar
            self.cambios_pendientes = {}
            self.actualizar_label_cambios()
            self.cargar_datos()
            
            mensaje = f"Se guardaron {total_guardados} productos"
            if errores:
                mensaje += f"\n\nErrores:\n" + "\n".join(errores)
                show_warning_dialog(self, "Guardado parcial", mensaje)
            else:
                show_info_dialog(self, "Éxito", mensaje)
            
            self.catalogo_actualizado.emit()
            logging.info(f"Cambios guardados: {total_guardados} productos actualizados")
            
        except Exception as e:
            logging.error(f"Error guardando cambios: {e}")
            show_error_dialog(self, "Error al guardar", "No se pudieron guardar los cambios", detail=str(e))
    
    def descartar_cambios(self):
        """Descartar cambios pendientes"""
        if not self.cambios_pendientes:
            return
        
        reply = QMessageBox.question(
            self,
            "Confirmar",
            "¿Descartar todos los cambios pendientes?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.cambios_pendientes = {}
            self.cargar_datos()
