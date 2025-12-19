"""
Script de Migración de Base de Datos
Actualiza el esquema de Supabase con los cambios del esquema local
Fecha: 19 de Diciembre 2025
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migracion_supabase.log'),
        logging.StreamHandler()
    ]
)

# Cargar variables de entorno
load_dotenv()

def get_supabase_client() -> Client:
    """Crear cliente de Supabase"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("SUPABASE_URL y SUPABASE_KEY deben estar configurados en .env")
    
    return create_client(url, key)

def ejecutar_sql(client: Client, sql: str, descripcion: str) -> bool:
    """Ejecutar una consulta SQL y registrar el resultado"""
    try:
        logging.info(f"Ejecutando: {descripcion}")
        # Supabase no tiene ejecución directa de SQL desde el cliente Python
        # Necesitamos usar la API REST o hacer las operaciones de otra forma
        logging.warning("⚠️  Esta operación debe ejecutarse manualmente en la consola SQL de Supabase")
        logging.info(f"SQL: {sql}")
        return True
    except Exception as e:
        logging.error(f"❌ Error en {descripcion}: {e}")
        return False

def main():
    """Ejecutar migración completa"""
    logging.info("="*60)
    logging.info("INICIANDO MIGRACIÓN DE BASE DE DATOS")
    logging.info(f"Fecha: {datetime.now()}")
    logging.info("="*60)
    
    try:
        client = get_supabase_client()
        logging.info("✅ Conectado a Supabase")
        
        print("\n" + "="*60)
        print("IMPORTANTE: Este script genera el SQL necesario.")
        print("Debes ejecutar el SQL manualmente en la consola de Supabase:")
        print("1. Ve a https://supabase.com/dashboard")
        print("2. Selecciona tu proyecto")
        print("3. Ve a SQL Editor")
        print("4. Copia y pega el SQL que se muestra a continuación")
        print("="*60 + "\n")
        
        # SQL completo de migración
        migracion_sql = """
-- ==========================================================
-- SCRIPT DE MIGRACIÓN SUPABASE
-- Ejecutar en SQL Editor de Supabase Dashboard
-- ==========================================================

-- PASO 1: Crear tabla ca_ubicaciones
CREATE TABLE IF NOT EXISTS ca_ubicaciones (
    id_ubicacion SERIAL PRIMARY KEY,
    nombre CHARACTER VARYING(100) NOT NULL UNIQUE,
    descripcion TEXT,
    activa BOOLEAN NOT NULL DEFAULT TRUE,
    creada_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_nombre_ubicacion_length CHECK (LENGTH(nombre) >= 3)
);

-- Insertar ubicaciones predefinidas
INSERT INTO ca_ubicaciones (nombre, descripcion, activa) VALUES
    ('Zona Lockers', 'Área de almacenamiento en lockers', TRUE),
    ('Recepción', 'Mostrador de recepción', TRUE),
    ('Bodega 1', 'Bodega principal de almacenamiento', TRUE),
    ('Bodega 2', 'Bodega secundaria de almacenamiento', TRUE),
    ('Mostrador', 'Productos en exhibición', TRUE),
    ('Almacén Central', 'Almacén central del gimnasio', TRUE)
ON CONFLICT (nombre) DO NOTHING;

-- PASO 2: Migrar inventario.ubicacion a id_ubicacion
-- Agregar nueva columna
ALTER TABLE inventario ADD COLUMN IF NOT EXISTS id_ubicacion INTEGER;

-- Mapear ubicaciones existentes
UPDATE inventario SET id_ubicacion = (
    SELECT id_ubicacion FROM ca_ubicaciones 
    WHERE ca_ubicaciones.nombre = inventario.ubicacion
    LIMIT 1
) WHERE id_ubicacion IS NULL;

-- Asignar default para ubicaciones sin match (Recepción)
UPDATE inventario SET id_ubicacion = 2 WHERE id_ubicacion IS NULL;

-- Hacer NOT NULL y agregar constraint
ALTER TABLE inventario ALTER COLUMN id_ubicacion SET NOT NULL;
ALTER TABLE inventario ALTER COLUMN id_ubicacion SET DEFAULT 2;

-- Agregar foreign key
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'inventario_id_ubicacion_fkey'
    ) THEN
        ALTER TABLE inventario ADD CONSTRAINT inventario_id_ubicacion_fkey 
            FOREIGN KEY (id_ubicacion) REFERENCES ca_ubicaciones(id_ubicacion);
    END IF;
END $$;

-- Eliminar columna antigua ubicacion (CUIDADO: esto es destructivo)
-- ALTER TABLE inventario DROP COLUMN IF EXISTS ubicacion;
-- NOTA: Comentado por seguridad. Descomentar solo cuando estés seguro.

-- PASO 3: Actualizar asignaciones_activas
ALTER TABLE asignaciones_activas ADD COLUMN IF NOT EXISTS estado CHARACTER VARYING DEFAULT 'activa';

-- Actualizar estados existentes
UPDATE asignaciones_activas SET estado = 'activa' 
WHERE activa = TRUE AND cancelada = FALSE AND estado IS NULL;

UPDATE asignaciones_activas SET estado = 'cancelada' 
WHERE cancelada = TRUE AND estado IS NULL;

UPDATE asignaciones_activas SET estado = 'vencida' 
WHERE activa = FALSE AND cancelada = FALSE AND estado IS NULL;

-- Agregar constraint de coherencia
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'chk_estado_coherente'
    ) THEN
        ALTER TABLE asignaciones_activas DROP CONSTRAINT chk_estado_coherente;
    END IF;
    
    ALTER TABLE asignaciones_activas ADD CONSTRAINT chk_estado_coherente CHECK (
        (activa = TRUE AND cancelada = FALSE AND estado = 'activa') OR
        (activa = FALSE AND estado IN ('vencida', 'cancelada', 'inactiva'))
    );
END $$;

-- PASO 4: Actualizar ca_suplementos
ALTER TABLE ca_suplementos ADD COLUMN IF NOT EXISTS peso_neto_gr DECIMAL(8, 2);

-- PASO 5: Actualizar turnos_caja
ALTER TABLE turnos_caja ADD COLUMN IF NOT EXISTS creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE turnos_caja ADD COLUMN IF NOT EXISTS actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Actualizar registros existentes con fecha de apertura
UPDATE turnos_caja SET creado_en = fecha_apertura WHERE creado_en IS NULL;
UPDATE turnos_caja SET actualizado_en = COALESCE(fecha_cierre, fecha_apertura) WHERE actualizado_en IS NULL;

-- PASO 6: Crear índices
CREATE INDEX IF NOT EXISTS idx_ubicaciones_activas ON ca_ubicaciones (activa);
CREATE INDEX IF NOT EXISTS idx_inventario_ubicacion ON inventario (id_ubicacion, seccion);
CREATE UNIQUE INDEX IF NOT EXISTS idx_turno_activo_por_usuario 
    ON turnos_caja (id_usuario) WHERE cerrado = FALSE;

-- PASO 7: Índices para notificaciones_pos
CREATE INDEX IF NOT EXISTS idx_notificaciones_miembro ON notificaciones_pos (id_miembro, leida);
CREATE INDEX IF NOT EXISTS idx_notificaciones_tipo ON notificaciones_pos (tipo_notificacion, creada_en DESC);
CREATE INDEX IF NOT EXISTS idx_notificaciones_pendientes ON notificaciones_pos (leida, para_recepcion) 
    WHERE leida = FALSE;
CREATE INDEX IF NOT EXISTS idx_notificaciones_vencimiento ON notificaciones_pos (fecha_vencimiento) 
    WHERE respondida = FALSE;
CREATE UNIQUE INDEX IF NOT EXISTS idx_notificaciones_codigo_pago ON notificaciones_pos (codigo_pago_generado) 
    WHERE codigo_pago_generado IS NOT NULL;

-- ==========================================================
-- VERIFICACIÓN
-- ==========================================================

-- Verificar ca_ubicaciones
SELECT 'ca_ubicaciones' as tabla, COUNT(*) as registros FROM ca_ubicaciones;

-- Verificar migración de inventario
SELECT 'inventario' as tabla, COUNT(*) as registros, 
       COUNT(DISTINCT id_ubicacion) as ubicaciones_distintas 
FROM inventario;

-- Verificar asignaciones_activas
SELECT 'asignaciones_activas' as tabla, 
       estado, COUNT(*) as cantidad 
FROM asignaciones_activas 
GROUP BY estado;

-- ==========================================================
-- FIN DEL SCRIPT DE MIGRACIÓN
-- ==========================================================
"""
        
        # Guardar SQL en archivo
        sql_file = "migracion_supabase.sql"
        with open(sql_file, 'w', encoding='utf-8') as f:
            f.write(migracion_sql)
        
        logging.info(f"✅ SQL guardado en: {sql_file}")
        
        print("\n" + "="*60)
        print(f"SQL DE MIGRACIÓN GUARDADO EN: {sql_file}")
        print("="*60)
        print(migracion_sql)
        print("="*60)
        
        print("\n📋 PASOS A SEGUIR:")
        print("1. Haz BACKUP de tu base de datos en Supabase")
        print("2. Ve a: https://supabase.com/dashboard/project/[tu-proyecto]/sql")
        print("3. Copia el contenido del archivo 'migracion_supabase.sql'")
        print("4. Pégalo en el SQL Editor")
        print("5. Ejecuta el script")
        print("6. Revisa los resultados de verificación al final")
        print("\n⚠️  ADVERTENCIA: La línea de DROP COLUMN está comentada por seguridad")
        print("   Descoméntala solo cuando estés seguro de que todo funciona correctamente")
        
        logging.info("✅ Migración preparada exitosamente")
        
    except Exception as e:
        logging.error(f"❌ Error fatal: {e}")
        return False
    
    logging.info("="*60)
    logging.info("SCRIPT COMPLETADO")
    logging.info("="*60)
    return True

if __name__ == "__main__":
    main()
