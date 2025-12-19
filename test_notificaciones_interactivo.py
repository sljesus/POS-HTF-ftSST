#!/usr/bin/env python3
"""
Script para Probar Notificaciones de Pago
Simula lo que hace la aplicación: busca miembro, crea notificación de pago
Permite introducir datos manualmente
"""

import os
import sys
import logging
import random
import string
from datetime import datetime, timedelta
from decimal import Decimal
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Cargar .env
load_dotenv()

from database.postgres_manager import PostgresManager

def limpiar_pantalla():
    """Limpiar pantalla según SO"""
    os.system('cls' if os.name == 'nt' else 'clear')

def generar_codigo_pago():
    """Generar código de pago único (CASH-XXXX)"""
    numeros = ''.join(random.choices(string.digits, k=4))
    return f"CASH-{numeros}"

def mostrar_menu_principal():
    """Mostrar menú principal"""
    limpiar_pantalla()
    print("\n" + "="*70)
    print("PRUEBA DE NOTIFICACIONES DE PAGO - HTF GIMNASIO")
    print("="*70 + "\n")
    
    print("Opciones:")
    print("  1. Crear notificación de pago (búsqueda por ID)")
    print("  2. Crear notificación de pago (búsqueda por nombre)")
    print("  3. Ver notificaciones pendientes")
    print("  4. Buscar notificación por código de pago")
    print("  5. Salir\n")
    
    return input("Selecciona una opción (1-5): ").strip()

def buscar_miembro_por_id(db):
    """Buscar miembro por ID"""
    try:
        id_miembro = input("\nIngresa ID del miembro: ").strip()
        
        if not id_miembro.isdigit():
            print("❌ El ID debe ser un número")
            return None
        
        # Usar PostgresManager para obtener miembro
        response = db.client.table('miembros').select('*').eq('id_miembro', int(id_miembro)).execute()
        
        if response.data:
            return response.data[0]
        else:
            print(f"❌ No se encontró miembro con ID {id_miembro}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def buscar_miembro_por_nombre(db):
    """Buscar miembro por nombre"""
    try:
        nombre = input("\nIngresa nombre del miembro a buscar: ").strip()
        
        if not nombre:
            print("❌ Debes ingresar un nombre")
            return None
        
        # Buscar por ilike (case insensitive)
        response = db.client.table('miembros').select('*').ilike('nombres', f"%{nombre}%").limit(10).execute()
        
        if response.data:
            print(f"\n✓ Se encontraron {len(response.data)} resultado(s):\n")
            for idx, m in enumerate(response.data, 1):
                print(f"  {idx}. ID:{m['id_miembro']:3} - {m['nombres']} {m.get('apellido_paterno', '')}")
            
            seleccion = input("\nSelecciona número del miembro (o Enter para cancelar): ").strip()
            
            if seleccion and seleccion.isdigit():
                idx = int(seleccion) - 1
                if 0 <= idx < len(response.data):
                    return response.data[idx]
            
            print("❌ Selección inválida")
            return None
        else:
            print(f"❌ No se encontró miembro con nombre '{nombre}'")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def crear_notificacion_pago(db):
    """Crear una nueva notificación de pago"""
    try:
        print("\n" + "-"*70)
        print("CREAR NOTIFICACIÓN DE PAGO")
        print("-"*70)
        
        # Seleccionar cómo buscar miembro
        print("\n¿Cómo deseas buscar el miembro?")
        print("  1. Por ID")
        print("  2. Por nombre\n")
        
        opcion = input("Selecciona (1-2): ").strip()
        
        if opcion == "1":
            miembro = buscar_miembro_por_id(db)
        elif opcion == "2":
            miembro = buscar_miembro_por_nombre(db)
        else:
            print("❌ Opción inválida")
            return
        
        if not miembro:
            return
        
        # Mostrar datos del miembro
        print(f"\n✓ Miembro seleccionado:")
        print(f"  ID: {miembro['id_miembro']}")
        print(f"  Nombres: {miembro['nombres']}")
        print(f"  Apellidos: {miembro.get('apellido_paterno', '')} {miembro.get('apellido_materno', '')}")
        print(f"  Email: {miembro.get('email', 'N/A')}")
        print(f"  Teléfono: {miembro.get('telefono', 'N/A')}")
        
        # Solicitar datos de la notificación
        print("\n" + "-"*70)
        print("DATOS DE LA NOTIFICACIÓN DE PAGO")
        print("-"*70 + "\n")
        
        print("Tipo de notificación:")
        print("  1. membresia_pendiente")
        print("  2. visita_pendiente")
        print("  3. pago_pendiente\n")
        
        tipo_opcion = input("Selecciona tipo (1-3): ").strip()
        tipo_map = {"1": "membresia_pendiente", "2": "visita_pendiente", "3": "pago_pendiente"}
        tipo_notif = tipo_map.get(tipo_opcion, "pago_pendiente")
        
        print(f"✓ Tipo de notificación: {tipo_notif}\n")
        
        # Monto a pagar
        monto_str = input("Ingresa monto a pagar (ej: 100.50): ").strip()
        try:
            monto = float(monto_str)
        except ValueError:
            print("❌ Monto inválido, usando 0")
            monto = 0
        
        # Asunto
        asuntos = {
            "membresia_pendiente": "Membresía Pendiente de Pago",
            "visita_pendiente": "Visita Pendiente de Pago",
            "pago_pendiente": "Pago Pendiente"
        }
        asunto = asuntos.get(tipo_notif, "Pago Pendiente")
        
        # Descripción
        descripcion = input("Descripción (opcional): ").strip()
        if not descripcion:
            descripcion = f"Se requiere el pago de ${monto:.2f}"
        
        # Generar código de pago
        codigo_pago = generar_codigo_pago()
        
        # Fecha de vencimiento (en 7 días)
        fecha_vencimiento = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        # Crear notificación
        notif_data = {
            'id_miembro': miembro['id_miembro'],
            'tipo_notificacion': tipo_notif,
            'asunto': asunto,
            'descripcion': descripcion,
            'monto_pendiente': monto,
            'fecha_vencimiento': fecha_vencimiento,
            'para_miembro': True,
            'para_recepcion': True,
            'codigo_pago_generado': codigo_pago
        }
        
        print("\n" + "-"*70)
        print("RESUMEN DE LA NOTIFICACIÓN")
        print("-"*70)
        print(f"  Miembro: {miembro['nombres']} (ID:{miembro['id_miembro']})")
        print(f"  Tipo: {tipo_notif}")
        print(f"  Monto: ${monto:.2f}")
        print(f"  Código de Pago: {codigo_pago}")
        print(f"  Vencimiento: {fecha_vencimiento}")
        print(f"  Descripción: {descripcion}")
        
        confirmar = input("\n¿Crear esta notificación? (s/n): ").strip().lower()
        
        if confirmar == 's':
            id_notif = db.crear_notificacion_pago(notif_data)
            
            if id_notif:
                print(f"\n✅ NOTIFICACIÓN CREADA EXITOSAMENTE")
                print(f"  ID de notificación: {id_notif}")
                print(f"  Código de pago: {codigo_pago}")
                print(f"  Monto: ${monto:.2f}")
                print(f"\n💡 Usa este código para probar el escaneo en la app")
            else:
                print("❌ Error al crear la notificación")
        else:
            print("❌ Operación cancelada")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def ver_notificaciones_pendientes(db):
    """Ver notificaciones pendientes"""
    try:
        print("\n" + "-"*70)
        print("NOTIFICACIONES PENDIENTES")
        print("-"*70 + "\n")
        
        notificaciones = db.obtener_notificaciones_pendientes()
        
        if notificaciones:
            print(f"✓ Total de notificaciones pendientes: {len(notificaciones)}\n")
            
            for idx, notif in enumerate(notificaciones[:10], 1):
                print(f"{idx}. ID:{notif.get('id_notificacion')} - {notif.get('asunto')}")
                print(f"   Miembro: {notif['miembros'].get('nombres') if notif.get('miembros') else 'N/A'}")
                print(f"   Código: {notif.get('codigo_pago_generado', 'N/A')}")
                print(f"   Monto: ${notif.get('monto_pendiente', 0):.2f}")
                print(f"   Leída: {'Sí' if notif.get('leida') else 'No'}")
                print()
        else:
            print("✓ No hay notificaciones pendientes")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def buscar_por_codigo_pago(db):
    """Buscar notificación por código de pago"""
    try:
        print("\n" + "-"*70)
        print("BUSCAR NOTIFICACIÓN POR CÓDIGO DE PAGO")
        print("-"*70 + "\n")
        
        codigo = input("Ingresa código de pago (ej: CASH-1234): ").strip().upper()
        
        notif = db.buscar_notificacion_por_codigo_pago(codigo)
        
        if notif:
            print(f"\n✓ Notificación encontrada:")
            print(f"  ID: {notif.get('id_notificacion')}")
            print(f"  Código: {notif.get('codigo_pago_generado')}")
            print(f"  Miembro: {notif['miembros'].get('nombres') if notif.get('miembros') else 'N/A'}")
            print(f"  Tipo: {notif.get('tipo_notificacion')}")
            print(f"  Monto: ${notif.get('monto_pendiente', 0):.2f}")
            print(f"  Asunto: {notif.get('asunto')}")
            print(f"  Leída: {'Sí' if notif.get('leida') else 'No'}")
        else:
            print(f"❌ No se encontró notificación con código '{codigo}'")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Función principal"""
    try:
        # Conectar a base de datos
        db_config = {
            'url': os.getenv('SUPABASE_URL'),
            'key': os.getenv('SUPABASE_ROLE_KEY') or os.getenv('SUPABASE_KEY'),
        }
        
        db = PostgresManager(db_config)
        
        if not db.is_connected:
            print("❌ No se pudo conectar a Supabase")
            sys.exit(1)
        
        print("✓ Conectado a Supabase\n")
        
        while True:
            opcion = mostrar_menu_principal()
            
            if opcion == "1":
                crear_notificacion_pago(db)
            elif opcion == "2":
                crear_notificacion_pago(db)
            elif opcion == "3":
                ver_notificaciones_pendientes(db)
            elif opcion == "4":
                buscar_por_codigo_pago(db)
            elif opcion == "5":
                print("\n✓ Hasta luego!")
                break
            else:
                print("❌ Opción inválida")
            
            input("\nPresiona Enter para continuar...")
    
    except KeyboardInterrupt:
        print("\n\n✓ Programa interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
