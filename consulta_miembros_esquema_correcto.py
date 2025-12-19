"""
Script para consultar a Supabase usando el esquema exacto de la tabla miembros
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
print("CONSULTA SUPABASE - TABLA MIEMBROS CON ESQUEMA CORRECTO")
print("="*70)

try:
    # Listar todas las columnas del esquema
    columnas = [
        'id_miembro',
        'nombres',
        'apellido_paterno',
        'apellido_materno',
        'telefono',
        'email',
        'contacto_emergencia',
        'telefono_emergencia',
        'codigo_qr',
        'activo',
        'fecha_registro',
        'fecha_nacimiento',
        'foto_url'
    ]
    
    # Construir select con todas las columnas
    select_str = ','.join(columnas)
    
    print(f"\n[1] CONSULTANDO CON TODAS LAS COLUMNAS DEL ESQUEMA:")
    print(f"    Columnas: {', '.join(columnas[:5])}...")
    
    response = pg_manager.client.table('miembros').select(select_str).limit(100).execute()
    
    if response.data:
        print(f"\n    REGISTROS ENCONTRADOS: {len(response.data)}\n")
        
        for i, miembro in enumerate(response.data, 1):
            print(f"    Miembro {i}:")
            print(f"      ID: {miembro.get('id_miembro')}")
            print(f"      Nombre: {miembro.get('nombres')} {miembro.get('apellido_paterno')} {miembro.get('apellido_materno')}")
            print(f"      Email: {miembro.get('email')}")
            print(f"      Teléfono: {miembro.get('telefono')}")
            print(f"      Código QR: {miembro.get('codigo_qr')}")
            print(f"      Activo: {miembro.get('activo')}")
            print(f"      Fecha Registro: {miembro.get('fecha_registro')}")
            print()
    else:
        print("    NO HAY REGISTROS EN LA TABLA")
        
        # Intentar count exacto
        print("\n[2] INTENTO CON COUNT=EXACT:")
        response = pg_manager.client.table('miembros').select('id_miembro', count='exact').execute()
        print(f"    Total de registros (con count): {response.count if hasattr(response, 'count') else 'N/A'}")
        
        # Intentar SIN seleccionar nada
        print("\n[3] INTENTO CON SELECT * (sin especificar columnas):")
        response = pg_manager.client.table('miembros').select('*').execute()
        print(f"    Registros: {len(response.data) if response.data else 0}")
        
        # Si hay respuesta, mostrar qué columnas tiene
        if response.data and len(response.data) > 0:
            print(f"    Columnas encontradas: {list(response.data[0].keys())}")
        
        # Filtro con activo = true
        print("\n[4] INTENTO FILTRANDO CON activo=true:")
        response = pg_manager.client.table('miembros').select('*').eq('activo', True).execute()
        print(f"    Registros activos: {len(response.data) if response.data else 0}")
        
        # Filtro con activo = false
        print("\n[5] INTENTO FILTRANDO CON activo=false:")
        response = pg_manager.client.table('miembros').select('*').eq('activo', False).execute()
        print(f"    Registros inactivos: {len(response.data) if response.data else 0}")
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
