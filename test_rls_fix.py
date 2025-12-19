#!/usr/bin/env python3
"""Test RLS con ROLE_KEY"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ROLE_KEY = os.getenv('SUPABASE_ROLE_KEY')

print(f"URL: {SUPABASE_URL[:30]}...")
print(f"ROLE_KEY: {SUPABASE_ROLE_KEY[:30] if SUPABASE_ROLE_KEY else 'NO ENCONTRADA'}...")

if not SUPABASE_ROLE_KEY:
    print("ERROR: SUPABASE_ROLE_KEY no encontrada")
    sys.exit(1)

try:
    from supabase import create_client
    client = create_client(SUPABASE_URL, SUPABASE_ROLE_KEY)
    
    print("\n✓ Cliente creado")
    
    # Intentar consulta simple
    response = client.table('miembros').select('id_miembro, nombres').limit(5).execute()
    
    print(f"✓ Consulta exitosa: {len(response.data)} registros")
    for row in response.data:
        print(f"  - ID {row['id_miembro']}: {row['nombres']}")
        
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
