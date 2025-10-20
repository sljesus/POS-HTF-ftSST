"""
Script de prueba para verificar conexión con Supabase
y sincronización de usuario admin
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
from services.supabase_service import SupabaseService
from utils.config import Config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_database_connection():
    """Probar conexión y estructura de base de datos local"""
    print("\n" + "="*60)
    print("🗄️  PROBANDO BASE DE DATOS LOCAL (SQLite)")
    print("="*60)
    
    try:
        # Inicializar base de datos
        db_manager = DatabaseManager()
        
        if db_manager.initialize_database():
            print("✅ Base de datos SQLite inicializada correctamente")
            
            # Probar usuario admin
            admin_user = db_manager.test_supabase_sync()
            if admin_user:
                print(f"✅ Usuario admin encontrado:")
                print(f"   - ID: {admin_user['id_usuario']}")
                print(f"   - Usuario: {admin_user['nombre_usuario']}")
                print(f"   - Nombre: {admin_user['nombre_completo']}")
                print(f"   - Rol: {admin_user['rol']}")
                
                # Probar autenticación
                auth_result = db_manager.authenticate_user('admin', 'admin123')
                if auth_result:
                    print("✅ Autenticación local exitosa")
                else:
                    print("❌ Error en autenticación local")
                    
                return db_manager, admin_user
            else:
                print("❌ Usuario admin no encontrado")
                return None, None
        else:
            print("❌ Error inicializando base de datos")
            return None, None
            
    except Exception as e:
        print(f"❌ Error en base de datos: {e}")
        return None, None

def test_supabase_connection():
    """Probar conexión con Supabase"""
    print("\n" + "="*60)
    print("☁️  PROBANDO CONEXIÓN CON SUPABASE")
    print("="*60)
    
    try:
        # Cargar configuración
        config = Config()
        config.validate_config()
        
        # Inicializar servicio
        supabase_service = SupabaseService()
        
        # Probar conexión
        if supabase_service.test_connection_with_user_sync():
            print("✅ Conexión a Supabase exitosa")
            
            # Mostrar estado
            status = supabase_service.get_connection_status()
            print(f"   - URL configurada: {status['url_configured']}")
            print(f"   - Key configurada: {status['key_configured']}")
            print(f"   - Supabase disponible: {status['supabase_available']}")
            print(f"   - Conectado: {status['connected']}")
            
            return supabase_service
        else:
            print("❌ Error conectando a Supabase")
            return None
            
    except Exception as e:
        print(f"❌ Error en Supabase: {e}")
        return None

def test_user_sync(db_manager, supabase_service, admin_user):
    """Probar sincronización de usuario admin"""
    print("\n" + "="*60)
    print("🔄 PROBANDO SINCRONIZACIÓN DE USUARIO")
    print("="*60)
    
    try:
        if not supabase_service or not admin_user:
            print("❌ No se puede probar sincronización - servicios no disponibles")
            return False
        
        # Sincronizar usuario admin
        supabase_id = supabase_service.sync_admin_user_to_supabase(admin_user)
        
        if supabase_id:
            print(f"✅ Usuario sincronizado con Supabase ID: {supabase_id}")
            
            # Probar autenticación en Supabase
            password_hash = db_manager.hash_password('admin123')
            supabase_auth = supabase_service.authenticate_user_supabase('admin', password_hash)
            
            if supabase_auth:
                print("✅ Autenticación en Supabase exitosa")
                print(f"   - ID Supabase: {supabase_auth['supabase_id']}")
                print(f"   - Nombre completo: {supabase_auth['full_name']}")
                return True
            else:
                print("❌ Error en autenticación Supabase")
                return False
        else:
            print("❌ Error sincronizando usuario")
            return False
            
    except Exception as e:
        print(f"❌ Error en sincronización: {e}")
        return False

def test_products_sync(db_manager, supabase_service):
    """Probar sincronización de productos"""
    print("\n" + "="*60)
    print("📦 PROBANDO PRODUCTOS LOCAL")
    print("="*60)
    
    try:
        # Obtener productos locales
        productos = db_manager.get_all_products()
        print(f"✅ Productos encontrados: {len(productos)}")
        
        for producto in productos[:3]:  # Mostrar primeros 3
            print(f"   - {producto['codigo_interno']}: {producto['nombre']} (${producto['precio_venta']})")
        
        # Obtener inventario
        inventario = db_manager.get_inventory_status()
        print(f"✅ Items en inventario: {len(inventario)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error obteniendo productos: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🚀 INICIANDO PRUEBAS DE CONEXIÓN HTF GIMNASIO POS")
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Pruebas
    db_manager, admin_user = test_database_connection()
    supabase_service = test_supabase_connection()
    
    if db_manager and admin_user:
        test_user_sync(db_manager, supabase_service, admin_user)
        test_products_sync(db_manager, supabase_service)
    
    print("\n" + "="*60)
    print("🎯 RESUMEN DE PRUEBAS")
    print("="*60)
    print(f"✅ Base de datos local: {'OK' if db_manager else 'ERROR'}")
    print(f"✅ Usuario admin: {'OK' if admin_user else 'ERROR'}")
    print(f"✅ Conexión Supabase: {'OK' if supabase_service else 'ERROR'}")
    print("="*60)
    
    if db_manager:
        db_manager.close_connection()

if __name__ == "__main__":
    main()