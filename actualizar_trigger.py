"""
Script para actualizar el trigger en PostgreSQL con codificación UTF-8 correcta
"""

import psycopg2

PG_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'HTF_DB',
    'user': 'postgres',
    'password': 'postgres'
}

TRIGGER_SQL = """
-- Eliminar función anterior si existe
DROP TRIGGER IF EXISTS trigger_notificar_nueva_entrada ON registro_entradas;
DROP FUNCTION IF EXISTS notificar_nueva_entrada();

-- Crear función mejorada con manejo UTF-8
CREATE OR REPLACE FUNCTION notificar_nueva_entrada()
RETURNS TRIGGER AS $$
DECLARE
    miembro_data RECORD;
    payload_json TEXT;
BEGIN
    -- Obtener datos del miembro
    SELECT 
        m.id_miembro,
        m.nombres,
        m.apellido_paterno,
        m.apellido_materno,
        COALESCE(m.telefono, '') as telefono,
        COALESCE(m.email, '') as email,
        COALESCE(m.codigo_qr, '') as codigo_qr,
        m.activo,
        m.fecha_registro,
        COALESCE(m.fecha_nacimiento, '1900-01-01'::date) as fecha_nacimiento
    INTO miembro_data
    FROM miembros m
    WHERE m.id_miembro = NEW.id_miembro;
    
    -- Construir JSON con manejo de caracteres especiales
    payload_json := json_build_object(
        'id_entrada', NEW.id_entrada,
        'id_miembro', NEW.id_miembro,
        'tipo_acceso', NEW.tipo_acceso,
        'fecha_entrada', to_char(NEW.fecha_entrada, 'YYYY-MM-DD HH24:MI:SS'),
        'area_accedida', COALESCE(NEW.area_accedida, ''),
        'dispositivo_registro', COALESCE(NEW.dispositivo_registro, ''),
        'notas', COALESCE(NEW.notas, ''),
        'nombres', COALESCE(miembro_data.nombres, ''),
        'apellido_paterno', COALESCE(miembro_data.apellido_paterno, ''),
        'apellido_materno', COALESCE(miembro_data.apellido_materno, ''),
        'telefono', miembro_data.telefono,
        'email', miembro_data.email,
        'codigo_qr', miembro_data.codigo_qr,
        'activo', miembro_data.activo,
        'fecha_registro', to_char(miembro_data.fecha_registro, 'YYYY-MM-DD HH24:MI:SS'),
        'fecha_nacimiento', to_char(miembro_data.fecha_nacimiento, 'YYYY-MM-DD')
    )::text;
    
    -- Enviar notificación
    PERFORM pg_notify('nueva_entrada_canal', payload_json);
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Crear trigger
CREATE TRIGGER trigger_notificar_nueva_entrada
AFTER INSERT ON registro_entradas
FOR EACH ROW
WHEN (NEW.tipo_acceso = 'miembro')
EXECUTE FUNCTION notificar_nueva_entrada();
"""


def actualizar_trigger():
    print("🔌 Conectando a PostgreSQL HTF_DB...")
    
    try:
        conn = psycopg2.connect(**PG_CONFIG, client_encoding='UTF8')
        cursor = conn.cursor()
        
        print("📝 Actualizando función y trigger...")
        cursor.execute(TRIGGER_SQL)
        conn.commit()
        
        print("✅ Trigger actualizado correctamente")
        print("💡 La función ahora maneja correctamente caracteres UTF-8")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  ACTUALIZAR TRIGGER POSTGRESQL")
    print("="*60 + "\n")
    
    actualizar_trigger()
