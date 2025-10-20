"""
Servicio de Supabase para sincronización de datos
"""

import logging
from datetime import datetime
import os

# Nota: Se requiere instalar supabase: pip install supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logging.warning("Supabase no está instalado. Funcionando en modo offline.")

class SupabaseService:
    def __init__(self, url=None, key=None):
        self.url = url or os.getenv('SUPABASE_URL')
        self.key = key or os.getenv('SUPABASE_KEY')
        self.client = None
        self.is_connected = False
        
        if SUPABASE_AVAILABLE and self.url and self.key:
            self.connect()
    
    def connect(self):
        """Conectar a Supabase"""
        try:
            if not SUPABASE_AVAILABLE:
                logging.warning("Supabase no disponible")
                return False
            
            self.client = create_client(self.url, self.key)
            
            # Probar conexión con tabla usuarios (no users)
            response = self.client.table('usuarios').select('id_usuario').limit(1).execute()
            self.is_connected = True
            logging.info("Conexión a Supabase establecida")
            return True
            
        except Exception as e:
            logging.error(f"Error conectando a Supabase: {e}")
            self.is_connected = False
            return False
    
    def test_connection_with_user_sync(self):
        """Probar conexión y sincronizar usuario admin"""
        if not self.is_connected:
            logging.warning("No hay conexión a Supabase")
            return False
        
        try:
            # Probar conexión básica
            response = self.client.table('usuarios').select('id_usuario').limit(1).execute()
            
            logging.info("✅ Conexión a Supabase exitosa")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error probando conexión: {e}")
            return False
    
    def sync_admin_user_to_supabase(self, admin_data):
        """Sincronizar usuario admin con Supabase"""
        if not self.is_connected:
            logging.warning("No hay conexión para sincronizar usuario admin")
            return False
        
        try:
            # Verificar si el usuario admin ya existe en Supabase
            response = self.client.table('usuarios').select('*').eq('nombre_usuario', 'admin').execute()
            
            user_data = {
                'nombre_usuario': admin_data['nombre_usuario'],
                'contrasenia': admin_data['contrasenia'],  # Ya está hasheada
                'nombre_completo': admin_data['nombre_completo'],
                'rol': admin_data['rol'],
                'activo': bool(admin_data['activo']),
                'fecha_creacion': admin_data['fecha_creacion']
            }
            
            if response.data:
                # Usuario existe, actualizar
                supabase_user = response.data[0]
                update_response = self.client.table('usuarios').update(user_data).eq('id_usuario', supabase_user['id_usuario']).execute()
                
                if update_response.data:
                    logging.info(f"✅ Usuario admin actualizado en Supabase: ID {supabase_user['id_usuario']}")
                    return supabase_user['id_usuario']
            else:
                # Usuario no existe, crear
                insert_response = self.client.table('usuarios').insert(user_data).execute()
                
                if insert_response.data:
                    supabase_id = insert_response.data[0]['id_usuario']
                    logging.info(f"✅ Usuario admin creado en Supabase: ID {supabase_id}")
                    return supabase_id
            
            return None
            
        except Exception as e:
            logging.error(f"❌ Error sincronizando usuario admin: {e}")
            return False
    
    def authenticate_user_supabase(self, username, password_hash):
        """Autenticar usuario contra Supabase usando hash"""
        if not self.is_connected:
            return None
        
        try:
            # Buscar usuario por username y password hash
            response = self.client.table('usuarios').select('*').eq('nombre_usuario', username).eq('contrasenia', password_hash).eq('activo', True).execute()
            
            if response.data:
                user = response.data[0]
                logging.info(f"✅ Usuario autenticado en Supabase: {username}")
                return {
                    'id': user['id_usuario'],
                    'username': user['nombre_usuario'],
                    'full_name': user['nombre_completo'],
                    'role': user['rol'],
                    'supabase_id': user['id_usuario']
                }
            
            logging.warning(f"❌ Usuario no encontrado en Supabase: {username}")
            return None
            
        except Exception as e:
            logging.error(f"❌ Error autenticando en Supabase: {e}")
            return None
    
    def sync_products_to_supabase(self, products):
        """Sincronizar productos locales a Supabase"""
        if not self.is_connected:
            logging.warning("No hay conexión a Supabase para sincronizar")
            return False
        
        try:
            for product in products:
                if product.get('needs_sync'):
                    # Determinar tabla según tipo de producto
                    table_name = 'ca_productos_varios' if product['tipo'] == 'varios' else 'ca_suplementos'
                    
                    # Preparar datos para Supabase
                    product_data = {
                        'codigo_interno': product['codigo_interno'],
                        'nombre': product['nombre'],
                        'descripcion': product['descripcion'],
                        'precio_venta': product['precio_venta'],
                        'activo': product['activo'],
                        'updated_at': datetime.now().isoformat()
                    }
                    
                    if product.get('supabase_id'):
                        # Actualizar producto existente
                        response = self.client.table(table_name).update(product_data).eq('id_producto', product['supabase_id']).execute()
                    else:
                        # Crear nuevo producto
                        response = self.client.table(table_name).insert(product_data).execute()
                        
            logging.info("Productos sincronizados con Supabase")
            return True
            
        except Exception as e:
            logging.error(f"Error sincronizando productos: {e}")
            return False
    
    def sync_products_from_supabase(self):
        """Obtener productos desde Supabase"""
        if not self.is_connected:
            return []
        
        try:
            productos = []
            
            # Obtener productos varios
            response_varios = self.client.table('ca_productos_varios').select('*').eq('activo', True).execute()
            productos.extend(response_varios.data)
            
            # Obtener suplementos  
            response_suplementos = self.client.table('ca_suplementos').select('*').eq('activo', True).execute()
            productos.extend(response_suplementos.data)
            
            logging.info(f"Obtenidos {len(productos)} productos desde Supabase")
            return productos
            
        except Exception as e:
            logging.error(f"Error obteniendo productos desde Supabase: {e}")
            return []
    
    def sync_sales_to_supabase(self, sales):
        """Sincronizar ventas locales a Supabase"""
        if not self.is_connected:
            logging.warning("No hay conexión a Supabase para sincronizar ventas")
            return False
        
        try:
            for sale in sales:
                if sale.get('needs_sync'):
                    sale_data = {
                        'numero_ticket': sale['numero_ticket'],
                        'id_usuario': sale['id_usuario'],
                        'total': sale['total'],
                        'impuestos': sale['impuestos'],
                        'descuento': sale['descuento'],
                        'metodo_pago': sale['metodo_pago'],
                        'estado': sale['estado'],
                        'fecha': sale['fecha']
                    }
                    
                    response = self.client.table('ventas').insert(sale_data).execute()
                    
            logging.info("Ventas sincronizadas con Supabase")
            return True
            
        except Exception as e:
            logging.error(f"Error sincronizando ventas: {e}")
            return False
    
    def test_connection(self):
        """Probar conexión a Supabase"""
        return self.is_connected
    
    def get_connection_status(self):
        """Obtener estado de conexión"""
        return {
            'connected': self.is_connected,
            'supabase_available': SUPABASE_AVAILABLE,
            'url_configured': bool(self.url),
            'key_configured': bool(self.key)
        }