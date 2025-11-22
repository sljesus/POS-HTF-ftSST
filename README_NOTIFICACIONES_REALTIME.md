# Sistema de Notificaciones en Tiempo Real - PostgreSQL LISTEN/NOTIFY

## 📋 Descripción

El sistema de notificaciones ahora usa **PostgreSQL LISTEN/NOTIFY** para recibir alertas **instantáneas** cuando un miembro registra su entrada en el torniquete.

## 🏗️ Arquitectura

```
┌─────────────────────────┐
│   TORNIQUETE            │
│   Mini PC               │
│   PostgreSQL            │
│   (torniquete_db)       │
└──────────┬──────────────┘
           │
           │ NOTIFY 'nueva_entrada_canal'
           │ (tiempo real)
           ▼
┌─────────────────────────┐
│   POS HTF               │
│   LISTEN (listener)     │
│   → Muestra notificación│
└─────────────────────────┘
```

## 🚀 Configuración

### 1. En el PostgreSQL del Torniquete

Ejecutar el script SQL para crear el trigger:

```bash
psql -U postgres -d torniquete_db -f setup_postgres_trigger.sql
```

O ejecutar manualmente:

```sql
-- Ver contenido de setup_postgres_trigger.sql
```

Este trigger:
- Se dispara cuando hay `INSERT` en `registro_entradas`
- Solo para `tipo_acceso = 'miembro'`
- Envía un JSON completo con datos del miembro por el canal `nueva_entrada_canal`

### 2. En el POS

Configurar la conexión en `main_pos_window.py`:

```python
self.monitor_entradas = MonitorEntradas(
    self.db_manager,
    supabase_service=self.supabase_service,
    pg_host='192.168.1.XXX',      # ← IP de la mini PC del torniquete
    pg_port=5432,
    pg_database='torniquete_db',   # ← Nombre de la BD
    pg_user='pos_user',            # ← Usuario con permisos de LISTEN
    pg_password='tu_password',     # ← Contraseña
    pg_channel='nueva_entrada_canal'
)
```

### 3. Instalar dependencias

```bash
pip install psycopg2-binary
```

Ya está incluido en `requirements.txt`.

## 🧪 Pruebas Locales

### Paso 1: Configurar PostgreSQL local

```bash
# Crear base de datos de prueba
createdb torniquete_db

# Crear tablas básicas (miembros y registro_entradas)
# Usar el schema de tu proyecto
```

### Paso 2: Instalar trigger

```bash
psql -d torniquete_db -f setup_postgres_trigger.sql
```

### Paso 3: Probar listener

En una terminal:

```bash
python test_postgres_listener.py
```

Deberías ver:
```
✅ Conexión establecida
👂 Escuchando canal: nueva_entrada_canal
⏳ Esperando notificaciones...
```

### Paso 4: Simular entrada

En otra terminal:

```bash
python test_simular_entrada_postgres.py
```

Esto insertará un registro y verás la notificación en la primera terminal.

### Paso 5: Probar con el POS

```bash
python main.py
```

Iniciar sesión y dejar el POS abierto. Luego ejecuta el simulador de entradas.

## 📊 Ventajas vs Polling

| Característica | Polling (anterior) | LISTEN/NOTIFY (actual) |
|----------------|-------------------|------------------------|
| Latencia | 0-2 segundos | < 100ms (instantáneo) |
| Carga en BD | Consulta cada 2s | Solo cuando hay evento |
| Escalabilidad | Baja | Alta |
| Conexiones | 1 por ciclo | 1 persistente |
| Confiabilidad | Puede perder eventos | Garantizado |

## 🔧 Configuración de Red

### Para red local del gimnasio:

1. En la mini PC del torniquete:
   - PostgreSQL escuchando en `0.0.0.0` (no solo localhost)
   - Firewall permitir puerto 5432
   - Crear usuario `pos_user` con permisos limitados

```sql
-- En PostgreSQL del torniquete
CREATE USER pos_user WITH PASSWORD 'password_seguro';
GRANT CONNECT ON DATABASE torniquete_db TO pos_user;
GRANT SELECT ON miembros TO pos_user;
GRANT SELECT ON registro_entradas TO pos_user;
```

2. En `pg_hba.conf` del torniquete:
```
# Permitir conexión del POS desde la red local
host    torniquete_db    pos_user    192.168.1.0/24    md5
```

3. En `postgresql.conf`:
```
listen_addresses = '*'
```

## 🐛 Troubleshooting

### Error: "psycopg2 no disponible"
```bash
pip install psycopg2-binary
```

### Error: "Connection refused"
- Verificar que PostgreSQL está corriendo
- Verificar IP y puerto
- Verificar firewall

### Error: "Password authentication failed"
- Verificar usuario y contraseña
- Verificar `pg_hba.conf`

### No llegan notificaciones
```sql
-- Verificar que el trigger existe
SELECT trigger_name FROM information_schema.triggers 
WHERE event_object_table = 'registro_entradas';

-- Probar manualmente
LISTEN nueva_entrada_canal;
-- En otra sesión insertar un registro
-- Deberías ver: Asynchronous notification "nueva_entrada_canal" received...
```

## 📝 Logs

El sistema genera logs detallados:

```
✅ Escuchando canal PostgreSQL: nueva_entrada_canal
📨 Notificación recibida: {"id_entrada":123...
🔔 Procesando entrada ID: 123
```

Ver en consola del POS o archivo de logs.

## 🔐 Seguridad

- ✅ Usuario `pos_user` solo tiene permisos de lectura
- ✅ No puede modificar datos
- ✅ Conexión con contraseña
- ⚠️ Considerar SSL/TLS para producción
