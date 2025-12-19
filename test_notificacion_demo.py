#!/usr/bin/env python3
"""
Script de Demostración: Crear Notificación de Pago
Simula automáticamente el flujo de la app
"""

import os
import random
import string
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

from database.postgres_manager import PostgresManager

def generar_codigo_pago():
    """Generar código de pago único"""
    numeros = ''.join(random.choices(string.digits, k=4))
    return f"CASH-{numeros}"

def main():
    print("\n" + "="*70)
    print("DEMO: CREAR NOTIFICACIÓN DE PAGO")
    print("="*70 + "\n")
    
    # Conectar
    db_config = {
        'url': os.getenv('SUPABASE_URL'),
        'key': os.getenv('SUPABASE_ROLE_KEY') or os.getenv('SUPABASE_KEY'),
    }
    
    db = PostgresManager(db_config)
    print("✓ Conectado a Supabase\n")
    
    # Obtener un miembro al azar
    print("[1] Obteniendo miembros activos...")
    try:
        response = db.client.table('miembros').select('*').eq('activo', True).limit(10).execute()
        miembros = response.data or []
        
        if not miembros:
            print("❌ No hay miembros activos")
            return
        
        print(f"✓ Se encontraron {len(miembros)} miembros\n")
        
        # Seleccionar el primero
        miembro = miembros[0]
        print(f"[2] Miembro seleccionado:")
        print(f"    ID: {miembro['id_miembro']}")
        print(f"    Nombre: {miembro['nombres']} {miembro.get('apellido_paterno', '')}")
        print(f"    Teléfono: {miembro.get('telefono', 'N/A')}")
        print(f"    Email: {miembro.get('email', 'N/A')}\n")
        
        # Crear notificación
        print("[3] Creando notificación de pago...")
        
        codigo_pago = generar_codigo_pago()
        monto = round(random.uniform(50, 500), 2)
        fecha_vencimiento = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        notif_data = {
            'id_miembro': miembro['id_miembro'],
            'tipo_notificacion': 'pago_pendiente',
            'asunto': 'Pago de Membresía',
            'descripcion': f'Se requiere el pago de ${monto:.2f} para activar tu membresía',
            'monto_pendiente': monto,
            'fecha_vencimiento': fecha_vencimiento,
            'para_miembro': True,
            'para_recepcion': True,
            'codigo_pago_generado': codigo_pago
        }
        
        id_notif = db.crear_notificacion_pago(notif_data)
        
        if id_notif:
            print(f"\n✅ NOTIFICACIÓN CREADA EXITOSAMENTE\n")
            print(f"════════════════════════════════════════════════════════════════════")
            print(f"  ID Notificación:  {id_notif}")
            print(f"  Código de Pago:   {codigo_pago}")
            print(f"  Monto:            ${monto:.2f}")
            print(f"  Miembro:          {miembro['nombres']}")
            print(f"  Vencimiento:      {fecha_vencimiento}")
            print(f"════════════════════════════════════════════════════════════════════\n")
            
            # Buscar la notificación por código
            print("[4] Verificando notificación creada...\n")
            notif = db.buscar_notificacion_por_codigo_pago(codigo_pago)
            
            if notif:
                print(f"✓ Notificación encontrada en base de datos")
                print(f"  ID: {notif.get('id_notificacion')}")
                print(f"  Código: {notif.get('codigo_pago_generado')}")
                print(f"  Tipo: {notif.get('tipo_notificacion')}")
                print(f"  Respondida: {notif.get('respondida')}")
                print(f"\n✓ El flujo funciona correctamente!")
                print(f"\n💡 PRÓXIMO PASO: Ingresa el código '{codigo_pago}' en la app para procesar el pago\n")
            else:
                print(f"❌ No se encontró la notificación")
        else:
            print("❌ Error al crear la notificación")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
