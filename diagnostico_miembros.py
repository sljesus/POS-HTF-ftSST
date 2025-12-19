"""
Script de diagnostico detallado para revisar la tabla miembros en Supabase
"""

import sys
import os
from pathlib import Path
import dotenv
import json

dotenv.load_dotenv()
sys.path.insert(0, str(Path(__file__).parent))

from database.postgres_manager import PostgresManager

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

print("\n" + "="*70)
print("DIAGNOSTICO - TABLA MIEMBROS EN SUPABASE")
print("="*70)

try:
    # 1. Contar total de registros
    print("\n[1] CONTEO TOTAL:")
    response = pg_manager.client.table('miembros').select('id_miembro', count='exact').execute()
    total = response.count if hasattr(response, 'count') else len(response.data) if response.data else 0
    print(f"    Total de miembros: {total}")
    
    # 2. Obtener TODOS los datos sin filtros
    print("\n[2] OBTENER TODOS LOS MIEMBROS (sin filtros):")
    response = pg_manager.client.table('miembros').select('*').execute()
    
    if response.data:
        print(f"    Registros obtenidos: {len(response.data)}\n")
        
        # Mostrar los primeros 5
        for i, miembro in enumerate(response.data[:5], 1):
            print(f"    Miembro {i}:")
            print(f"      Campos disponibles: {list(miembro.keys())}")
            for key, value in miembro.items():
                print(f"        {key}: {value}")
            print()
    else:
        print("    NO HAY DATOS")
    
    # 3. Intentar con limit alto
    print("\n[3] CONSULTA CON LIMIT 1000:")
    response = pg_manager.client.table('miembros').select('*').limit(1000).execute()
    print(f"    Registros encontrados: {len(response.data) if response.data else 0}")
    
    # 4. Verificar todas las columnas de la tabla
    print("\n[4] VERIFICAR ESTRUCTURA DE LA TABLA:")
    if response.data and len(response.data) > 0:
        primer_registro = response.data[0]
        print(f"    Columnas en la tabla:")
        for col in primer_registro.keys():
            print(f"      - {col}")
    
    # 5. Búsqueda específica
    print("\n[5] BUSCAR MIEMBROS CON NOMBRE 'Juan':")
    response = pg_manager.client.table('miembros').select('*').ilike('nombres', '%Juan%').execute()
    print(f"    Encontrados: {len(response.data) if response.data else 0}")
    if response.data:
        for m in response.data:
            print(f"      {m.get('nombres')} {m.get('apellido_paterno')}")
    
    # 6. Intentar consulta directa con todas las opciones
    print("\n[6] CONSULTA SIN RESTRICCIONES:")
    response = pg_manager.client.table('miembros').select('*', count='exact').execute()
    print(f"    Total con count='exact': {response.count if hasattr(response, 'count') else 'N/A'}")
    print(f"    Datos en respuesta: {len(response.data) if response.data else 0}")
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
