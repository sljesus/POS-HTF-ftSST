#!/usr/bin/env python3
"""Test simple de PostgresManager con ROLE_KEY"""

from database.postgres_manager import PostgresManager
from dotenv import load_dotenv
import os

load_dotenv()

# Crear conexión directamente con ROLE_KEY
db = PostgresManager({
    'url': os.getenv('SUPABASE_URL'),
    'key': os.getenv('SUPABASE_ROLE_KEY') or os.getenv('SUPABASE_KEY'),
})

print("✓ Conectado con Supabase\n")

# Intentar obtener total de miembros
try:
    total = db.get_total_members()
    print(f"✓ Total de miembros activos: {total}")
except Exception as e:
    print(f"✗ Error: {e}")
