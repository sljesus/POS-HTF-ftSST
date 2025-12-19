#!/usr/bin/env python3
"""Test de conexión PostgreSQL directo"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

try:
    print("Intentando conexión a PostgreSQL...")
    
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', '192.168.100.4'),
        port=int(os.getenv('DB_PORT', '5432')),
        database=os.getenv('DB_NAME', 'htf_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres'),
        client_encoding='utf8'
    )
    print("✓ Conexión exitosa")
    conn.close()
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
