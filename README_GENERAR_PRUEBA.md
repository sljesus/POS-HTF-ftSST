# 🧪 GENERADOR DE DATOS DE PRUEBA - FLUJO COMPLETO

## Descripción

Script para generar datos de prueba automáticamente:
- ✅ Busca un miembro activo aleatoriamente
- ✅ Genera múltiples entradas/visitas con fechas variadas
- ✅ Crea códigos de pago de prueba
- ✅ Prepara el sistema para probar el flujo completo

## Archivo Principal

`test_generar_prueba_flujo.py` - Script Python que genera los datos

## Forma de Usar

### Opción 1: Ejecutar directamente (Recomendado)

```bash
# Abrir terminal PowerShell en la carpeta POS_HTF
python test_generar_prueba_flujo.py
```

### Opción 2: Usar el archivo batch

```bash
# Hacer doble clic en GENERAR_PRUEBA.bat
# O ejecutar desde terminal:
GENERAR_PRUEBA.bat
```

## Qué Genera

### 1. **Miembro Aleatorio**
   - Selecciona un miembro activo de la BD
   - Se muestra toda su información

### 2. **5 Visitas/Entradas**
   - Con fechas distribuidas en los últimos 30 días
   - Diferentes áreas (Pesas, Cardio, Yoga, etc.)
   - Diferentes tipos de acceso

   Ejemplo:
   ```
   ✅ Visita 1: ID entrada 245 - 2025-12-15 14:30
   ✅ Visita 2: ID entrada 246 - 2025-12-10 09:45
   ```

### 3. **3 Códigos de Pago**
   - Códigos formato: CASH-XXXX (ej: CASH-5287)
   - Montos aleatorios ($100-$2000)
   - Notificaciones pendientes

   Ejemplo:
   ```
   ✅ Código 1: CASH-5287 | Monto: $1500 | ID Notif: 892
   ✅ Código 2: CASH-1234 | Monto: $500  | ID Notif: 893
   ```

## Cómo Probar el Flujo Completo

### Paso 1: Generar datos
```bash
python test_generar_prueba_flujo.py
```

Se verá algo así:
```
🎯 GENERADOR DE DATOS DE PRUEBA - FLUJO COMPLETO
==========================================
✅ Conexiones establecidas
✅ Miembro encontrado: Juan Carlos Pérez

📝 Generando 5 visitas para miembro ID 1...
  ✅ Visita 1: ID entrada 245 - 2025-12-15 14:30
  ✅ Visita 2: ID entrada 246 - 2025-12-10 09:45
  ...

💰 Generando 3 códigos de pago para miembro ID 1...
  ✅ Código 1: CASH-5287 | Monto: $1500 | ID Notif: 892
  ✅ Código 2: CASH-1234 | Monto: $500  | ID Notif: 893
  ...

📊 RESUMEN DE DATOS GENERADOS
==========================================
👤 MIEMBRO SELECCIONADO:
   ID: 1
   Nombre: Juan Carlos Pérez García
   ...

PROXIMOS PASOS:
1. Inicia la aplicación POS
2. Busca al miembro: Juan Carlos Pérez
3. Prueba escanear: CASH-5287, CASH-1234
4. Verifica que se procese correctamente
```

### Paso 2: Inicia la aplicación POS
```bash
python main.py
```

### Paso 3: Prueba el flujo

**3.1 Prueba de Escaneo de Código:**
- Hace clic en botón "Escanear Código Pago"
- Ingresa uno de los códigos generados (ej: CASH-5287)
- Presiona Enter
- Debe abrir el modal de notificación del miembro
- Verifica los datos del pago

**3.2 Prueba de Historial:**
- En la ventana principal, busca al miembro por nombre
- Abre el historial de entradas
- Debe aparecer las 5 visitas generadas con sus fechas

**3.3 Prueba de Acceso:**
- Escanea el código QR del miembro (o código manual)
- Sistema debe registrar la entrada
- Debe aparecer en historial

## Estructura de Datos Generados

```
MIEMBRO
  ├─ Visitas (registro_entradas)
  │  ├─ Visita 1 (hace 25 días)
  │  ├─ Visita 2 (hace 18 días)
  │  ├─ Visita 3 (hace 10 días)
  │  ├─ Visita 4 (hace 5 días)
  │  └─ Visita 5 (hace 2 días)
  │
  └─ Códigos de Pago (notificaciones_pos)
     ├─ CASH-5287 ($1500) - Pendiente
     ├─ CASH-1234 ($500)  - Pendiente
     └─ CASH-9876 ($2000) - Pendiente
```

## Ventajas

- ✅ **Rápido**: Genera datos en segundos
- ✅ **Realista**: Datos distribuidos en tiempo
- ✅ **Completo**: Prueba todo el flujo
- ✅ **Repetible**: Ejecuta varias veces si necesita más datos
- ✅ **Seguro**: Solo usa base de datos de prueba

## Notas

- Cada vez que ejecutas el script genera datos **nuevos**
- Los miembros deben estar activos en la BD
- Si no hay miembros activos, el script no funcionará
- Los códigos de pago se marcan como "respondida: false" (pendientes)

## Solución de Problemas

### "No se encontró ningún miembro activo"
- Verifica que haya miembros con `activo = TRUE` en la BD
- Ejecuta `insertar_datos_prueba.py` primero

### "Error de conexión"
- Verifica que PostgreSQL/Supabase esté disponible
- Revisa las variables de entorno en `.env`
- Prueba con `test_connection.py`

### Los códigos no aparecen en POS
- Verifica que Supabase esté sincronizando
- Revisa los logs en `pos_htf.log`
- Prueba manualmente con `test_supabase_sync.py`

## Modificar Cantidades

Para cambiar la cantidad de visitas o códigos, edita el archivo:

```python
# test_generar_prueba_flujo.py, línea ~240
ids_entrada = generar_visitas(pg_manager, miembro['id_miembro'], cantidad=5)    # Cambiar 5
codigos = generar_codigos_pago(supabase_service, pg_manager, miembro['id_miembro'], cantidad=3)  # Cambiar 3
```

## Scripts Relacionados

- `test_connection.py` - Verifica conexiones
- `test_supabase_sync.py` - Prueba sincronización
- `insertar_datos_prueba.py` - Genera miembros y productos
- `main.py` - Aplicación POS

---

**Última actualización**: 2025-12-18
**Versión**: 1.0
