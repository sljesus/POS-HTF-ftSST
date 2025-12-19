#!/usr/bin/env python3
"""Script para debuggear la configuración cargada"""

import os
from dotenv import load_dotenv

# Cargar .env
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'), encoding='utf-8')

print("=== VARIABLES CARGADAS DEL .env ===")
print(f"DB_HOST: {repr(os.getenv('DB_HOST'))}")
print(f"DB_PORT: {repr(os.getenv('DB_PORT'))}")
print(f"DB_NAME: {repr(os.getenv('DB_NAME'))}")
print(f"DB_USER: {repr(os.getenv('DB_USER'))}")
print(f"DB_PASSWORD: {repr(os.getenv('DB_PASSWORD'))}")

print("\n=== CODIFICACIÓN ===")
db_password = os.getenv('DB_PASSWORD', '')
print(f"Tipo de password: {type(db_password)}")
print(f"Bytes: {db_password.encode('utf-8')}")
print(f"Posición 79 aproximadamente en DSN:")

# Simular DSN
dsn = f"host={os.getenv('DB_HOST')} port={os.getenv('DB_PORT')} database={os.getenv('DB_NAME')} user={os.getenv('DB_USER')} password={db_password}"
print(f"DSN length: {len(dsn)}")
if len(dsn) > 79:
    print(f"Char at pos 79: {repr(dsn[79])}")
    print(f"Context around 79: {repr(dsn[70:90])}")
