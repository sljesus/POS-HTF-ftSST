#!/usr/bin/env python3
"""Test conexión PostgreSQL con diagnóstico detallado"""

import psycopg2
import socket

host = '192.168.100.4'
port = 5432

print("=" * 60)
print("DIAGNÓSTICO DE CONEXIÓN A PostgreSQL")
print("=" * 60)

# 1. Test TCP
print("\n1️⃣ Prueba TCP:")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    if sock.connect_ex((host, port)) == 0:
        print(f"   ✓ Puerto {port} está abierto en {host}")
    sock.close()
except Exception as e:
    print(f"   ✗ Error: {e}")

# 2. Test PostgreSQL
print(f"\n2️⃣ Prueba conexión PostgreSQL a {host}:{port}:")
try:
    conn = psycopg2.connect(
        host=host,
        port=port,
        database='postgres',
        user='postgres',
        password='postgres',
        connect_timeout=10
    )
    print("   ✓ ¡Conexión exitosa!")
    conn.close()
    
except UnicodeDecodeError as e:
    print(f"   ✗ UnicodeDecodeError")
    print(f"      Posición: {e.start}")
    print(f"      Byte problemático: {hex(e.object[e.start])}")
    print(f"      Contexto: {e.object[max(0,e.start-10):e.start+10]}")
    
except psycopg2.OperationalError as e:
    print(f"   ✗ OperationalError")
    print(f"      {e}")
    
except Exception as e:
    print(f"   ✗ {type(e).__name__}")
    print(f"      {e}")

print("\n" + "=" * 60)
