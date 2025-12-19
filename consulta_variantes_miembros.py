"""
Consultar miembros con filtros y sin restricciones
Asumiendo que hay datos como muestra la UI
"""

import os
import dotenv
from supabase import create_client

dotenv.load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("\n" + "="*70)
print("CONSULTA CON DIFERENTES VARIANTES")
print("="*70)

# [1] Select * sin límite
print("\n[1] SELECT * SIN LIMITE:")
try:
    response = client.table('miembros').select('*').execute()
    print(f"    Registros: {len(response.data)}")
    if response.data:
        for m in response.data[:3]:
            print(f"      - {m.get('id_miembro')}: {m.get('nombres')}")
except Exception as e:
    print(f"    ERROR: {e}")

# [2] Con limit muy alto
print("\n[2] SELECT * CON LIMIT 1000:")
try:
    response = client.table('miembros').select('*').limit(1000).execute()
    print(f"    Registros: {len(response.data)}")
    if response.data:
        for m in response.data[:3]:
            print(f"      - {m.get('id_miembro')}: {m.get('nombres')}")
except Exception as e:
    print(f"    ERROR: {e}")

# [3] Con orden
print("\n[3] SELECT * ORDENADO POR id_miembro:")
try:
    response = client.table('miembros').select('*').order('id_miembro', desc=False).execute()
    print(f"    Registros: {len(response.data)}")
    if response.data:
        for m in response.data[:5]:
            print(f"      - ID {m.get('id_miembro')}: {m.get('nombres')}")
except Exception as e:
    print(f"    ERROR: {e}")

# [4] Solo contar
print("\n[4] CONTAR REGISTROS:")
try:
    response = client.table('miembros').select('id_miembro', count='exact').execute()
    print(f"    Total: {response.count}")
except Exception as e:
    print(f"    ERROR: {e}")

# [5] Filtrar por activo
print("\n[5] FILTRAR POR activo=true:")
try:
    response = client.table('miembros').select('*').eq('activo', True).execute()
    print(f"    Registros activos: {len(response.data)}")
    if response.data:
        for m in response.data[:3]:
            print(f"      - {m.get('nombres')}")
except Exception as e:
    print(f"    ERROR: {e}")

# [6] Filtrar por activo negado
print("\n[6] FILTRAR POR activo!=true:")
try:
    response = client.table('miembros').select('*').neq('activo', True).execute()
    print(f"    Registros NO activos: {len(response.data)}")
except Exception as e:
    print(f"    ERROR: {e}")

# [7] Filtrar SIN activo
print("\n[7] FILTRAR POR is_null(activo):")
try:
    response = client.table('miembros').select('*').is_('activo', None).execute()
    print(f"    Registros con activo NULL: {len(response.data)}")
except Exception as e:
    print(f"    ERROR: {e}")

# [8] Todos sin filtro, con offset
print("\n[8] OFFSET 0, LIMIT 50:")
try:
    response = client.table('miembros').select('*').range(0, 49).execute()
    print(f"    Registros: {len(response.data)}")
    if response.data:
        print(f"    IDs: {[m.get('id_miembro') for m in response.data]}")
except Exception as e:
    print(f"    ERROR: {e}")

print("\n" + "="*70)
