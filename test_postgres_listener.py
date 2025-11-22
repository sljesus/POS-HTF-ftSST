"""
Script de prueba para verificar PostgreSQL LISTEN/NOTIFY
Escucha notificaciones del canal 'nueva_entrada_canal'
"""

import psycopg2
import psycopg2.extensions
import select
import json
from datetime import datetime

# Configuración de conexión (ajustar según tu configuración)
PG_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'HTF_DB',
    'user': 'postgres',
    'password': 'postgres'
}

CHANNEL = 'nueva_entrada_canal'


def escuchar_notificaciones():
    """Escuchar notificaciones de PostgreSQL"""
    print(f"🔌 Conectando a PostgreSQL en {PG_CONFIG['host']}:{PG_CONFIG['port']}...")
    
    try:
        # Conectar
        conn = psycopg2.connect(**PG_CONFIG)
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = conn.cursor()
        cursor.execute(f"LISTEN {CHANNEL};")
        
        print(f"✅ Conexión establecida")
        print(f"👂 Escuchando canal: {CHANNEL}")
        print(f"⏳ Esperando notificaciones... (Ctrl+C para salir)\n")
        
        while True:
            # Esperar notificaciones
            if select.select([conn], [], [], 5) == ([], [], []):
                # Timeout cada 5 segundos
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Esperando... (sin notificaciones)")
            else:
                conn.poll()
                while conn.notifies:
                    notify = conn.notifies.pop(0)
                    
                    print("\n" + "="*60)
                    print(f"📨 NOTIFICACIÓN RECIBIDA")
                    print("="*60)
                    print(f"Canal: {notify.channel}")
                    print(f"PID: {notify.pid}")
                    print(f"Payload (raw): {notify.payload[:200]}...")
                    
                    # Parsear JSON
                    try:
                        datos = json.loads(notify.payload)
                        print(f"\n📋 Datos parseados:")
                        print(f"  ID Entrada: {datos.get('id_entrada')}")
                        print(f"  ID Miembro: {datos.get('id_miembro')}")
                        print(f"  Nombre: {datos.get('nombres')} {datos.get('apellido_paterno')}")
                        print(f"  Fecha: {datos.get('fecha_entrada')}")
                        print(f"  Área: {datos.get('area_accedida')}")
                        print(f"  Tipo: {datos.get('tipo_acceso')}")
                    except json.JSONDecodeError as e:
                        print(f"❌ Error parseando JSON: {e}")
                    
                    print("="*60 + "\n")
                    
    except psycopg2.OperationalError as e:
        print(f"\n❌ Error de conexión: {e}")
        print("\n💡 Verifica:")
        print(f"   - PostgreSQL está corriendo en {PG_CONFIG['host']}:{PG_CONFIG['port']}")
        print(f"   - La base de datos '{PG_CONFIG['database']}' existe")
        print(f"   - El usuario '{PG_CONFIG['user']}' tiene permisos")
        print(f"   - La contraseña es correcta")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Detenido por el usuario")
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            print("🔌 Conexión cerrada")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  PRUEBA DE POSTGRESQL LISTEN/NOTIFY")
    print("="*60 + "\n")
    
    escuchar_notificaciones()
