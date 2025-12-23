# Campos Numéricos Optimizados para Pantalla Táctil

## Problema con QSpinBox y QDoubleSpinBox

Los widgets estándar de Qt `QSpinBox` y `QDoubleSpinBox` tienen **flechas pequeñas** (▲▼) que son difíciles de usar en pantallas táctiles:

❌ **Problemas**:
- Flechas muy pequeñas (difíciles de tocar con dedos)
- Experiencia de usuario pobre en tablets
- No aprovechan teclado táctil numérico
- Diseño orientado a mouse/teclado físico

## Solución: TouchNumericInput y TouchMoneyInput

Hemos creado dos componentes personalizados en `ui/components.py` que reemplazan los spinboxes tradicionales:

### 1. `TouchNumericInput` 
**Para números enteros (cantidades, stock, etc.)**

✅ **Ventajas**:
- Campo grande y fácil de tocar (50px altura mínima)
- Teclado numérico automático en dispositivos táctiles
- Validación automática de rango
- API compatible con `QSpinBox`

**Ejemplo de uso:**

```python
from ui.components import TouchNumericInput

# Antes (QSpinBox)
cantidad_spin = QSpinBox()
cantidad_spin.setRange(1, 9999)
cantidad_spin.setValue(1)
cantidad_spin.setMinimumHeight(46)

# Ahora (TouchNumericInput) - Más simple y táctil
cantidad_input = TouchNumericInput(minimum=1, maximum=9999, default_value=1)

# API compatible
cantidad_input.setValue(5)
valor = cantidad_input.value()
cantidad_input.setRange(1, 100)
cantidad_input.valueChanged.connect(mi_funcion)
```

### 2. `TouchMoneyInput`
**Para cantidades monetarias (precios, montos, etc.)**

✅ **Ventajas**:
- Formato automático con símbolo de moneda ($ )
- Validación de decimales (2 dígitos por defecto)
- Color verde para valores monetarios
- Alineación a la derecha (estándar contable)

**Ejemplo de uso:**

```python
from ui.components import TouchMoneyInput

# Antes (QDoubleSpinBox)
precio_input = QDoubleSpinBox()
precio_input.setPrefix("$ ")
precio_input.setDecimals(2)
precio_input.setMaximum(999999.99)
precio_input.setMinimumHeight(40)

# Ahora (TouchMoneyInput) - Más simple y táctil
precio_input = TouchMoneyInput(maximum=999999.99, decimals=2, prefix="$ ")

# API compatible
precio_input.setValue(150.50)  # Mostrará: $ 150.50
valor = precio_input.value()   # Retorna: 150.50 (float)
precio_input.valueChanged.connect(mi_funcion)
```

## Migración de Código Existente

### Archivos que deben actualizarse:

1. **`ui/nuevo_producto_window.py`**
   - Línea 127: `self.precio_input` → Usar `TouchMoneyInput`
   - Línea 183: `self.peso_input` → Usar `TouchNumericInput` o `TouchMoneyInput`
   - Línea 231: `self.peso_neto_input` → Similar

2. **`ui/movimiento_inventario_window.py`**
   - Línea 129: `self.cantidad_spin` → Usar `TouchNumericInput`

3. **`ui/sales_windows.py`**
   - Línea 291: `cantidad_spin` en carrito → Usar `TouchNumericInput`

4. **`ui/asignacion_turnos_window.py`**
   - Línea 191: `self.monto_inicial` → Usar `TouchMoneyInput`

## Comparación Visual

```
┌─────────────────────────────────┐
│  QSpinBox (Tradicional)         │
├─────────────────────────────────┤
│  [ 5        ] ▲▼  ← Flechas     │
│                     pequeñas    │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│  TouchNumericInput (Táctil)     │
├─────────────────────────────────┤
│  ┌───────────────────────────┐  │
│  │          5                │  │ ← Campo grande
│  └───────────────────────────┘  │   fácil de tocar
└─────────────────────────────────┘
```

## API Completa

### TouchNumericInput

```python
# Constructor
input = TouchNumericInput(
    minimum=0,          # Valor mínimo
    maximum=999999,     # Valor máximo
    default_value=0,    # Valor inicial
    parent=None
)

# Métodos (compatibles con QSpinBox)
input.setValue(100)              # Establecer valor
valor = input.value()            # Obtener valor (int)
input.setRange(0, 1000)          # Establecer rango
input.setMinimum(0)              # Solo mínimo
input.setMaximum(1000)           # Solo máximo

# Señales
input.valueChanged.connect(callback)  # Se emite al cambiar
```

### TouchMoneyInput

```python
# Constructor
input = TouchMoneyInput(
    minimum=0.0,
    maximum=999999.99,
    decimals=2,         # Cantidad de decimales
    default_value=0.0,
    prefix="$ ",        # Símbolo de moneda
    parent=None
)

# Métodos (compatibles con QDoubleSpinBox)
input.setValue(150.50)           # Muestra: $ 150.50
valor = input.value()            # Retorna: 150.50 (float)
input.setRange(0.0, 10000.0)     # Establecer rango
input.setDecimals(2)             # Decimales
input.setPrefix("$ ")            # Cambiar prefijo

# Señales
input.valueChanged.connect(callback)  # Se emite al cambiar
```

## Características Técnicas

### Validación Automática
- `TouchNumericInput` usa `QIntValidator` para validar enteros
- `TouchMoneyInput` usa `QDoubleValidator` para decimales
- No permite ingresar caracteres inválidos

### Estilo Visual
- **Altura mínima**: 50px (óptimo para dedos)
- **Borde azul** al obtener foco
- **Fondo claro** para indicar campo activo
- **Fuente grande** (18px) para legibilidad

### Señales Compatibles
- `valueChanged(int)` para `TouchNumericInput`
- `valueChanged(float)` para `TouchMoneyInput`
- Totalmente compatibles con código existente que usa spinboxes

## Ejemplo Completo: Formulario de Producto

```python
from PySide6.QtWidgets import QWidget, QFormLayout
from ui.components import TouchNumericInput, TouchMoneyInput

class ProductoForm(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout(self)
        
        # Precio (monetario)
        self.precio = TouchMoneyInput(
            minimum=0.01,
            maximum=999999.99,
            decimals=2,
            default_value=0.0
        )
        layout.addRow("Precio de Venta:", self.precio)
        
        # Stock (numérico)
        self.stock = TouchNumericInput(
            minimum=0,
            maximum=99999,
            default_value=0
        )
        layout.addRow("Stock Inicial:", self.stock)
        
        # Conectar señales
        self.precio.valueChanged.connect(self.on_precio_changed)
        self.stock.valueChanged.connect(self.on_stock_changed)
    
    def on_precio_changed(self, valor):
        print(f"Nuevo precio: ${valor:.2f}")
    
    def on_stock_changed(self, valor):
        print(f"Nuevo stock: {valor} unidades")
```

## Beneficios

✅ **Mejor UX en pantallas táctiles**: Campos grandes y fáciles de tocar  
✅ **Sin flechas molestas**: Experiencia más limpia  
✅ **Teclado numérico**: Se activa automáticamente en tablets  
✅ **Validación robusta**: Previene errores de entrada  
✅ **Compatible**: API similar a QSpinBox/QDoubleSpinBox  
✅ **Consistente**: Usa el sistema de diseño WindowsPhoneTheme  

---

**Implementado en**: `ui/components.py`  
**Fecha**: Diciembre 2025  
**Sistema**: HTF POS - Point of Sale
