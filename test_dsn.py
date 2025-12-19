#!/usr/bin/env python3
"""Test con cadena DSN y opciones especiales"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Intenta con una cadena DSN
dsn = f"postgresql://{os.getenv('DB_USER', 'postgres')}:{os.getenv('DB_PASSWORD', 'postgres')}@{os.getenv('DB_HOST', '192.168.100.4')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'htf_db')}"

try:
    print(f"Conectando con DSN: {dsn[:50]}...")
    conn = psycopg2.connect(dsn, options="-c statement_timeout=5000")
    print("✓ Conexión exitosa con DSN")
    conn.close()
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {str(e)[:100]}")
