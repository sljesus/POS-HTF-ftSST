#!/usr/bin/env python3
"""Test simple de miembros"""

from services.supabase_service import SupabaseService
from dotenv import load_dotenv
import os

load_dotenv()

service = SupabaseService()
print(f"Conectado: {service.is_connected}")
print(f"Using key: {service.key[:30]}...\n")

if not service.is_connected:
    print("❌ No conectado")
    exit(1)

# Test 1: Simple select
print("[1] Simple SELECT * FROM miembros:")
try:
    r1 = service.client.table('miembros').select('*').execute()
    print(f"    Registros: {len(r1.data)}")
except Exception as e:
    print(f"    ERROR: {e}")

# Test 2: Select con limit
print("\n[2] SELECT * FROM miembros LIMIT 5:")
try:
    r2 = service.client.table('miembros').select('*').limit(5).execute()
    print(f"    Registros: {len(r2.data)}")
except Exception as e:
    print(f"    ERROR: {e}")

# Test 3: Select con orden
print("\n[3] SELECT * FROM miembros ORDER BY nombres:")
try:
    r3 = service.client.table('miembros').select('*').order('nombres').execute()
    print(f"    Registros: {len(r3.data)}")
except Exception as e:
    print(f"    ERROR: {e}")

# Test 4: Con JOIN (como hace la interfaz)
print("\n[4] SELECT * FROM miembros WITH JOIN a asignaciones_activas:")
try:
    r4 = service.client.table('miembros')\
        .select('*,asignaciones_activas(fecha_fin,activa,cancelada)')\
        .execute()
    print(f"    Registros: {len(r4.data)}")
    if r4.data:
        print(f"    Primer registro: {r4.data[0].get('nombres')}")
except Exception as e:
    print(f"    ERROR: {e}")
