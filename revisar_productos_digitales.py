"""
Script para revisar productos digitales en Supabase
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
print("REVISAR CATALOGO DE PRODUCTOS DIGITALES")
print("="*70)

try:
    # Primero, obtener todo sin especificar columnas
    print("\n[1] OBTENIENDO PRIMEROS 10 PRODUCTOS:")
    response = pg_manager.client.table('ca_productos_digitales').select('*').limit(10).execute()
    
    if response.data:
        print(f"    Total encontrado: {len(response.data)}\n")
        
        # Mostrar estructura
        print("    COLUMNAS DISPONIBLES:")
        if len(response.data) > 0:
            for col in response.data[0].keys():
                print(f"      - {col}")
        
        print("\n    PRODUCTOS:")
        for i, prod in enumerate(response.data, 1):
            print(f"\n    Producto {i}:")
            for key, value in prod.items():
                print(f"      {key}: {value}")
    else:
        print("    NO HAY PRODUCTOS EN LA TABLA")
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
