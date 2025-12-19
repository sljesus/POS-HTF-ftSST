"""
Script para consultar Supabase directamente SIN PostgresManager
Usando supabase-py directamente
"""

import os
import dotenv
from supabase import create_client

dotenv.load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

print("\n" + "="*70)
print("CONSULTA DIRECTA A SUPABASE - SIN PostgresManager")
print("="*70)

print(f"\nURL: {SUPABASE_URL}")
print(f"KEY: {SUPABASE_KEY[:20]}...")

# Conectar directamente
client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("\n[1] CONSULTANDO TABLA: miembros")
try:
    response = client.table('miembros').select('*').limit(100).execute()
    print(f"    Status: OK")
    print(f"    Total de registros: {len(response.data) if response.data else 0}")
    
    if response.data:
        print(f"\n    MIEMBROS ENCONTRADOS:")
        for i, miembro in enumerate(response.data, 1):
            print(f"\n    {i}. {miembro}")
    else:
        print(f"    No hay registros")
        
except Exception as e:
    print(f"    ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n[2] CONSULTANDO TABLA: ca_productos_digitales")
try:
    response = client.table('ca_productos_digitales').select('*').limit(5).execute()
    print(f"    Status: OK")
    print(f"    Total de registros: {len(response.data) if response.data else 0}")
    
    if response.data:
        print(f"\n    PRIMEROS 5 PRODUCTOS:")
        for i, prod in enumerate(response.data, 1):
            print(f"\n    {i}. {prod.get('nombre')} - ${prod.get('precio_venta')}")
    
except Exception as e:
    print(f"    ERROR: {e}")

print("\n" + "="*70)
