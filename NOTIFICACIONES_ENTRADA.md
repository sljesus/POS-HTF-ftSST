# Sistema de Notificaciones de Entrada de Miembros

## 📋 Descripción

Sistema automático de notificaciones emergentes que muestra la información del miembro cada vez que se registra una entrada al gimnasio.

## ⚡ Inicio Rápido

### 1. Verificar el Sistema
```bash
python verificar_notificaciones.py
```
Este script verifica que todo esté configurado correctamente.

### 2. Probar el Sistema
```bash
# Terminal 1: Abrir el POS
python main.py

# Terminal 2: Simular una entrada
python test_entrada_rapida.py
```

### 3. Si hay problemas
Consultar: `TROUBLESHOOTING_NOTIFICACIONES.md`

## ✨ Características

- **Notificaciones Emergentes Automáticas**: Aparecen automáticamente cuando un miembro registra su entrada
- **Información del Miembro**: Muestra foto, nombre completo, ID, teléfono y datos relevantes
- **Diseño Atractivo**: Interfaz Windows Phone con animaciones suaves
- **Auto-cierre**: Las notificaciones se cierran automáticamente después de 6 segundos
- **No Bloqueante**: Las notificaciones no bloquean el trabajo en el POS
- **Múltiples Notificaciones**: Soporta varias notificaciones apiladas verticalmente

## 🏗️ Componentes

### 1. NotificacionEntradaWidget (`ui/notificacion_entrada_widget.py`)
Ventana emergente que muestra:
- ✓ Foto del miembro (circular)
- ✓ Nombre completo
- ✓ ID de miembro
- ✓ Fecha de registro
- ✓ Teléfono de contacto
- ✓ Hora de entrada
- ✓ Botón para cerrar manualmente

### 2. MonitorEntradas (`utils/monitor_entradas.py`)
Sistema de monitoreo que:
- Verifica la tabla `registro_entradas` cada 2 segundos
- Detecta nuevos registros automáticamente
- Emite señal con los datos del miembro
- Se ejecuta en segundo plano sin afectar rendimiento

### 3. Integración en MainPOSWindow
- Inicia automáticamente al abrir el POS
- Posiciona notificaciones en la esquina superior derecha
- Gestiona múltiples notificaciones simultáneas
- Se detiene automáticamente al cerrar el POS

## 🧪 Pruebas

### Script de Prueba: `test_simulador_entradas.py`

Simulador interactivo para probar el sistema de notificaciones.

#### Ejecutar el simulador:

```bash
python test_simulador_entradas.py
```

#### Opciones del menú:

1. **Listar miembros disponibles**
   - Muestra todos los miembros activos en la base de datos
   - Útil para conocer los IDs disponibles

2. **Simular entrada de un miembro específico**
   - Registra entrada de un miembro por ID
   - Permite especificar área y notas
   - Verifica si el miembro está activo

3. **Simular entradas aleatorias automáticas**
   - Genera múltiples entradas aleatorias
   - Configurable: cantidad e intervalo
   - Perfecto para probar notificaciones múltiples

4. **Ver últimas entradas registradas**
   - Muestra historial reciente
   - Verifica que las entradas se registraron correctamente

5. **Salir**

## 📝 Uso del Sistema

### Flujo Normal

1. **Iniciar el POS**: El monitor se inicia automáticamente
2. **Registrar Entrada**: Cuando un miembro accede (desde cualquier dispositivo/ventana)
3. **Notificación Automática**: Aparece la notificación con datos del miembro
4. **Auto-cierre**: La notificación desaparece después de 6 segundos

### Para Probar

#### Opción A: Usar el Simulador (Recomendado)

1. Abrir dos terminales:
   - **Terminal 1**: Ejecutar el POS
     ```bash
     python main.py
     ```
   
   - **Terminal 2**: Ejecutar el simulador
     ```bash
     python test_simulador_entradas.py
     ```

2. En el simulador:
   - Seleccionar opción **3** (Simular entradas aleatorias)
   - Ingresar cantidad: `5`
   - Ingresar intervalo: `3` segundos
   - Observar las notificaciones en el POS

#### Opción B: Registro Manual

1. Abrir el POS
2. Ir a la pestaña "Miembros"
3. Buscar un miembro
4. Registrar su entrada
5. Observar la notificación emergente

## 🎨 Personalización

### Modificar Duración de Notificaciones

En `main_pos_window.py`, línea ~887:

```python
notificacion = NotificacionEntradaWidget(
    miembro_data=entrada_data,
    parent=self,
    duracion=6000  # Cambiar valor en milisegundos
)
```

### Modificar Intervalo de Monitoreo

En `main_pos_window.py`, línea ~882:

```python
self.monitor_entradas = MonitorEntradas(
    self.db_manager,
    intervalo_ms=2000  # Cambiar intervalo en milisegundos
)
```

### Modificar Posición de Notificaciones

En `main_pos_window.py`, método `posicionar_notificacion()`:

```python
# Esquina superior derecha (actual)
x = main_geometry.right() - notificacion.width() - margen
y = main_geometry.top() + margen

# Para esquina superior izquierda:
# x = main_geometry.left() + margen
# y = main_geometry.top() + margen

# Para esquina inferior derecha:
# x = main_geometry.right() - notificacion.width() - margen
# y = main_geometry.bottom() - notificacion.height() - margen
```

## 🔧 Configuración de Base de Datos

### Tabla Requerida: `registro_entradas`

El sistema monitorea esta tabla. Asegúrate de que exista:

```sql
CREATE TABLE IF NOT EXISTS registro_entradas (
    id_entrada INTEGER PRIMARY KEY AUTOINCREMENT,
    id_miembro INTEGER,
    tipo_acceso TEXT NOT NULL,
    fecha_entrada TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    area_accedida TEXT DEFAULT 'General',
    dispositivo_registro TEXT,
    notas TEXT,
    ...
    FOREIGN KEY (id_miembro) REFERENCES miembros (id_miembro)
);
```

### Campos Requeridos del Miembro

Para mostrar correctamente la información:

- `id_miembro` (INTEGER)
- `nombres` (TEXT)
- `apellido_paterno` (TEXT)
- `apellido_materno` (TEXT)
- `telefono` (TEXT, opcional)
- `email` (TEXT, opcional)
- `fecha_registro` (DATE, opcional)
- `activo` (BOOLEAN)
- `foto` (TEXT, path a imagen, opcional)

## 🐛 Troubleshooting

### Las notificaciones no aparecen

1. **Verificar que el monitor está activo**:
   - Revisar logs: debe aparecer "Monitor de entradas iniciado"

2. **Verificar registros en la DB**:
   ```bash
   python test_simulador_entradas.py
   # Opción 4: Ver últimas entradas
   ```

3. **Verificar intervalo del monitor**:
   - Por defecto verifica cada 2 segundos
   - Esperar al menos 2 segundos después de registrar entrada

### Notificaciones no se posicionan correctamente

1. **Ajustar margen en `posicionar_notificacion()`**
2. **Verificar resolución de pantalla**
3. **Probar en modo ventana (no maximizado)**

### Error al cargar fotos

1. **Verificar path de la foto en DB**
2. **Asegurar que el archivo existe**
3. **Formato soportado**: JPG, PNG
4. **Fallback**: Si no hay foto, muestra iniciales en círculo de color

## 📊 Logs

El sistema genera logs detallados:

```
INFO - Monitor de entradas iniciado (intervalo: 2000ms)
INFO - Último ID procesado: 45
INFO - Detectadas 1 nueva(s) entrada(s)
INFO - Emitiendo señal para entrada ID: 46, Miembro: Juan Pérez
INFO - Mostrando notificación para miembro: Juan Pérez García
INFO - Notificación mostrada para entrada ID: 46
INFO - Notificación de entrada cerrada
```

## 🚀 Características Futuras (Posibles Mejoras)

- [ ] Sonido al mostrar notificación
- [ ] Diferentes colores según tipo de membresía
- [ ] Mostrar foto del QR escaneado
- [ ] Historial de notificaciones del día
- [ ] Integración con sistema de alertas (membresía vencida, etc.)
- [ ] Soporte para notificaciones de salida
- [ ] Dashboard con métricas en tiempo real

## 📄 Archivos Modificados/Creados

### Nuevos Archivos
- `POS_HTF/ui/notificacion_entrada_widget.py` - Widget de notificación
- `POS_HTF/utils/monitor_entradas.py` - Monitor de base de datos
- `POS_HTF/test_simulador_entradas.py` - Script de pruebas

### Archivos Modificados
- `POS_HTF/ui/main_pos_window.py` - Integración del sistema

## 💡 Notas Técnicas

- **Framework**: PySide6 (Qt6)
- **Base de Datos**: SQLite3
- **Animaciones**: QPropertyAnimation con QGraphicsOpacityEffect
- **Señales**: Sistema de señales Qt para comunicación entre componentes
- **Timer**: QTimer para monitoreo periódico no bloqueante
- **Thread Safety**: Todas las operaciones en el hilo principal de Qt

## 📞 Soporte

Para problemas o mejoras, contactar al equipo de desarrollo.

---

**Última actualización**: Noviembre 2025
**Versión**: 1.0.0
