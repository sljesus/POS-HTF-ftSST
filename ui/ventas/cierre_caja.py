"""
Ventana de Cierre de Caja para HTF POS
Usando componentes reutilizables del sistema de diseño
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLineEdit, QGridLayout,
    QTextEdit, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QDoubleValidator
import logging
from datetime import date

# Importar componentes del sistema de diseño
from ui.components import (
    WindowsPhoneTheme,
    TileButton,
    InfoTile,
    SectionTitle,
    ContentPanel,
    StyledLabel,
    show_success_dialog,
    show_warning_dialog,
    show_error_dialog,
    show_confirmation_dialog
)


class CierreCajaWindow(QWidget):
    """Widget para cierre de caja"""
    
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
        """Configurar interfaz de cierre de caja"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(WindowsPhoneTheme.MARGIN_MEDIUM,
                                 WindowsPhoneTheme.MARGIN_MEDIUM,
                                 WindowsPhoneTheme.MARGIN_MEDIUM,
                                 WindowsPhoneTheme.MARGIN_MEDIUM)
        layout.setSpacing(WindowsPhoneTheme.MARGIN_SMALL)
        
        # 1. Sección de conteo de efectivo primero
        self.create_cash_count_section(layout)
        
        # 2. Resumen en una fila (esperado, transacciones, contado)
        self.create_summary_section(layout)
        
        # 3. Espaciador flexible antes de los botones
        layout.addStretch()
        
        # 4. Botones al final
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(WindowsPhoneTheme.TILE_SPACING)
        
        btn_cerrar_caja = TileButton("Cerrar Caja", "fa5s.lock", WindowsPhoneTheme.TILE_GREEN)
        btn_cerrar_caja.clicked.connect(self.procesar_cierre)
        
        btn_cancelar = TileButton("Cancelar", "fa5s.times", WindowsPhoneTheme.TILE_RED)
        btn_cancelar.clicked.connect(self.cerrar_solicitado.emit)
        
        buttons_layout.addWidget(btn_cerrar_caja)
        buttons_layout.addWidget(btn_cancelar)
        
        layout.addLayout(buttons_layout)
        
        # Cargar datos iniciales
        self.cargar_resumen()
        
    def create_cash_count_section(self, parent_layout):
        """Crear sección de conteo de efectivo simplificada"""
        cash_panel = ContentPanel()
        cash_layout = QVBoxLayout(cash_panel)
        cash_layout.setContentsMargins(20, 20, 20, 20)
        cash_layout.setSpacing(15)
        
        # Título
        title = SectionTitle("CONTEO DE EFECTIVO")
        cash_layout.addWidget(title)
        
        # Grid simplificado
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        form_layout.setColumnStretch(1, 1)
        
        # Efectivo en caja
        label_efectivo = StyledLabel("Efectivo en caja:", bold=True, size=WindowsPhoneTheme.FONT_SIZE_NORMAL)
        form_layout.addWidget(label_efectivo, 0, 0, Qt.AlignTop)
        
        self.efectivo_input = QLineEdit()
        self.efectivo_input.setPlaceholderText("0.00")
        
        # Validador para limitar a 99,999.99 máximo con 2 decimales
        validator = QDoubleValidator(0.0, 99999.99, 2)
        validator.setNotation(QDoubleValidator.StandardNotation)
        self.efectivo_input.setValidator(validator)
        
        self.efectivo_input.textChanged.connect(self.calcular_diferencia)
        self.efectivo_input.setMinimumHeight(45)
        self.efectivo_input.setMaximumHeight(50)
        form_layout.addWidget(self.efectivo_input, 0, 1)
        
        # Notas
        label_notas = StyledLabel("Notas:", bold=True, size=WindowsPhoneTheme.FONT_SIZE_NORMAL)
        form_layout.addWidget(label_notas, 1, 0, Qt.AlignTop)
        
        self.notas_input = QTextEdit()
        self.notas_input.setPlaceholderText("Observaciones del cierre de caja...")
        self.notas_input.setMinimumHeight(80)
        self.notas_input.setMaximumHeight(100)
        form_layout.addWidget(self.notas_input, 1, 1)
        
        cash_layout.addLayout(form_layout)
        
        parent_layout.addWidget(cash_panel)
        
    def create_summary_section(self, parent_layout):
        """Crear sección de resumen en una fila"""
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(WindowsPhoneTheme.TILE_SPACING)
        
        # Total esperado
        self.esperado_tile = InfoTile("TOTAL ESPERADO", "fa5s.dollar-sign", WindowsPhoneTheme.TILE_BLUE)
        self.esperado_tile.setMinimumHeight(140)
        self.esperado_value = self.esperado_tile.add_main_value("$0.00")
        self.esperado_tile.add_secondary_value("según ventas")
        summary_layout.addWidget(self.esperado_tile)
        
        # Número de ventas
        self.ventas_tile = InfoTile("TRANSACCIONES", "fa5s.shopping-cart", WindowsPhoneTheme.TILE_GREEN)
        self.ventas_tile.setMinimumHeight(140)
        self.ventas_value = self.ventas_tile.add_main_value("0")
        self.ventas_tile.add_secondary_value("ventas realizadas")
        summary_layout.addWidget(self.ventas_tile)
        
        # Total contado
        self.total_tile = InfoTile("TOTAL CONTADO", "fa5s.money-bill", WindowsPhoneTheme.TILE_ORANGE)
        self.total_tile.setMinimumHeight(140)
        self.total_contado = self.total_tile.add_main_value("$0.00")
        self.diferencia_label = self.total_tile.add_secondary_value("Diferencia: $0.00")
        summary_layout.addWidget(self.total_tile)
        
        parent_layout.addLayout(summary_layout)
        
    def cargar_resumen(self):
        """Cargar resumen del día"""
        try:
            # Obtener ventas del día
            ventas = self.db_manager.get_sales_by_date(date.today())
            
            total_esperado = sum(venta['total'] for venta in ventas)
            num_ventas = len(ventas)
            
            # Actualizar widgets
            self.esperado_value.setText(f"${total_esperado:.2f}")
            self.ventas_value.setText(str(num_ventas))
            
            # Guardar valores para cálculos
            self.total_esperado_valor = total_esperado
            
        except Exception as e:
            logging.error(f"Error cargando resumen: {e}")
            self.total_esperado_valor = 0.0
            
    def calcular_diferencia(self):
        """Calcular diferencia entre esperado y contado"""
        try:
            # Solo efectivo
            efectivo_texto = self.efectivo_input.text()
            
            # Validar que no esté vacío
            if not efectivo_texto:
                efectivo = 0.0
            else:
                efectivo = float(efectivo_texto)
                
                # Validación adicional de límite
                if efectivo > 99999.99:
                    efectivo = 99999.99
                    self.efectivo_input.setText(f"{efectivo:.2f}")
                elif efectivo < 0:
                    efectivo = 0.0
                    self.efectivo_input.setText("0.00")
            
            # Calcular total
            total = efectivo
            
            # Actualizar total contado
            self.total_contado.setText(f"${total:.2f}")
            self.total_contado_valor = total
            
            # Calcular diferencia
            diferencia = total - self.total_esperado_valor
            signo = "+" if diferencia >= 0 else ""
            self.diferencia_label.setText(f"Diferencia: {signo}${diferencia:.2f}")
            
        except ValueError:
            # Si hay un error de conversión, resetear a 0
            self.efectivo_input.setText("0.00")
            self.total_contado.setText("$0.00")
            self.total_contado_valor = 0.0
            self.diferencia_label.setText("Diferencia: $0.00")
        
    def procesar_cierre(self):
        """Procesar cierre de caja"""
        if not hasattr(self, 'total_contado_valor'):
            show_warning_dialog(self, "Cierre de Caja", "Debe contar el efectivo antes de cerrar la caja.")
            return
        
        # Validar que el campo de efectivo tenga un valor válido
        try:
            efectivo = float(self.efectivo_input.text() or 0)
            
            # Validar rango
            if efectivo < 0 or efectivo > 99999.99:
                show_warning_dialog(
                    self, 
                    "Valor Inválido", 
                    "El efectivo debe estar entre $0.00 y $99,999.99"
                )
                return
        except ValueError:
            show_warning_dialog(
                self, 
                "Valor Inválido", 
                "Por favor ingrese un valor numérico válido para el efectivo."
            )
            return
            
        diferencia = self.total_contado_valor - self.total_esperado_valor
        
        # Confirmar cierre
        resumen = (
            f"Total esperado: ${self.total_esperado_valor:.2f}\n\n"
            f"Efectivo en caja: ${efectivo:.2f}\n"
            "─────────────────────\n"
            f"Total contado: ${self.total_contado_valor:.2f}\n"
            f"Diferencia: ${diferencia:.2f}"
        )

        if show_confirmation_dialog(
            self,
            "Confirmar Cierre",
            "Revise el resumen antes de confirmar.",
            detail=resumen,
            confirm_text="Sí, cerrar",
            cancel_text="Volver"
        ):
            try:
                # Obtener valores
                efectivo = float(self.efectivo_input.text() or 0)
                notas = self.notas_input.toPlainText()
                
                # Registrar cierre en la base de datos
                cierre_data = {
                    'fecha': date.today(),
                    'total_esperado': self.total_esperado_valor,
                    'total_contado': self.total_contado_valor,
                    'diferencia': diferencia,
                    'id_usuario': self.user_data['id'],
                    'efectivo': efectivo,
                    'notas': notas
                }
                
                # TODO: Implementar método en db_manager para registrar cierre
                # self.db_manager.register_cash_closing(cierre_data)
                
                show_success_dialog(self, "Cierre Completado", "Cierre de caja registrado exitosamente.")
                self.cerrar_solicitado.emit()
                
            except Exception as e:
                logging.error(f"Error procesando cierre: {e}")
                show_error_dialog(self, "Error", f"Error al procesar cierre: {e}")
