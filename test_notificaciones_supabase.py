"""
Script de prueba para consultar notificaciones_pos en Supabase
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
import json

# Cargar variables de entorno
load_dotenv()

# Obtener credenciales
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("=" * 80)
print("TEST: Consulta de notificaciones_pos en Supabase")
print("=" * 80)
print(f"\nSupabase URL: {SUPABASE_URL}")
print(f"Supabase Key: {'*' * 20}{SUPABASE_KEY[-10:] if SUPABASE_KEY else 'NO ENCONTRADA'}")

try:
    # Crear cliente de Supabase
    print("\n1. Creando cliente de Supabase...")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("   ✓ Cliente creado exitosamente")
    
    # Consulta 1: Todas las notificaciones
    print("\n2. Consultando TODAS las notificaciones_pos...")
    response_all = supabase.table('notificaciones_pos').select('*').execute()
    print(f"   Total de notificaciones en la tabla: {len(response_all.data)}")
    
    if response_all.data:
        print("\n   Primeras 3 notificaciones:")
        for i, notif in enumerate(response_all.data[:3], 1):
            print(f"\n   [{i}] ID: {notif.get('id_notificacion')}")
            print(f"       Tipo: {notif.get('tipo_notificacion')}")
            print(f"       Asunto: {notif.get('asunto')}")
            print(f"       Para recepción: {notif.get('para_recepcion')}")
            print(f"       Respondida: {notif.get('respondida')}")
            print(f"       Miembro ID: {notif.get('id_miembro')}")
    
    # Consulta 2: Notificaciones pendientes (filtradas)
    print("\n3. Consultando notificaciones PENDIENTES (como en el POS)...")
    response_filtered = supabase.table('notificaciones_pos') \
        .select('*') \
        .eq('para_recepcion', True) \
        .eq('respondida', False) \
        .in_('tipo_notificacion', ['membresia_pendiente', 'visita_pendiente']) \
        .execute()
    
    print(f"   Notificaciones pendientes encontradas: {len(response_filtered.data)}")
    
    if response_filtered.data:
        print("\n   Detalles de notificaciones pendientes:")
        for i, notif in enumerate(response_filtered.data, 1):
            print(f"\n   [{i}] ID: {notif.get('id_notificacion')}")
            print(f"       Tipo: {notif.get('tipo_notificacion')}")
            print(f"       Asunto: {notif.get('asunto')}")
            print(f"       Monto: ${notif.get('monto_pendiente')}")
            print(f"       Fecha vencimiento: {notif.get('fecha_vencimiento')}")
            print(f"       Código pago: {notif.get('codigo_pago_generado')}")
            print(f"       Creada en: {notif.get('creada_en')}")
    
    # Consulta 3: Con JOIN a miembros
    print("\n4. Consultando con JOIN a tabla miembros...")
    response_with_join = supabase.table('notificaciones_pos') \
        .select('*, miembros(nombres, apellido_paterno, apellido_materno, telefono)') \
        .eq('para_recepcion', True) \
        .eq('respondida', False) \
        .in_('tipo_notificacion', ['membresia_pendiente', 'visita_pendiente']) \
        .order('creada_en', desc=True) \
        .execute()
    
    print(f"   Notificaciones con datos de miembro: {len(response_with_join.data)}")
    
    if response_with_join.data:
        print("\n   Ejemplo de datos completos:")
        for i, notif in enumerate(response_with_join.data[:2], 1):
            miembro = notif.get('miembros', {})
            print(f"\n   [{i}] Notificación #{notif.get('id_notificacion')}")
            print(f"       Tipo: {notif.get('tipo_notificacion')}")
            print(f"       Miembro: {miembro.get('nombres')} {miembro.get('apellido_paterno')} {miembro.get('apellido_materno')}")
            print(f"       Teléfono: {miembro.get('telefono')}")
            print(f"       Monto: ${notif.get('monto_pendiente')}")
    
    # Resumen de columnas
    print("\n5. Verificando estructura de la tabla...")
    if response_all.data:
        columnas = list(response_all.data[0].keys())
        print(f"   Columnas disponibles: {', '.join(columnas)}")
    
    print("\n" + "=" * 80)
    print("✓ Prueba completada exitosamente")
    print("=" * 80)
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    print("\nTraceback completo:")
    print(traceback.format_exc())
    print("=" * 80)
