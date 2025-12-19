"""
Consultar miembros usando SECRET KEY (SERVICE_ROLE_KEY)
Esto bypasea las políticas RLS
"""

import os
import dotenv
from supabase import create_client

dotenv.load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_KEY')
SUPABASE_SECRET_KEY = os.getenv('SUPABASE_ROLE_KEY')

print("\n" + "="*70)
print("COMPARACIÓN: ANON KEY vs SECRET KEY")
print("="*70)

# [1] Con ANON KEY (actual)
print("\n[1] CON ANON KEY (actual):")
try:
    client_anon = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    response = client_anon.table('miembros').select('*').execute()
    print(f"    Registros: {len(response.data)}")
except Exception as e:
    print(f"    ERROR: {e}")

# [2] Con SECRET KEY (si existe)
print("\n[2] CON SECRET KEY (SERVICE_ROLE_KEY):")
if SUPABASE_SECRET_KEY:
    try:
        client_secret = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)
        response = client_secret.table('miembros').select('*').execute()
        print(f"    Registros: {len(response.data)}")
        if response.data:
            for m in response.data[:5]:
                print(f"      - ID {m.get('id_miembro')}: {m.get('nombres')}")
    except Exception as e:
        print(f"    ERROR: {e}")
else:
    print("    ⚠️  SUPABASE_SERVICE_ROLE_KEY no definido en .env")
    print("    Necesitas agregar esto a tu archivo .env:")
    print("    SUPABASE_SERVICE_ROLE_KEY=tu_secret_key_aqui")

print("\n" + "="*70)
