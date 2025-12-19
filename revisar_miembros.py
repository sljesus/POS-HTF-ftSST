"""
Script para revisar los datos de miembros en Supabase
"""

import sys
import os
from pathlib import Path
import dotenv

dotenv.load_dotenv()
sys.path.insert(0, str(Path(__file__).parent))

from database.postgres_manager import PostgresManager
from services.supabase_service import SupabaseService

# Conectar
db_config = {
    'url': os.getenv('SUPABASE_URL'),
    'key': os.getenv('SUPABASE_KEY'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}

pg_manager = PostgresManager(db_config)
print("\n=== DATOS EN TABLA MIEMBROS ===\n")

# Obtener todos los miembros
try:
    response = pg_manager.client.table('miembros').select('*').execute()
    
    if response.data:
        print(f"Total de miembros: {len(response.data)}\n")
        for i, miembro in enumerate(response.data[:10], 1):
            print(f"Miembro {i}:")
            print(f"  ID: {miembro.get('id_miembro')}")
            print(f"  Nombre: {miembro.get('nombres')} {miembro.get('apellido_paterno')}")
            print(f"  Activo: {miembro.get('activo')}")
            print(f"  Email: {miembro.get('email')}")
            print()
    else:
        print("NO HAY MIEMBROS EN LA TABLA")
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
