#!/usr/bin/env python
"""
Script para verificar si existe el código CASH-8 en la tabla de notificaciones
"""

import os
import sys
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Agregar ruta del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.supabase_service import SupabaseService
from database.postgres_manager import PostgresManager
from utils.config import Config

def consultar_codigo_cash_8():
    """Consultar si existe CASH-8 en notificaciones"""
    
    print("\n" + "="*60)
    print("🔍 BUSCANDO CÓDIGO CASH-8 EN TABLA DE NOTIFICACIONES")
    print("="*60 + "\n")
    
    try:
        # Inicializar servicios
        config = Config()
        
        # Supabase
        supabase_service = SupabaseService()
        if not supabase_service.is_connected:
            print("❌ No hay conexión a Supabase")
            return
        
        print("✅ Conectado a Supabase\n")
        
        # Búsqueda en Supabase
        print("📋 Buscando en tabla 'notificaciones_pos'...")
        response = supabase_service.client.table('notificaciones_pos').select('*').eq(
            'codigo_pago_generado', 'CASH-8'
        ).execute()
        
        if response.data and len(response.data) > 0:
            print(f"✅ ENCONTRADO: {len(response.data)} registro(s) con CASH-8\n")
            
            for idx, notif in enumerate(response.data, 1):
                print(f"\n📌 Notificación #{idx}:")
                print(f"   ID Notificación: {notif.get('id_notificacion')}")
                print(f"   ID Miembro: {notif.get('id_miembro')}")
                print(f"   Código Pago: {notif.get('codigo_pago_generado')}")
                print(f"   Tipo: {notif.get('tipo_notificacion')}")
                print(f"   Asunto: {notif.get('asunto')}")
                print(f"   Monto: ${notif.get('monto_pendiente', 0)}")
                print(f"   Respondida: {notif.get('respondida')}")
                print(f"   Leída: {notif.get('leida')}")
                print(f"   Fecha Creación: {notif.get('creada_en')}")
                print(f"   Venta Digital ID: {notif.get('id_venta_digital')}")
                
                # Información de la venta digital si existe
                if notif.get('id_venta_digital'):
                    print(f"\n   📦 Venta Digital #{notif.get('id_venta_digital')}:")
                    try:
                        venta_response = supabase_service.client.table('ventas_digitales').select('*').eq(
                            'id_venta_digital', notif.get('id_venta_digital')
                        ).execute()
                        
                        if venta_response.data:
                            venta = venta_response.data[0]
                            print(f"      Estado: {venta.get('estado')}")
                            print(f"      Producto Digital: {venta.get('id_producto_digital')}")
                            print(f"      Fecha Inicio: {venta.get('fecha_inicio')}")
                            print(f"      Fecha Fin: {venta.get('fecha_fin')}")
                    except Exception as e:
                        print(f"      Error consultando venta: {e}")
        else:
            print("❌ NO ENCONTRADO: No existe código CASH-8 en Supabase\n")
        
        # También buscar en PostgreSQL local (si está disponible)
        print("\n" + "="*60)
        print("📋 Verificando en base de datos local...")
        
        db_config = config.get_postgres_config()
        pg_manager = PostgresManager(db_config)
        
        if pg_manager.connect():
            print("✅ Conectado a PostgreSQL local\n")
            
            try:
                response = pg_manager.client.table('notificaciones_pos').select('*').eq(
                    'codigo_pago_generado', 'CASH-8'
                ).execute()
                
                if response.data and len(response.data) > 0:
                    print(f"✅ ENCONTRADO: {len(response.data)} registro(s) en local\n")
                    
                    for idx, notif in enumerate(response.data, 1):
                        print(f"\n📌 Notificación Local #{idx}:")
                        print(f"   ID Notificación: {notif.get('id_notificacion')}")
                        print(f"   ID Miembro: {notif.get('id_miembro')}")
                        print(f"   Respondida: {notif.get('respondida')}")
                else:
                    print("❌ NO ENCONTRADO en base de datos local\n")
            except Exception as e:
                print(f"⚠️  Error consultando PostgreSQL: {e}\n")
        else:
            print("⚠️  No se pudo conectar a PostgreSQL local\n")
        
        print("\n" + "="*60)
        print("✅ Consulta completada")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    consultar_codigo_cash_8()
