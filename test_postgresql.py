"""
Script alternativo para probar conexión directa a PostgreSQL
sin usar la API REST de Supabase
"""

import os
import sys
import logging
import psycopg2
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_postgresql_connection():
    """Probar conexión directa a PostgreSQL de Supabase"""
    print("\n" + "="*60)
    print("🐘 PROBANDO CONEXIÓN DIRECTA A POSTGRESQL")
    print("="*60)
    
    try:
        # Cargar variables de entorno
        load_dotenv()
        
        # Parámetros de conexión
        connection_params = {
            'host': os.getenv('host', 'db.ufnmqxyvrfionysjeiko.supabase.co'),
            'port': os.getenv('port', '5432'),
            'database': os.getenv('dbname', 'postgres'),
            'user': os.getenv('user', 'postgres'),
            'password': os.getenv('password', 'MFG3103@gmail')
        }
        
        print(f"🔗 Conectando a: {connection_params['host']}")
        print(f"📁 Base de datos: {connection_params['database']}")
        print(f"👤 Usuario: {connection_params['user']}")
        
        # Intentar conexión
        conn = psycopg2.connect(**connection_params)
        cursor = conn.cursor()
        
        print("✅ Conexión PostgreSQL exitosa!")
        
        # Probar consultas básicas
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"📊 Versión PostgreSQL: {version[:50]}...")
        
        # Verificar si existe tabla usuarios
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'usuarios';
        """)
        
        if cursor.fetchone():
            print("✅ Tabla 'usuarios' existe en Supabase")
            
            # Contar usuarios
            cursor.execute("SELECT COUNT(*) FROM usuarios;")
            count = cursor.fetchone()[0]
            print(f"👥 Usuarios en Supabase: {count}")
            
        else:
            print("⚠️ Tabla 'usuarios' no existe - necesita crearse")
        
        # Cerrar conexión
        cursor.close()
        conn.close()
        print("✅ Conexión cerrada correctamente")
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Error de PostgreSQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 PROBANDO CONEXIÓN DIRECTA A SUPABASE")
    
    # Instalar psycopg2 si no está disponible
    try:
        import psycopg2
    except ImportError:
        print("❌ psycopg2 no está instalado")
        print("💡 Instala con: pip install psycopg2-binary")
        return
    
    success = test_postgresql_connection()
    
    print("\n" + "="*60)
    print("🎯 RESULTADO")
    print("="*60)
    
    if success:
        print("✅ ¡Conexión a Supabase funcional!")
        print("💡 Puedes usar PostgreSQL directo mientras obtienes la anon key")
    else:
        print("❌ No se pudo conectar")
        print("🔍 Verifica las credenciales en el archivo .env")

if __name__ == "__main__":
    main()