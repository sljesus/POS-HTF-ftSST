#!/usr/bin/env python3
"""Test del catálogo de miembros desde Supabase"""

from services.supabase_service import SupabaseService
from dotenv import load_dotenv
import os

load_dotenv()

print("\n" + "="*70)
print("TEST: CATÁLOGO DE MIEMBROS DESDE SUPABASE")
print("="*70 + "\n")

# Crear servicio Supabase
service = SupabaseService()

print(f"✓ Conectado: {service.is_connected}")
print(f"✓ URL: {service.url[:40]}...")
print(f"✓ Key (primeros 30): {service.key[:30]}...")

if not service.is_connected:
    print("\n❌ ERROR: No hay conexión a Supabase")
    exit(1)

# Intentar cargar miembros como lo hace la interfaz
print("\n[1] Consultando tabla 'miembros' con JOIN a 'asignaciones_activas'...")
try:
    response = service.client.table('miembros')\
        .select('''
            *,
            asignaciones_activas(
                fecha_fin,
                activa,
                cancelada,
                ca_productos_digitales(nombre),
                lockers(numero)
            )
        ''')\
        .order('nombres')\
        .execute()
    
    rows = response.data if response.data else []
    print(f"✓ Registros obtenidos: {len(rows)}\n")
    
    if rows:
        for idx, m in enumerate(rows[:5], 1):
            print(f"{idx}. {m.get('nombres', 'N/A')} {m.get('apellido_paterno', 'N/A')}")
            asig = m.get('asignaciones_activas', [])
            if asig:
                print(f"   └─ Asignaciones: {len(asig)}")
    else:
        print("⚠️  No hay registros de miembros")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
