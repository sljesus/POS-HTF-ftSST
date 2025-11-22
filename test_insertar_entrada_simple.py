"""
Script simple para insertar entrada de prueba en PostgreSQL
Crea miembro si no existe y registra entrada
"""

import psycopg2
from datetime import datetime

# Configuración
PG_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'HTF_DB',
    'user': 'postgres',
    'password': 'postgres'
}


def main():
    print("🔌 Conectando a PostgreSQL HTF_DB...")
    
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        
        # Verificar si existe tabla miembros
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'miembros'
            )
        """)
        
        if not cursor.fetchone()[0]:
            print("❌ La tabla 'miembros' no existe en la base de datos")
            conn.close()
            return
        
        # Buscar o crear miembro de prueba
        cursor.execute("SELECT id_miembro FROM miembros WHERE email = 'test@htf.com' LIMIT 1")
        resultado = cursor.fetchone()
        
        if resultado:
            id_miembro = resultado[0]
            print(f"✅ Usando miembro existente ID: {id_miembro}")
        else:
            print("📝 Creando miembro de prueba...")
            cursor.execute("""
                INSERT INTO miembros 
                (nombres, apellido_paterno, apellido_materno, telefono, email, 
                 fecha_registro, activo, codigo_qr, fecha_nacimiento)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id_miembro
            """, (
                'Juan Carlos',
                'Pérez',
                'García',
                '5551234567',
                'test@htf.com',
                datetime.now(),
                True,
                'HTF001',
                '1990-01-01'
            ))
            
            id_miembro = cursor.fetchone()[0]
            conn.commit()
            print(f"✅ Miembro creado con ID: {id_miembro}")
        
        # Insertar entrada
        print(f"\n📝 Registrando entrada para miembro ID {id_miembro}...")
        cursor.execute("""
            INSERT INTO registro_entradas 
            (id_miembro, tipo_acceso, fecha_entrada, area_accedida, dispositivo_registro, notas)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id_entrada
        """, (
            id_miembro,
            'miembro',
            datetime.now(),
            'Gimnasio',
            'TEST_SCRIPT',
            'Entrada de prueba - Test notificación'
        ))
        
        id_entrada = cursor.fetchone()[0]
        conn.commit()
        
        print(f"✅ Entrada registrada con ID: {id_entrada}")
        print(f"\n🔔 NOTIFICACIÓN ENVIADA al canal 'nueva_entrada_canal'")
        print(f"💡 Si tienes el listener o el POS abierto, deberías ver la notificación\n")
        
        cursor.close()
        conn.close()
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ Error de conexión: {e}")
        print("\n💡 Verifica:")
        print("   - PostgreSQL está corriendo")
        print("   - La base de datos HTF_DB existe")
        print("   - Usuario y contraseña correctos")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  INSERTAR ENTRADA DE PRUEBA")
    print("="*60 + "\n")
    
    main()
