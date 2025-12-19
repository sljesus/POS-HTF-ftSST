#!/usr/bin/env python3
"""Test PostgresManager con ROLE_KEY"""

from database.postgres_manager import PostgresManager
from dotenv import load_dotenv
import os

load_dotenv()

# Crear conexión
db_config = {
    'url': os.getenv('SUPABASE_URL'),
    'key': os.getenv('SUPABASE_ROLE_KEY') or os.getenv('SUPABASE_KEY'),
}

db = PostgresManager(db_config)

print("✓ Conectando...")
try:
    # Intentar consulta
    miembros = db.consultar_miembros_activos()
    print(f"✓ Miembros encontrados: {len(miembros)}")
    for m in miembros[:3]:
        print(f"  - {m['nombres']}")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
