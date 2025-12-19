"""
Script para listar todas las tablas disponibles en Supabase
"""

import sys
import os
from pathlib import Path
import dotenv

dotenv.load_dotenv()
sys.path.insert(0, str(Path(__file__).parent))

from database.postgres_manager import PostgresManager

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

print("\n" + "="*70)
print("LISTAR TODAS LAS TABLAS DISPONIBLES EN SUPABASE")
print("="*70)

try:
    # Intentar con tabla informatica_schema si existe
    tablas_a_probar = [
        'miembros',
        'public.miembros',
        'usuarios_miembros',
        'members',
        'clientes',
        'personas',
        'participantes'
    ]
    
    print("\nIntentando consultar diferentes tablas:\n")
    
    for tabla in tablas_a_probar:
        try:
            response = pg_manager.client.table(tabla).select('*').limit(1).execute()
            total = len(response.data) if response.data else 0
            print(f"  {tabla}: {total} registros")
        except Exception as e:
            print(f"  {tabla}: ERROR - {str(e)[:80]}")
    
    # Intentar obtener info de schema de Supabase
    print("\n" + "="*70)
    print("REVISANDO TABLA: information_schema.tables")
    print("="*70)
    
    try:
        response = pg_manager.client.table('information_schema.tables').select('table_name, table_schema').limit(50).execute()
        if response.data:
            print(f"\nTablas encontradas ({len(response.data)}):\n")
            for table in response.data:
                print(f"  {table.get('table_schema')}.{table.get('table_name')}")
        else:
            print("No se pudo acceder a information_schema")
    except Exception as e:
        print(f"Error: {e}")
        
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
