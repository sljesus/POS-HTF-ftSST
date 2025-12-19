#!/usr/bin/env python3
"""Solución: usar subprocess para ejecutar PostgreSQL con locale específico"""

import subprocess
import sys
import os

# Crear un script Python simple que intente conectar
script = """
import os
import locale

# Forzar locale a Latin-1
try:
    locale.setlocale(locale.LC_ALL, 'es_ES.iso88591')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'C')
    except:
        pass

import psycopg2

try:
    conn = psycopg2.connect(
        host='192.168.100.4',
        port=5432,
        database='postgres',
        user='postgres',
        password='postgres'
    )
    print("OK")
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
"""

# Ejecutar en subprocess con PYTHONIOENCODING
env = os.environ.copy()
env['PYTHONIOENCODING'] = 'latin-1'

result = subprocess.run([sys.executable, '-c', script], capture_output=True, text=True, env=env)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
