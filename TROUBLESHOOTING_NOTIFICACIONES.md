# Guía Rápida de Troubleshooting - Sistema de Notificaciones

## ⚠️ Problemas Comunes y Soluciones

### 1. KeyboardInterrupt o el POS se congela

**Síntomas:**
- Error `KeyboardInterrupt` en `monitor_entradas.py`
- El POS se congela o no responde
- Alto uso de CPU

**Soluciones:**

#### Opción A: Ajustar el intervalo del monitor
Editar `main_pos_window.py`, línea ~883:

```python
self.monitor_entradas = MonitorEntradas(
    self.db_manager,
    intervalo_ms=5000  # Cambiar de 2000 a 5000 (5 segundos)
)
```

#### Opción B: Desactivar temporalmente el monitor
Comentar la línea en `main_pos_window.py`, línea ~77:

```python
# self.iniciar_monitor_entradas()  # Comentar esta línea
```

#### Opción C: Verificar la base de datos
```bash
python
>>> from database.db_manager import DatabaseManager
>>> db = DatabaseManager()
>>> db.initialize_database()
>>> cursor = db.connection.cursor()
>>> cursor.execute("SELECT COUNT(*) FROM registro_entradas")
>>> print(cursor.fetchone())  # Si hay muchos registros, puede ser el problema
```

### 2. Las notificaciones no aparecen

**Verificaciones:**

1. **Revisar logs del monitor:**
   - Debe aparecer: "Monitor de entradas iniciado correctamente"
   - Debe aparecer: "Detectadas X nueva(s) entrada(s)"

2. **Verificar que hay miembros en la DB:**
   ```bash
   python test_simulador_entradas.py
   # Opción 1: Listar miembros
   ```

3. **Verificar el intervalo de verificación:**
   - El monitor verifica cada 2 segundos
   - Esperar al menos 2-3 segundos después de registrar entrada

4. **Probar con el script de entrada rápida:**
   ```bash
   # Terminal 1: POS abierto
   python main.py
   
   # Terminal 2: Registrar entrada
   python test_entrada_rapida.py
   ```

### 3. Error al cerrar el POS

**Síntomas:**
- Error al cerrar la ventana principal
- El proceso no termina correctamente

**Solución:**
Ya está implementado el manejo seguro en `closeEvent()`. Si persiste:

1. Verificar que no hay notificaciones abiertas manualmente
2. Cerrar usando el botón X de la ventana
3. Si se congela, usar Ctrl+C en la terminal

### 4. Base de datos bloqueada

**Síntomas:**
- Error: "database is locked"
- No se pueden registrar entradas

**Soluciones:**

1. **Cerrar todas las instancias del POS**
2. **Verificar procesos Python activos:**
   ```powershell
   Get-Process python
   ```

3. **Si es necesario, eliminar el lock:**
   ```powershell
   # Cerrar todos los procesos Python
   Stop-Process -Name python -Force
   ```

### 5. Notificaciones fuera de la pantalla

**Síntomas:**
- Las notificaciones no son visibles
- Aparecen en posición incorrecta

**Solución:**
Editar `main_pos_window.py`, método `posicionar_notificacion()`:

```python
def posicionar_notificacion(self, notificacion):
    # Obtener geometría de la ventana principal
    main_geometry = self.geometry()
    
    # Ajustar valores según tu pantalla
    margen = 20  # Aumentar si están muy cerca del borde
    x = main_geometry.right() - notificacion.width() - margen
    y = main_geometry.top() + margen + 80  # Agregar offset para barra superior
    
    # ... resto del código
```

### 6. Monitor consume muchos recursos

**Opciones de optimización:**

#### Aumentar intervalo:
```python
# En main_pos_window.py, línea ~883
intervalo_ms=5000  # 5 segundos en lugar de 2
```

#### Limitar consultas:
En `monitor_entradas.py`, agregar LIMIT:

```python
cursor.execute("""
    SELECT ...
    FROM registro_entradas re
    ...
    ORDER BY re.id_entrada ASC
    LIMIT 5  # Máximo 5 notificaciones a la vez
""", (self.ultimo_id_procesado,))
```

### 7. Foto del miembro no carga

**Verificaciones:**

1. **Verificar que el campo `foto` existe en la tabla:**
   ```sql
   PRAGMA table_info(miembros);
   ```

2. **Verificar path de la foto:**
   - Debe ser ruta absoluta o relativa válida
   - Formatos soportados: JPG, PNG
   - Verificar que el archivo existe

3. **Agregar campo foto si no existe:**
   ```sql
   ALTER TABLE miembros ADD COLUMN foto TEXT;
   ```

## 🔍 Logs de Diagnóstico

### Activar logging detallado

En `main.py`, cambiar nivel de logging:

```python
logging.basicConfig(
    level=logging.DEBUG,  # Cambiar de INFO a DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Logs importantes a revisar:

```
✓ "Monitor de entradas iniciado correctamente"
✓ "Último ID procesado: X"
✓ "Detectadas X nueva(s) entrada(s)"
✓ "Emitiendo señal para entrada ID: X"
✓ "Mostrando notificación para miembro: ..."
✓ "Notificación mostrada para entrada ID: X"

❌ "Error verificando nuevas entradas"
❌ "Error mostrando notificación de entrada"
❌ "Conexión a base de datos no disponible"
```

## 🚨 Solución de Emergencia

Si nada funciona, **deshabilitar el sistema temporalmente:**

En `main_pos_window.py`, línea ~77:

```python
def __init__(self, user_data, db_manager, supabase_service):
    super().__init__()
    self.user_data = user_data
    self.db_manager = db_manager
    self.supabase_service = supabase_service
    
    # ... código ...
    
    self.setup_ui()
    
    # self.iniciar_monitor_entradas()  # ← COMENTAR ESTA LÍNEA
```

Reiniciar el POS y debería funcionar sin el sistema de notificaciones.

## 📊 Verificar Estado del Sistema

### Script de verificación rápida:

```python
# Guardar como: verificar_monitor.py

from database.db_manager import DatabaseManager

db = DatabaseManager()
db.initialize_database()

cursor = db.connection.cursor()

# Verificar tablas
print("=== VERIFICACIÓN DEL SISTEMA ===\n")

# Contar miembros
cursor.execute("SELECT COUNT(*) FROM miembros WHERE activo = 1")
print(f"Miembros activos: {cursor.fetchone()[0]}")

# Contar entradas hoy
cursor.execute("SELECT COUNT(*) FROM registro_entradas WHERE DATE(fecha_entrada) = DATE('now')")
print(f"Entradas hoy: {cursor.fetchone()[0]}")

# Última entrada
cursor.execute("SELECT MAX(id_entrada) FROM registro_entradas")
ultimo_id = cursor.fetchone()[0]
print(f"Último ID entrada: {ultimo_id}")

# Total de entradas
cursor.execute("SELECT COUNT(*) FROM registro_entradas")
print(f"Total entradas: {cursor.fetchone()[0]}")

print("\n✓ Sistema verificado correctamente")
```

Ejecutar: `python verificar_monitor.py`

## 💡 Tips de Rendimiento

1. **No tener el POS y múltiples simuladores abiertos simultáneamente**
2. **Cerrar el POS correctamente** (no forzar cierre)
3. **Usar intervalo de 3-5 segundos** si hay problemas de rendimiento
4. **Limpiar registros antiguos** periódicamente
5. **No simular más de 10 entradas seguidas** sin pausas

## 📞 Contacto

Si los problemas persisten, revisar:
- Versión de Python (recomendado: 3.8+)
- Versión de PySide6 (recomendado: 6.0+)
- Espacio en disco disponible
- Permisos de escritura en la carpeta del proyecto

---

**Última actualización**: Noviembre 2025
