"""
Script para sincronizar el usuario admin con Supabase
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
from services.supabase_service import SupabaseService

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def sync_admin_user():
    """Sincronizar usuario admin con Supabase"""
    print("🔄 SINCRONIZANDO USUARIO ADMIN CON SUPABASE")
    print("="*60)
    
    try:
        # Inicializar servicios
        db_manager = DatabaseManager()
        db_manager.initialize_database()
        
        supabase_service = SupabaseService()
        
        if not supabase_service.test_connection():
            print("❌ No hay conexión con Supabase")
            return False
        
        # Obtener usuario admin local
        cursor = db_manager.connection.cursor()
        cursor.execute('''
            SELECT id_usuario, nombre_usuario, contrasenia, nombre_completo, rol, 
                   activo, fecha_creacion
            FROM usuarios WHERE nombre_usuario = 'admin'
        ''')
        
        admin_user = cursor.fetchone()
        if not admin_user:
            print("❌ Usuario admin no encontrado en base local")
            return False
        
        print(f"✅ Usuario admin encontrado: {admin_user['nombre_completo']}")
        
        # Verificar si ya existe en Supabase
        try:
            response = supabase_service.client.table('usuarios').select('*').eq('nombre_usuario', 'admin').execute()
            
            user_data = {
                'nombre_usuario': admin_user['nombre_usuario'],
                'contrasenia': admin_user['contrasenia'],
                'nombre_completo': admin_user['nombre_completo'],
                'rol': admin_user['rol'],
                'activo': bool(admin_user['activo']),
                'fecha_creacion': admin_user['fecha_creacion']
            }
            
            if response.data:
                # Usuario existe, actualizar
                supabase_user = response.data[0]
                print(f"👤 Usuario admin ya existe en Supabase (ID: {supabase_user['id_usuario']})")
                
                update_response = supabase_service.client.table('usuarios').update(user_data).eq('id_usuario', supabase_user['id_usuario']).execute()
                
                if update_response.data:
                    print("✅ Usuario admin actualizado en Supabase")
                    
                    # Actualizar referencia local
                    cursor.execute('''
                        UPDATE usuarios SET supabase_id = ?, needs_sync = 0
                        WHERE id_usuario = ?
                    ''', (supabase_user['id_usuario'], admin_user['id_usuario']))
                    db_manager.connection.commit()
                    
                    return True
            else:
                # Usuario no existe, crear
                print("🆕 Creando usuario admin en Supabase...")
                
                insert_response = supabase_service.client.table('usuarios').insert(user_data).execute()
                
                if insert_response.data:
                    supabase_id = insert_response.data[0]['id_usuario']
                    print(f"✅ Usuario admin creado en Supabase (ID: {supabase_id})")
                    
                    # Actualizar referencia local
                    cursor.execute('''
                        UPDATE usuarios SET supabase_id = ?, needs_sync = 0
                        WHERE id_usuario = ?
                    ''', (supabase_id, admin_user['id_usuario']))
                    db_manager.connection.commit()
                    
                    return True
                else:
                    print("❌ Error creando usuario en Supabase")
                    return False
                    
        except Exception as e:
            print(f"❌ Error en sincronización: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False
    
    finally:
        if 'db_manager' in locals():
            db_manager.close_connection()

def test_authentication():
    """Probar autenticación en ambos sistemas"""
    print("\n🔐 PROBANDO AUTENTICACIÓN COMPLETA")
    print("="*60)
    
    try:
        # Probar autenticación local
        db_manager = DatabaseManager()
        db_manager.initialize_database()
        
        local_auth = db_manager.authenticate_user('admin', 'admin123')
        if local_auth:
            print("✅ Autenticación local exitosa")
        else:
            print("❌ Error en autenticación local")
            return False
        
        # Probar autenticación en Supabase
        supabase_service = SupabaseService()
        if supabase_service.test_connection():
            password_hash = db_manager.hash_password('admin123')
            supabase_auth = supabase_service.authenticate_user_supabase('admin', password_hash)
            
            if supabase_auth:
                print("✅ Autenticación en Supabase exitosa")
                print(f"   - ID Local: {local_auth['id']}")
                print(f"   - ID Supabase: {supabase_auth['supabase_id']}")
                return True
            else:
                print("❌ Error en autenticación Supabase")
                return False
        else:
            print("❌ No hay conexión con Supabase para autenticación")
            return False
            
    except Exception as e:
        print(f"❌ Error en autenticación: {e}")
        return False
    
    finally:
        if 'db_manager' in locals():
            db_manager.close_connection()

def main():
    """Función principal"""
    print("🚀 SINCRONIZANDO USUARIO ADMIN CON SUPABASE")
    
    load_dotenv()
    
    # Sincronizar usuario
    sync_success = sync_admin_user()
    
    if sync_success:
        # Probar autenticación
        auth_success = test_authentication()
        
        print("\n🎯 RESULTADO FINAL")
        print("="*60)
        print(f"✅ Sincronización: {'OK' if sync_success else 'ERROR'}")
        print(f"✅ Autenticación: {'OK' if auth_success else 'ERROR'}")
        
        if sync_success and auth_success:
            print("🎉 ¡Usuario admin completamente sincronizado!")
            print("💡 Ya puedes usar el POS con sincronización completa")
        
    else:
        print("\n❌ Error en sincronización")

if __name__ == "__main__":
    main()