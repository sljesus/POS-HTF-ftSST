#!/usr/bin/env python3
"""Listar métodos de PostgresManager"""

from database.postgres_manager import PostgresManager
import inspect

db_config = {
    'url': 'http://localhost',
    'key': 'test',
}

db = PostgresManager(db_config)

# Listar todos los métodos
methods = [m for m in dir(db) if not m.startswith('_') and callable(getattr(db, m))]

print("Métodos de PostgresManager:")
for m in sorted(methods):
    print(f"  - {m}()")
