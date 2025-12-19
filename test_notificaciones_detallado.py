"""
Test detallado de la tabla notificaciones_pos en Supabase
Verificar tipos de datos, valores booleanos y filtros
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
import json

# Cargar variables de entorno
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("=" * 80)
print("TEST DETALLADO: notificaciones_pos en Supabase")
print("=" * 80)

try:
    # Crear cliente
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✓ Cliente Supabase creado\n")
    
    # 1. Todas las notificaciones (sin filtros)
    print("1. TODAS LAS NOTIFICACIONES (sin filtros)")
    print("-" * 80)
    response_all = supabase.table('notificaciones_pos').select('*').execute()
    print(f"Total de registros: {len(response_all.data)}\n")
    
    if response_all.data:
        # Analizar primera notificación
        primera = response_all.data[0]
        print("Estructura de la primera notificación:")
        print(json.dumps(primera, indent=2, default=str))
        print("\nTipos de datos:")
        for key, value in primera.items():
            print(f"  {key}: {type(value).__name__} = {repr(value)}")
        
        # Analizar valores booleanos
        print("\n" + "=" * 80)
        print("2. ANÁLISIS DE COLUMNAS BOOLEANAS")
        print("-" * 80)
        
        valores_para_recepcion = set()
        valores_respondida = set()
        
        for notif in response_all.data:
            valores_para_recepcion.add((type(notif['para_recepcion']).__name__, notif['para_recepcion']))
            valores_respondida.add((type(notif['respondida']).__name__, notif['respondida']))
        
        print(f"Valores únicos en 'para_recepcion': {valores_para_recepcion}")
        print(f"Valores únicos en 'respondida': {valores_respondida}")
        
        # Contar por tipo de notificación
        print("\n" + "=" * 80)
        print("3. DISTRIBUCIÓN POR TIPO")
        print("-" * 80)
        tipos = {}
        for notif in response_all.data:
            tipo = notif['tipo_notificacion']
            tipos[tipo] = tipos.get(tipo, 0) + 1
        
        for tipo, count in tipos.items():
            print(f"  {tipo}: {count}")
        
        # Contar por estado
        print("\n" + "=" * 80)
        print("4. DISTRIBUCIÓN POR ESTADO")
        print("-" * 80)
        
        para_recepcion_true = sum(1 for n in response_all.data if n['para_recepcion'] == True)
        para_recepcion_false = sum(1 for n in response_all.data if n['para_recepcion'] == False)
        respondida_true = sum(1 for n in response_all.data if n['respondida'] == True)
        respondida_false = sum(1 for n in response_all.data if n['respondida'] == False)
        
        print(f"  para_recepcion = True: {para_recepcion_true}")
        print(f"  para_recepcion = False: {para_recepcion_false}")
        print(f"  respondida = True: {respondida_true}")
        print(f"  respondida = False: {respondida_false}")
        
    # 5. Probar filtros individuales
    print("\n" + "=" * 80)
    print("5. PRUEBA DE FILTROS INDIVIDUALES")
    print("-" * 80)
    
    # Filtro 1: solo para_recepcion
    f1 = supabase.table('notificaciones_pos').select('*').eq('para_recepcion', True).execute()
    print(f"Filtro [para_recepcion = True]: {len(f1.data)} resultados")
    
    # Filtro 2: solo respondida
    f2 = supabase.table('notificaciones_pos').select('*').eq('respondida', False).execute()
    print(f"Filtro [respondida = False]: {len(f2.data)} resultados")
    
    # Filtro 3: tipo_notificacion
    f3 = supabase.table('notificaciones_pos').select('*').in_('tipo_notificacion', ['membresia_pendiente', 'visita_pendiente']).execute()
    print(f"Filtro [tipo IN ('membresia_pendiente', 'visita_pendiente')]: {len(f3.data)} resultados")
    
    # Filtro 4: Combinación de todos
    f4 = supabase.table('notificaciones_pos') \
        .select('*') \
        .eq('para_recepcion', True) \
        .eq('respondida', False) \
        .in_('tipo_notificacion', ['membresia_pendiente', 'visita_pendiente']) \
        .execute()
    print(f"Filtro [TODOS combinados]: {len(f4.data)} resultados")
    
    if f4.data:
        print("\nPrimera notificación con todos los filtros:")
        print(json.dumps(f4.data[0], indent=2, default=str))
    
    # 6. Probar con JOIN
    print("\n" + "=" * 80)
    print("6. PRUEBA CON JOIN A MIEMBROS")
    print("-" * 80)
    
    f5 = supabase.table('notificaciones_pos') \
        .select('*, miembros(nombres, apellido_paterno, apellido_materno, telefono)') \
        .eq('para_recepcion', True) \
        .eq('respondida', False) \
        .in_('tipo_notificacion', ['membresia_pendiente', 'visita_pendiente']) \
        .order('creada_en', desc=True) \
        .execute()
    
    print(f"Con JOIN: {len(f5.data)} resultados")
    
    if f5.data:
        print("\nPrimera notificación con JOIN:")
        print(json.dumps(f5.data[0], indent=2, default=str))
    
    print("\n" + "=" * 80)
    print("✓ TEST COMPLETADO")
    print("=" * 80)
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
