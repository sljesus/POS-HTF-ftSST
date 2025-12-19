#!/usr/bin/env python3
"""Test para verificar que SUPABASE_ROLE_KEY está en .env y accesible"""

import os
from dotenv import load_dotenv

print("\n" + "="*70)
print("TEST: VERIFICAR CARGA DE .env Y ROLE_KEY")
print("="*70 + "\n")

# Simulando como lo hace Config
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'), encoding='utf-8')

print("Después de load_dotenv():\n")

url = os.getenv('SUPABASE_URL')
anon_key = os.getenv('SUPABASE_KEY')
role_key = os.getenv('SUPABASE_ROLE_KEY')

print(f"✓ SUPABASE_URL:       {url[:40] if url else 'NO ENCONTRADA'}...")
print(f"✓ SUPABASE_KEY:       {anon_key[:30] if anon_key else 'NO ENCONTRADA'}...")
print(f"✓ SUPABASE_ROLE_KEY:  {role_key[:30] if role_key else 'NO ENCONTRADA'}...")

if role_key:
    print("\n✓ SUPABASE_ROLE_KEY está disponible")
else:
    print("\n❌ SUPABASE_ROLE_KEY NO está disponible")

# Simular como lo hace SupabaseService
key = None or os.getenv('SUPABASE_ROLE_KEY') or os.getenv('SUPABASE_KEY')
print(f"\nKey seleccionado por SupabaseService: {key[:30] if key else 'NINGUNA'}...")

if key == role_key:
    print("✓ Está usando SUPABASE_ROLE_KEY correctamente")
elif key == anon_key:
    print("⚠️  Está usando SUPABASE_KEY (ANON KEY)")
else:
    print("❌ No hay key")

print("\n" + "="*70)
