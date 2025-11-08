"""
Ventana de Nueva Venta para HTF POS
Usando componentes reutilizables del sistema de diseño
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QTableWidget, QTableWidgetItem,
    QGridLayout, QSpinBox,
    QHeaderView, QSizePolicy, QPushButton,
    QDialog, QLabel, QTextEdit,
    QFrame
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QCursor
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
import logging
from datetime import datetime

# Importar componentes del sistema de diseño
from ui.components import (
    WindowsPhoneTheme,
    TileButton,
    InfoTile,
    SectionTitle,
    ContentPanel,
    SearchBar,
    StyledLabel,
    show_info_dialog,
    show_success_dialog,
    show_warning_dialog,
    show_error_dialog,
    show_confirmation_dialog
)


class NuevaVentaWindow(QWidget):
    """Widget para realizar nueva venta"""
    
    venta_completada = Signal(dict)
    cerrar_solicitado = Signal()
    
    def __init__(self, db_manager, supabase_service, user_data, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.supabase_service = supabase_service
        self.user_data = user_data
        
        # Configurar política de tamaño
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Variables de venta
        self.carrito = []
        self.total_venta = 0.0
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar interfaz de nueva venta"""
        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(WindowsPhoneTheme.MARGIN_MEDIUM,
                                       WindowsPhoneTheme.MARGIN_MEDIUM,
                                       WindowsPhoneTheme.MARGIN_MEDIUM,
                                       WindowsPhoneTheme.MARGIN_MEDIUM)
        root_layout.setSpacing(WindowsPhoneTheme.MARGIN_MEDIUM)

        productos_panel = self._build_products_panel()
        carrito_panel = self._build_cart_panel()

        root_layout.addWidget(productos_panel, 3)
        root_layout.addWidget(carrito_panel, 2)

    def _build_products_panel(self):
        """Construir panel con buscador, catálogo y total."""
        panel = ContentPanel()
        panel.setMinimumWidth(600)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(WindowsPhoneTheme.MARGIN_SMALL,
                                  WindowsPhoneTheme.MARGIN_SMALL,
                                  WindowsPhoneTheme.MARGIN_SMALL,
                                  WindowsPhoneTheme.MARGIN_SMALL)
        layout.setSpacing(WindowsPhoneTheme.MARGIN_SMALL)

        layout.addWidget(SectionTitle("PRODUCTOS"))

        self.search_bar = SearchBar("Buscar producto por código o nombre...")
        self.search_bar.connect_search(self.buscar_productos)
        layout.addWidget(self.search_bar)

        self.productos_table = QTableWidget()
        self.productos_table.setColumnCount(5)
        self.productos_table.setHorizontalHeaderLabels([
            "Código", "Nombre", "Precio", "Stock", "Acción"
        ])
        header = self.productos_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.resizeSection(4, 56)

        self.productos_table.verticalHeader().setVisible(False)
        self.productos_table.setSelectionMode(QTableWidget.NoSelection)
        self.productos_table.setFocusPolicy(Qt.NoFocus)
        self.productos_table.setAlternatingRowColors(True)
        self.productos_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.productos_table.setStyleSheet(
            """
            QTableView::item:hover {
                background-color: rgba(30, 58, 138, 0.08);
                color: black;
            }
            QTableView::item:selected {
                background-color: rgba(30, 58, 138, 0.15);
                color: black;
            }
            """
        )

        layout.addWidget(self.productos_table, 1)

        self.cargar_productos()

        total_tile = InfoTile("TOTAL A PAGAR", None, WindowsPhoneTheme.TILE_GREEN)
        total_tile.main_layout.insertStretch(0)
        self.total_label = total_tile.add_main_value("$0.00")
        total_tile.add_stretch()
        layout.addWidget(total_tile)

        return panel

    def _build_cart_panel(self):
        """Construir panel con carrito y acciones."""
        panel = ContentPanel()
        panel.setMinimumWidth(420)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(WindowsPhoneTheme.MARGIN_SMALL,
                                  WindowsPhoneTheme.MARGIN_SMALL,
                                  WindowsPhoneTheme.MARGIN_SMALL,
                                  WindowsPhoneTheme.MARGIN_SMALL)
        layout.setSpacing(WindowsPhoneTheme.MARGIN_SMALL)

        layout.addWidget(SectionTitle("CARRITO DE COMPRAS"))

        self.carrito_table = QTableWidget()
        self.carrito_table.setColumnCount(5)
        self.carrito_table.setHorizontalHeaderLabels([
            "Producto", "Precio", "Cant.", "Subtotal", "Quitar"
        ])
        header = self.carrito_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.resizeSection(4, 56)

        self.carrito_table.verticalHeader().setVisible(False)
        self.carrito_table.setSelectionMode(QTableWidget.NoSelection)
        self.carrito_table.setFocusPolicy(Qt.NoFocus)
        self.carrito_table.setAlternatingRowColors(True)
        self.carrito_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.carrito_table.setStyleSheet(
            """
            QTableView::item:hover {
                background-color: rgba(30, 58, 138, 0.08);
            }
            QTableView::item:selected {
                background-color: rgba(30, 58, 138, 0.15);
            }
            """
        )

        layout.addWidget(self.carrito_table, 1)

        buttons_container = self._build_action_buttons()
        layout.addWidget(buttons_container)
        layout.setStretch(0, 0)
        layout.setStretch(1, 1)

        return panel

    def _build_action_buttons(self):
        """Crear panel con botones Tile responsivos."""
        container = QWidget()
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        max_height = WindowsPhoneTheme.TILE_MIN_HEIGHT * 2 + WindowsPhoneTheme.TILE_SPACING
        container.setMaximumHeight(max_height)

        layout = QGridLayout(container)
        layout.setSpacing(WindowsPhoneTheme.TILE_SPACING)
        layout.setContentsMargins(0, WindowsPhoneTheme.TILE_SPACING, 0, 0)

        btn_procesar = self._create_tile_button(
            "Procesar Venta", "fa5s.credit-card", WindowsPhoneTheme.TILE_GREEN,
            self.confirmar_venta
        )
        layout.addWidget(btn_procesar, 0, 0, 1, 2)

        btn_limpiar = self._create_tile_button(
            "Limpiar Carrito", "fa5s.trash", WindowsPhoneTheme.TILE_RED,
            self.limpiar_carrito
        )
        layout.addWidget(btn_limpiar, 1, 0)

        btn_cancelar = self._create_tile_button(
            "Cancelar", "fa5s.times", WindowsPhoneTheme.TILE_ORANGE,
            self.cerrar_solicitado.emit
        )
        layout.addWidget(btn_cancelar, 1, 1)

        # Evitar que columnas de botones inferior cambien de tamaño relativo
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)

        return container

    def _create_tile_button(self, text, icon_name, color, slot):
        """Crear TileButton con política de tamaño consistente."""
        button = TileButton(text, icon_name, color)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        button.setMinimumHeight(WindowsPhoneTheme.TILE_MIN_HEIGHT)
        button.clicked.connect(slot)
        return button

    def _create_add_button(self, producto):
        """Crear botón de agregar centrado dentro de la celda."""
        container = QWidget()
        container.setContentsMargins(0, 0, 0, 0)

        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)

        btn = QPushButton()
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.setToolTip("Agregar al carrito")
        btn.setFixedSize(30, 30)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {WindowsPhoneTheme.TILE_GREEN};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {WindowsPhoneTheme.TILE_TEAL};
            }}
        """)

        try:
            import qtawesome as qta
            btn.setIcon(qta.icon('fa5s.plus', color='white'))
            btn.setIconSize(QSize(14, 14))
        except Exception:
            btn.setText("+")

        btn.clicked.connect(lambda _, p=producto: self.agregar_al_carrito(p))
        layout.addWidget(btn)

        return container
        
    def cargar_productos(self):
        """Cargar productos disponibles"""
        try:
            productos = self.db_manager.get_all_products()
            self.productos_table.setRowCount(len(productos))
            
            for row, producto in enumerate(productos):
                # Código
                self.productos_table.setItem(row, 0, QTableWidgetItem(producto['codigo_barras'] or f"P{producto['id_producto']:04d}"))
                
                # Nombre
                self.productos_table.setItem(row, 1, QTableWidgetItem(producto['nombre']))
                
                # Precio
                precio_item = QTableWidgetItem(f"${producto['precio_venta']:.2f}")
                precio_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.productos_table.setItem(row, 2, precio_item)
                
                # Stock
                stock_item = QTableWidgetItem(str(producto['stock_actual']))
                stock_item.setTextAlignment(Qt.AlignCenter)
                self.productos_table.setItem(row, 3, stock_item)
                
                btn_container = self._create_add_button(producto)
                self.productos_table.setCellWidget(row, 4, btn_container)
                
        except Exception as e:
            logging.error(f"Error cargando productos: {e}")
            show_warning_dialog(self, "Error", f"Error al cargar productos: {e}")
            
    def buscar_productos(self):
        """Buscar productos por texto"""
        texto = self.search_bar.text().strip()
        if not texto:
            self.cargar_productos()
            return
            
        try:
            productos = self.db_manager.search_products(texto)
            self.productos_table.setRowCount(len(productos))
            
            for row, producto in enumerate(productos):
                self.productos_table.setItem(row, 0, QTableWidgetItem(producto['codigo_barras'] or f"P{producto['id_producto']:04d}"))
                self.productos_table.setItem(row, 1, QTableWidgetItem(producto['nombre']))
                
                precio_item = QTableWidgetItem(f"${producto['precio_venta']:.2f}")
                precio_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.productos_table.setItem(row, 2, precio_item)
                
                stock_item = QTableWidgetItem(str(producto['stock_actual']))
                stock_item.setTextAlignment(Qt.AlignCenter)
                self.productos_table.setItem(row, 3, stock_item)
                
                btn_container = self._create_add_button(producto)
                self.productos_table.setCellWidget(row, 4, btn_container)
                
        except Exception as e:
            logging.error(f"Error buscando productos: {e}")
            
    def agregar_al_carrito(self, producto):
        """Agregar producto al carrito"""
        if producto['stock_actual'] <= 0:
            show_warning_dialog(self, "Sin Stock", f"El producto '{producto['nombre']}' no tiene stock disponible.")
            return
            
        # Verificar si ya está en el carrito
        for item in self.carrito:
            if item['id_producto'] == producto['id_producto']:
                if item['cantidad'] < producto['stock_actual']:
                    item['cantidad'] += 1
                    item['subtotal'] = item['cantidad'] * item['precio']
                else:
                    show_warning_dialog(self, "Stock Insuficiente", f"Solo hay {producto['stock_actual']} unidades disponibles.")
                    return
                break
        else:
            # Nuevo producto en el carrito
            self.carrito.append({
                'id_producto': producto['id_producto'],
                'codigo_interno': producto.get('codigo_interno', ''),
                'nombre': producto['nombre'],
                'precio': producto['precio_venta'],
                'cantidad': 1,
                'subtotal': producto['precio_venta'],
                'stock_disponible': producto['stock_actual']
            })
            
        self.actualizar_carrito()
        
    def actualizar_carrito(self):
        """Actualizar tabla del carrito y total"""
        self.carrito_table.setRowCount(len(self.carrito))
        self.total_venta = 0.0
        
        for row, item in enumerate(self.carrito):
            # Producto
            self.carrito_table.setItem(row, 0, QTableWidgetItem(item['nombre']))
            
            # Precio
            precio_item = QTableWidgetItem(f"${item['precio']:.2f}")
            precio_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.carrito_table.setItem(row, 1, precio_item)
            
            # Cantidad (editable)
            cantidad_spin = QSpinBox()
            cantidad_spin.setMinimum(1)
            cantidad_spin.setMaximum(item['stock_disponible'])
            cantidad_spin.setValue(item['cantidad'])
            cantidad_spin.valueChanged.connect(lambda val, idx=row: self.cambiar_cantidad(idx, val))
            self.carrito_table.setCellWidget(row, 2, cantidad_spin)
            
            # Subtotal
            subtotal_item = QTableWidgetItem(f"${item['subtotal']:.2f}")
            subtotal_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.carrito_table.setItem(row, 3, subtotal_item)
            
            # Botón quitar - SIMPLE, sin contenedor
            btn_quitar = QPushButton()
            btn_quitar.setFixedSize(40, 35)
            btn_quitar.setCursor(QCursor(Qt.PointingHandCursor))
            btn_quitar.setToolTip("Quitar")
            
            # Icono Font Awesome
            try:
                import qtawesome as qta
                btn_quitar.setIcon(qta.icon('fa5s.trash', color='white'))
                btn_quitar.setIconSize(QSize(16, 16))
            except:
                btn_quitar.setText("×")
            
            btn_quitar.setStyleSheet(f"""
                QPushButton {{
                    background-color: {WindowsPhoneTheme.TILE_RED};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 20px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {WindowsPhoneTheme.TILE_ORANGE};
                }}
            """)
            
            btn_quitar.clicked.connect(lambda checked, idx=row: self.quitar_del_carrito(idx))
            self.carrito_table.setCellWidget(row, 4, btn_quitar)
            
            self.total_venta += item['subtotal']
            
        # Actualizar total
        self.total_label.setText(f"${self.total_venta:.2f}")
        
    def cambiar_cantidad(self, index, nueva_cantidad):
        """Cambiar cantidad de un item del carrito"""
        if 0 <= index < len(self.carrito):
            self.carrito[index]['cantidad'] = nueva_cantidad
            self.carrito[index]['subtotal'] = nueva_cantidad * self.carrito[index]['precio']
            self.actualizar_carrito()
            
    def quitar_del_carrito(self, index):
        """Quitar item del carrito"""
        if 0 <= index < len(self.carrito):
            del self.carrito[index]
            self.actualizar_carrito()
            
    def limpiar_carrito(self):
        """Limpiar todo el carrito"""
        if not self.carrito:
            return

        if show_confirmation_dialog(
            self,
            "Confirmar",
            "¿Está seguro de que desea limpiar el carrito?",
            confirm_text="Sí, limpiar",
            cancel_text="No"
        ):
            self.carrito.clear()
            self.actualizar_carrito()
            
    def confirmar_venta(self):
        """Mostrar ventana de confirmación antes de procesar la venta"""
        if not self.carrito:
            show_warning_dialog(self, "Carrito Vacío", "Agregue productos al carrito antes de procesar la venta.")
            return
        
        # Crear diálogo de confirmación
        dialog = ConfirmacionVentaDialog(self.carrito, self.total_venta, self)
        if dialog.exec() == QDialog.Accepted:
            self.procesar_venta()
            
    def procesar_venta(self):
        """Procesar la venta"""
        try:
            # Crear venta en la base de datos
            venta_data = {
                'fecha_venta': datetime.now(),
                'total': self.total_venta,
                'id_usuario': self.user_data.get('id_usuario', self.user_data.get('id', 1)),
                'metodo_pago': 'efectivo',
                'tipo_venta': 'directa',
                'productos': self.carrito
            }
            
            venta_id = self.db_manager.create_sale(venta_data)
            
            if venta_id:
                # Mostrar mensaje de éxito
                show_success_dialog(
                    self, 
                    "Venta Completada", 
                    f"La venta se procesó exitosamente.\nID de venta: {venta_id}",
                    f"Total: ${self.total_venta:.2f}"
                )
                
                # Generar y mostrar ticket
                self.mostrar_ticket(venta_id)
                
                # Emitir señal de venta completada
                self.venta_completada.emit({
                    'id_venta': venta_id,
                    'total': self.total_venta,
                    'productos': len(self.carrito)
                })
                
                # Limpiar carrito
                self.carrito.clear()
                self.actualizar_carrito()
                
                # Recargar productos para actualizar stock
                self.cargar_productos()
                
                logging.info(f"Venta {venta_id} procesada exitosamente: ${self.total_venta:.2f}")
            else:
                show_error_dialog(self, "Error", "No se pudo procesar la venta.")
            
        except Exception as e:
            logging.error(f"Error procesando venta: {e}")
            show_error_dialog(
                self, 
                "Error al Procesar Venta", 
                "No se pudo completar la venta.",
                f"Detalle: {str(e)}"
            )
            
    def mostrar_ticket(self, venta_id):
        """Mostrar ticket de venta"""
        dialog = TicketVentaDialog(
            venta_id=venta_id,
            carrito=self.carrito,
            total=self.total_venta,
            usuario=self.user_data.get('nombre', 'Usuario'),
            parent=self
        )
        dialog.exec()


class ConfirmacionVentaDialog(QDialog):
    """Diálogo de confirmación de venta"""
    
    def __init__(self, carrito, total, parent=None):
        super().__init__(parent)
        self.carrito = carrito
        self.total = total
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar interfaz del diálogo"""
        self.setWindowTitle("Confirmar Venta")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Título
        title = QLabel("CONFIRMAR VENTA")
        title.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {WindowsPhoneTheme.TEXT_PRIMARY}; padding: 10px;")
        layout.addWidget(title)
        
        # Resumen de productos
        resumen_label = QLabel("Resumen de la Venta:")
        resumen_label.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, 12, QFont.Bold))
        layout.addWidget(resumen_label)
        
        # Tabla de resumen
        tabla = QTableWidget()
        tabla.setColumnCount(4)
        tabla.setHorizontalHeaderLabels(["Producto", "Precio", "Cantidad", "Subtotal"])
        tabla.setRowCount(len(self.carrito))
        
        header = tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        tabla.setSelectionMode(QTableWidget.NoSelection)
        
        for row, item in enumerate(self.carrito):
            tabla.setItem(row, 0, QTableWidgetItem(item['nombre']))
            
            precio_item = QTableWidgetItem(f"${item['precio']:.2f}")
            precio_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            tabla.setItem(row, 1, precio_item)
            
            cant_item = QTableWidgetItem(str(item['cantidad']))
            cant_item.setTextAlignment(Qt.AlignCenter)
            tabla.setItem(row, 2, cant_item)
            
            subtotal_item = QTableWidgetItem(f"${item['subtotal']:.2f}")
            subtotal_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            tabla.setItem(row, 3, subtotal_item)
            
        layout.addWidget(tabla)
        
        # Total
        total_frame = QFrame()
        total_frame.setStyleSheet(f"background-color: {WindowsPhoneTheme.TILE_GREEN}; border-radius: 4px; padding: 15px;")
        total_layout = QVBoxLayout(total_frame)
        
        total_title = QLabel("TOTAL A PAGAR")
        total_title.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, 12, QFont.Bold))
        total_title.setStyleSheet("color: white;")
        total_title.setAlignment(Qt.AlignCenter)
        
        total_value = QLabel(f"${self.total:.2f}")
        total_value.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, 32, QFont.Bold))
        total_value.setStyleSheet("color: white;")
        total_value.setAlignment(Qt.AlignCenter)
        
        total_layout.addWidget(total_title)
        total_layout.addWidget(total_value)
        layout.addWidget(total_frame)
        
        # Método de pago
        pago_label = QLabel("Método de Pago: EFECTIVO")
        pago_label.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, 11))
        pago_label.setAlignment(Qt.AlignCenter)
        pago_label.setStyleSheet(f"color: {WindowsPhoneTheme.TEXT_SECONDARY}; padding: 10px;")
        layout.addWidget(pago_label)
        
        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setMinimumHeight(50)
        btn_cancelar.setStyleSheet(f"""
            QPushButton {{
                background-color: {WindowsPhoneTheme.TILE_RED};
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {WindowsPhoneTheme.TILE_ORANGE};
            }}
        """)
        btn_cancelar.clicked.connect(self.reject)
        
        btn_confirmar = QPushButton("Confirmar Venta")
        btn_confirmar.setMinimumHeight(50)
        btn_confirmar.setStyleSheet(f"""
            QPushButton {{
                background-color: {WindowsPhoneTheme.TILE_GREEN};
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {WindowsPhoneTheme.TILE_TEAL};
            }}
        """)
        btn_confirmar.clicked.connect(self.accept)
        
        buttons_layout.addWidget(btn_cancelar)
        buttons_layout.addWidget(btn_confirmar)
        
        layout.addLayout(buttons_layout)


class TicketVentaDialog(QDialog):
    """Diálogo para mostrar el ticket de venta"""
    
    def __init__(self, venta_id, carrito, total, usuario, parent=None):
        super().__init__(parent)
        self.venta_id = venta_id
        self.carrito = carrito
        self.total = total
        self.usuario = usuario
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar interfaz del ticket"""
        self.setWindowTitle("Ticket de Venta")
        self.setMinimumWidth(400)
        self.setMinimumHeight(600)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Área de texto para el ticket
        self.ticket_text = QTextEdit()
        self.ticket_text.setReadOnly(True)
        self.ticket_text.setFont(QFont("Courier New", 10))
        
        # Generar contenido del ticket
        ticket_content = self.generar_ticket()
        self.ticket_text.setPlainText(ticket_content)
        
        layout.addWidget(self.ticket_text)
        
        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        btn_imprimir = QPushButton("Imprimir")
        btn_imprimir.setMinimumHeight(50)
        btn_imprimir.setStyleSheet(f"""
            QPushButton {{
                background-color: {WindowsPhoneTheme.TILE_BLUE};
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {WindowsPhoneTheme.TILE_TEAL};
            }}
        """)
        btn_imprimir.clicked.connect(self.imprimir_ticket)
        
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setMinimumHeight(50)
        btn_cerrar.setStyleSheet(f"""
            QPushButton {{
                background-color: {WindowsPhoneTheme.TILE_ORANGE};
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {WindowsPhoneTheme.TILE_RED};
            }}
        """)
        btn_cerrar.clicked.connect(self.accept)
        
        buttons_layout.addWidget(btn_imprimir)
        buttons_layout.addWidget(btn_cerrar)
        
        layout.addLayout(buttons_layout)
        
    def generar_ticket(self):
        """Generar el contenido del ticket"""
        fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        ticket = "=" * 42 + "\n"
        ticket += "           HTF GIMNASIO\n"
        ticket += "         PUNTO DE VENTA\n"
        ticket += "=" * 42 + "\n\n"
        
        ticket += f"Ticket No.: {self.venta_id:06d}\n"
        ticket += f"Fecha: {fecha_hora}\n"
        ticket += f"Cajero: {self.usuario}\n"
        ticket += "-" * 42 + "\n\n"
        
        ticket += "PRODUCTOS:\n"
        ticket += "-" * 42 + "\n"
        
        for item in self.carrito:
            nombre = item['nombre'][:28]  # Limitar nombre
            ticket += f"{nombre}\n"
            ticket += f"  {item['cantidad']} x ${item['precio']:.2f}"
            ticket += f"{' ' * (30 - len(f'{item['cantidad']} x ${item['precio']:.2f}'))}"
            ticket += f"${item['subtotal']:.2f}\n"
            
        ticket += "-" * 42 + "\n"
        ticket += f"{'TOTAL:' + ' ' * 28}${self.total:.2f}\n"
        ticket += "=" * 42 + "\n\n"
        
        ticket += "      PAGO EN EFECTIVO\n"
        ticket += "-" * 42 + "\n\n"
        
        ticket += "       ¡Gracias por su compra!\n"
        ticket += "         Vuelva pronto\n"
        ticket += "=" * 42 + "\n"
        
        return ticket
        
    def imprimir_ticket(self):
        """Imprimir el ticket"""
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        
        if dialog.exec() == QPrintDialog.Accepted:
            self.ticket_text.document().print(printer)
            show_success_dialog(self, "Éxito", "Ticket impreso correctamente.")
