#!/usr/bin/env python3
"""
Script para depurar el sincronización Supabase → PostgreSQL
Verifica qué datos devuelve Supabase y qué se inserta en PostgreSQL
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.supabase_service import SupabaseService
from database.postgres_manager import PostgresManager
from utils.config import Config
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cargar configuración
config = Config()
DB_CONFIG = {
    'host': config.DB_HOST,
    'port': config.DB_PORT,
    'database': config.DB_NAME,
    'user': config.DB_USER,
    'password': config.DB_PASSWORD
}

# Inicializar servicios
supabase = SupabaseService()
pg_manager = PostgresManager(DB_CONFIG)

try:
    # 1. Buscar notificación en Supabase
    codigo = "CASH-14"
    print(f"\n[DEBUG] Buscando codigo '{codigo}' en Supabase...")
    
    response = supabase.client.table('notificaciones_pos') \
        .select('id_notificacion, id_miembro, id_venta_digital, codigo_pago_generado, asunto, monto_pendiente') \
        .eq('codigo_pago_generado', codigo) \
        .eq('respondida', False) \
        .execute()
    
    print(f"\n[INFO] Respuesta de Supabase:")
    print(f"   Total de registros: {len(response.data)}")
    
    if response.data:
        item = response.data[0]
        print(f"\n   [OK] Datos de Supabase:")
        for key, value in item.items():
            print(f"      - {key}: {value} ({type(value).__name__})")
        
        # 2. Intentar sincronizar
        print(f"\n[ACTION] Sincronizando a PostgreSQL...")
        
        # Construir el diccionario igual a como lo hace escanear_codigo_pago()
        notif = {
            'id_notificacion': item['id_notificacion'],
            'id_miembro': item['id_miembro'],
            'id_venta_digital': item.get('id_venta_digital'),  # Exacto como en main_pos_window
            'tipo_notificacion': item.get('tipo_notificacion'),
            'asunto': item.get('asunto'),
            'monto_pendiente': item.get('monto_pendiente'),
            'codigo_pago_generado': item.get('codigo_pago_generado'),
        }
        
        print(f"\n   [INFO] Diccionario a sincronizar:")
        for key, value in notif.items():
            print(f"      - {key}: {value} ({type(value).__name__})")
        
        # Sincronizar
        exito = pg_manager.sincronizar_notificacion_supabase(
            notif['id_notificacion'],
            notif
        )
        
        if exito:
            print(f"\n   [OK] Sincronizacion exitosa")
            
            # 3. Verificar lo que quedó en PostgreSQL
            print(f"\n[ACTION] Verificando en PostgreSQL...")
            detalle = pg_manager.obtener_detalle_notificacion(item['id_notificacion'])
            
            if detalle:
                print(f"   [OK] Notificacion encontrada en PostgreSQL:")
                for key, value in detalle.items():
                    print(f"      - {key}: {value}")
            else:
                print(f"   [ERROR] Notificacion NO encontrada en PostgreSQL despues de sincronizar")
        else:
            print(f"\n   [ERROR] Error durante sincronizacion")
    else:
        print(f"   [ERROR] No se encontro en Supabase")

except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    pg_manager.close()

