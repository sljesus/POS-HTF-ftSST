"""
Demo de componentes numéricos optimizados para pantalla táctil
Muestra TouchNumericInput y TouchMoneyInput en acción
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QFormLayout, QLabel, QPushButton,
    QHBoxLayout, QGroupBox
)
from PySide6.QtCore import Qt
from ui.components import (
    TouchNumericInput, TouchMoneyInput, WindowsPhoneTheme, StyledLabel
)


class DemoTouchInputs(QWidget):
    """Ventana de demostración de inputs táctiles"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Demo: Campos Numéricos Táctiles")
        self.setMinimumSize(600, 700)
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar interfaz"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        titulo = StyledLabel(
            "Componentes Numéricos Optimizados para Pantalla Táctil",
            bold=True,
            size=WindowsPhoneTheme.FONT_SIZE_TITLE
        )
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Descripción
        descripcion = StyledLabel(
            "Estos campos reemplazan QSpinBox y QDoubleSpinBox\n"
            "eliminando las flechas pequeñas y mejorando la experiencia táctil.",
            size=WindowsPhoneTheme.FONT_SIZE_NORMAL
        )
        descripcion.setAlignment(Qt.AlignCenter)
        descripcion.setStyleSheet(f"color: {WindowsPhoneTheme.TEXT_SECONDARY};")
        layout.addWidget(descripcion)
        
        layout.addSpacing(20)
        
        # ===== GRUPO 1: TouchNumericInput =====
        numeric_group = QGroupBox("TouchNumericInput - Números Enteros")
        numeric_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 14px;
                border: 2px solid {WindowsPhoneTheme.TILE_BLUE};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }}
            QGroupBox::title {{
                color: {WindowsPhoneTheme.TILE_BLUE};
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        numeric_layout = QFormLayout(numeric_group)
        numeric_layout.setSpacing(15)
        
        # Campo de cantidad
        self.cantidad = TouchNumericInput(minimum=1, maximum=9999, default_value=1)
        self.cantidad.valueChanged.connect(self.on_cantidad_changed)
        numeric_layout.addRow("Cantidad (1-9999):", self.cantidad)
        
        # Campo de stock
        self.stock = TouchNumericInput(minimum=0, maximum=99999, default_value=100)
        self.stock.valueChanged.connect(self.on_stock_changed)
        numeric_layout.addRow("Stock (0-99999):", self.stock)
        
        # Etiqueta de resultado
        self.numeric_result = QLabel("Valores: Cantidad=1, Stock=100")
        self.numeric_result.setStyleSheet(f"""
            padding: 10px;
            background-color: {WindowsPhoneTheme.BG_LIGHT};
            border-radius: 4px;
            color: {WindowsPhoneTheme.TILE_BLUE};
            font-weight: bold;
        """)
        numeric_layout.addRow("", self.numeric_result)
        
        layout.addWidget(numeric_group)
        
        # ===== GRUPO 2: TouchMoneyInput =====
        money_group = QGroupBox("TouchMoneyInput - Valores Monetarios")
        money_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 14px;
                border: 2px solid {WindowsPhoneTheme.TILE_GREEN};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }}
            QGroupBox::title {{
                color: {WindowsPhoneTheme.TILE_GREEN};
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        money_layout = QFormLayout(money_group)
        money_layout.setSpacing(15)
        
        # Campo de precio
        self.precio = TouchMoneyInput(
            minimum=0.01,
            maximum=999999.99,
            decimals=2,
            default_value=100.00
        )
        self.precio.valueChanged.connect(self.on_precio_changed)
        money_layout.addRow("Precio de Venta:", self.precio)
        
        # Campo de descuento
        self.descuento = TouchMoneyInput(
            minimum=0.0,
            maximum=100.0,
            decimals=2,
            default_value=0.0,
            prefix="% "
        )
        self.descuento.valueChanged.connect(self.on_descuento_changed)
        money_layout.addRow("Descuento (%):", self.descuento)
        
        # Etiqueta de resultado
        self.money_result = QLabel("Precio: $100.00 | Descuento: %0.00 | Final: $100.00")
        self.money_result.setStyleSheet(f"""
            padding: 10px;
            background-color: {WindowsPhoneTheme.BG_LIGHT};
            border-radius: 4px;
            color: {WindowsPhoneTheme.TILE_GREEN};
            font-weight: bold;
        """)
        money_layout.addRow("", self.money_result)
        
        layout.addWidget(money_group)
        
        # ===== VENTAJAS =====
        ventajas_group = QGroupBox("✅ Ventajas sobre QSpinBox/QDoubleSpinBox")
        ventajas_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 14px;
                border: 2px solid {WindowsPhoneTheme.TILE_ORANGE};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }}
            QGroupBox::title {{
                color: {WindowsPhoneTheme.TILE_ORANGE};
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        ventajas_layout = QVBoxLayout(ventajas_group)
        
        ventajas_text = StyledLabel(
            "• Sin flechas pequeñas (▲▼) difíciles de tocar\n"
            "• Campos grandes (50px altura) fáciles de seleccionar\n"
            "• Teclado numérico automático en tablets\n"
            "• Validación automática de rangos\n"
            "• API compatible con QSpinBox/QDoubleSpinBox\n"
            "• Mejor experiencia de usuario en pantallas táctiles",
            size=WindowsPhoneTheme.FONT_SIZE_NORMAL
        )
        ventajas_text.setStyleSheet(f"color: {WindowsPhoneTheme.TEXT_PRIMARY};")
        ventajas_layout.addWidget(ventajas_text)
        
        layout.addWidget(ventajas_group)
        
        layout.addStretch()
        
        # Botón cerrar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setMinimumHeight(45)
        btn_cerrar.setMinimumWidth(150)
        btn_cerrar.setStyleSheet(f"""
            QPushButton {{
                background-color: {WindowsPhoneTheme.TILE_RED};
                color: white;
                border: none;
                font-weight: bold;
                font-size: 13px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #cc0a00;
            }}
        """)
        btn_cerrar.clicked.connect(self.close)
        btn_layout.addWidget(btn_cerrar)
        
        layout.addLayout(btn_layout)
    
    def on_cantidad_changed(self, valor):
        """Cuando cambia la cantidad"""
        self.actualizar_numeric_result()
    
    def on_stock_changed(self, valor):
        """Cuando cambia el stock"""
        self.actualizar_numeric_result()
    
    def actualizar_numeric_result(self):
        """Actualizar etiqueta de resultado numérico"""
        cantidad = self.cantidad.value()
        stock = self.stock.value()
        self.numeric_result.setText(f"Valores: Cantidad={cantidad}, Stock={stock}")
    
    def on_precio_changed(self, valor):
        """Cuando cambia el precio"""
        self.actualizar_money_result()
    
    def on_descuento_changed(self, valor):
        """Cuando cambia el descuento"""
        self.actualizar_money_result()
    
    def actualizar_money_result(self):
        """Actualizar etiqueta de resultado monetario"""
        precio = self.precio.value()
        descuento = self.descuento.value()
        precio_final = precio * (1 - descuento / 100)
        
        self.money_result.setText(
            f"Precio: ${precio:.2f} | Descuento: {descuento:.2f}% | Final: ${precio_final:.2f}"
        )


def main():
    """Ejecutar demo"""
    app = QApplication(sys.argv)
    
    window = DemoTouchInputs()
    window.show()
    
    print("\n" + "="*70)
    print("DEMO: CAMPOS NUMÉRICOS OPTIMIZADOS PARA PANTALLA TÁCTIL")
    print("="*70)
    print("\nPrueba estos campos en tu pantalla táctil:")
    print("  • TouchNumericInput: Para números enteros (cantidad, stock)")
    print("  • TouchMoneyInput: Para valores monetarios (precio, descuentos)")
    print("\nObserva cómo NO tienen flechas pequeñas y son fáciles de tocar.")
    print("="*70 + "\n")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
