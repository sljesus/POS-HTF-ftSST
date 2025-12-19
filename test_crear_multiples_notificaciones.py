#!/usr/bin/env python3
"""
Script para Crear Múltiples Notificaciones de Prueba
Crea N notificaciones para probar el sistema completo
"""

import os
import random
import string
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

load_dotenv()

from database.postgres_manager import PostgresManager

def generar_codigo_pago():
    """Generar código de pago único"""
    numeros = ''.join(random.choices(string.digits, k=4))
    return f"CASH-{numeros}"

def main():
    print("\n" + "="*70)
    print("CREAR MÚLTIPLES NOTIFICACIONES DE PRUEBA")
    print("="*70 + "\n")
    
    # Conectar
    db_config = {
        'url': os.getenv('SUPABASE_URL'),
        'key': os.getenv('SUPABASE_ROLE_KEY') or os.getenv('SUPABASE_KEY'),
    }
    
    db = PostgresManager(db_config)
    print("✓ Conectado a Supabase\n")
    
    # Cantidad de notificaciones
    cantidad = input("¿Cuántas notificaciones deseas crear? (default: 3): ").strip()
    cantidad = int(cantidad) if cantidad.isdigit() else 3
    
    # Obtener miembros
    print(f"\nObteniendo miembros...")
    try:
        response = db.client.table('miembros').select('*').eq('activo', True).limit(20).execute()
        miembros = response.data or []
        
        if not miembros:
            print("❌ No hay miembros activos")
            return
        
        print(f"✓ Se encontraron {len(miembros)} miembros\n")
        
        # Crear notificaciones
        codigos_creados = []
        
        print(f"{'─'*70}")
        print(f"{'Creando':<20} {'Código':<15} {'Monto':<15} {'Miembro':<20}")
        print(f"{'─'*70}")
        
        for i in range(cantidad):
            # Miembro al azar
            miembro = random.choice(miembros)
            
            # Datos aleatorios
            codigo_pago = generar_codigo_pago()
            monto = round(random.uniform(50, 500), 2)
            tipo = random.choice(['pago_pendiente', 'membresia_pendiente', 'visita_pendiente'])
            
            # Crear notificación
            notif_data = {
                'id_miembro': miembro['id_miembro'],
                'tipo_notificacion': tipo,
                'asunto': f'{tipo.replace("_", " ").title()}',
                'descripcion': f'Pago de ${monto:.2f} requerido',
                'monto_pendiente': monto,
                'fecha_vencimiento': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
                'para_miembro': True,
                'para_recepcion': True,
                'codigo_pago_generado': codigo_pago
            }
            
            id_notif = db.crear_notificacion_pago(notif_data)
            
            if id_notif:
                codigos_creados.append((codigo_pago, monto, miembro['nombres']))
                print(f"{f'✓ #{i+1}':<20} {codigo_pago:<15} ${monto:<14.2f} {miembro['nombres']:<20}")
            else:
                print(f"{'✗ #{i+1}':<20} {'ERROR':<15}")
        
        # Resumen
        print(f"{'─'*70}\n")
        print(f"✅ Se crearon {len(codigos_creados)} notificaciones exitosamente\n")
        
        print("CÓDIGOS DE PAGO PARA PRUEBA:")
        print(f"{'─'*70}")
        for codigo, monto, miembro in codigos_creados:
            print(f"  {codigo}  →  ${monto:.2f} ({miembro})")
        
        print(f"\n💡 Copia y pega estos códigos en la app para probar el escaneo\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
