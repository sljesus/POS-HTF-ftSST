#!/usr/bin/env python3
"""Test con configuración específica de locale y encoding"""

import os
import sys

# Configurar encoding antes de cualquier import
os.environ['PYTHONIOENCODING'] = 'utf-8'

import psycopg2
from psycopg2 import sql

# Intenta con parámetros de conexión especiales
conn_params = {
    'host': '192.168.100.4',
    'port': 5432,
    'database': 'postgres',
    'user': 'postgres',
    'password': 'postgres',
    'connect_timeout': 10,
    'options': '-c client_encoding=latin1'  # Opción a nivel de comando
}

try:
    print("Intentando con opción -c client_encoding=latin1...")
    conn = psycopg2.connect(**conn_params)
    print("✓ ¡Éxito!")
    conn.close()
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {str(e)[:80]}")
