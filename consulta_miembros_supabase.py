"""
Script para consultar directamente a Supabase - Tabla miembros
Igual de robusta que la de productos digitales que SÍ funcionó
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
print("CONSULTA DIRECTA - TABLA MIEMBROS")
print("="*70)

try:
    # Exactamente igual a como consultamos productos digitales
    print("\n[1] OBTENIENDO PRIMEROS 20 MIEMBROS:")
    response = pg_manager.client.table('miembros').select('*').limit(20).execute()
    
    if response.data:
        print(f"    Total encontrado: {len(response.data)}\n")
        
        # Mostrar estructura
        print("    COLUMNAS DISPONIBLES:")
        if len(response.data) > 0:
            for col in response.data[0].keys():
                print(f"      - {col}")
        
        print("\n    MIEMBROS:")
        for i, miembro in enumerate(response.data, 1):
            print(f"\n    Miembro {i}:")
            for key, value in miembro.items():
                print(f"      {key}: {value}")
    else:
        print("    NO HAY MIEMBROS EN LA TABLA")
        
        # Intentar ver las columnas sin datos
        print("\n[2] INTENTANDO CON LIMIT 1 SIN RESTRICCIONES:")
        response = pg_manager.client.table('miembros').select('*').limit(1).execute()
        print(f"    Respuesta: {response}")
        print(f"    Data: {response.data}")
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
