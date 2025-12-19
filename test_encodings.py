#!/usr/bin/env python3
"""Test de conexión con diferentes encodings"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

encodings_to_try = ['utf8', 'latin1', 'iso-8859-1', 'cp1252', None]

for encoding in encodings_to_try:
    try:
        print(f"Intentando con encoding={encoding}...")
        
        kwargs = {
            'host': os.getenv('DB_HOST', '192.168.100.4'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'database': os.getenv('DB_NAME', 'htf_db'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'postgres'),
        }
        
        if encoding:
            kwargs['client_encoding'] = encoding
            
        conn = psycopg2.connect(**kwargs)
        print(f"✓ Éxito con encoding={encoding}")
        conn.close()
        break
        
    except Exception as e:
        print(f"  ✗ {type(e).__name__}")
