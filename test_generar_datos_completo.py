"""
Script para generar datos completos:
1. Primero crea miembros de prueba si no existen
2. Luego genera visitas y codigos de pago
"""

import sys
import os
import io
import logging
from datetime import datetime, timedelta
import random
from pathlib import Path
import dotenv

# Configurar encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

dotenv.load_dotenv()
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from database.postgres_manager import PostgresManager
from services.supabase_service import SupabaseService

def crear_miembros_prueba(pg_manager):
    """Crear miembros de prueba si no existen"""
    print("\n[CREAR MIEMBROS] Insertando miembros de prueba...")
    
    miembros_prueba = [
        {
            'nombres': 'Juan Carlos',
            'apellido_paterno': 'Perez',
            'apellido_materno': 'Garcia',
            'email': 'juan.perez@test.com',
            'telefono': '3331234567',
            'codigo_qr': 'MIEMBRO001'
        },
        {
            'nombres': 'Maria',
            'apellido_paterno': 'Gonzalez',
            'apellido_materno': 'Martinez',
            'email': 'maria.gonzalez@test.com',
            'telefono': '3332345678',
            'codigo_qr': 'MIEMBRO002'
        },
        {
            'nombres': 'Roberto',
            'apellido_paterno': 'Sanchez',
            'apellido_materno': 'Lopez',
            'email': 'roberto.sanchez@test.com',
            'telefono': '3333456789',
            'codigo_qr': 'MIEMBRO003'
        }
    ]
    
    ids_creados = []
    for miembro in miembros_prueba:
        try:
            # Insertar directamente (sin verificar si existe)
            resp = pg_manager.client.table('miembros').insert([miembro]).execute()
            if resp.data:
                id_miembro = resp.data[0]['id_miembro']
                ids_creados.append(id_miembro)
                print(f"  OK - Miembro creado: {miembro['nombres']} (ID: {id_miembro})")
            else:
                print(f"  ERROR - No se pudo crear: {miembro['nombres']}")
        except Exception as e:
            print(f"  ERROR - {miembro['nombres']}: {str(e)}")
    
    return ids_creados

def generar_visitas(pg_manager, id_miembro, cantidad=5):
    """Generar visitas para un miembro"""
    print(f"\n[VISITAS] Generando {cantidad} visitas para miembro ID {id_miembro}...")
    
    ids_entrada = []
    tipos_acceso = ["Acceso Normal", "Acceso Clase", "Acceso Visitante"]
    areas = ["General", "Pesas", "Cardio", "Yoga", "Crossfit"]
    
    for i in range(cantidad):
        dias_atras = random.randint(0, 30)
        horas_atras = random.randint(0, 23)
        fecha_entrada = datetime.now() - timedelta(days=dias_atras, hours=horas_atras)
        
        try:
            entrada_data = {
                'id_miembro': id_miembro,
                'tipo_acceso': random.choice(tipos_acceso),
                'area_accedida': random.choice(areas),
                'dispositivo_registro': 'POS-TEST',
                'notas': f'Visita de prueba #{i+1}',
                'fecha_entrada': fecha_entrada.isoformat()
            }
            
            id_entrada = pg_manager.registrar_entrada(entrada_data)
            if id_entrada:
                ids_entrada.append(id_entrada)
                print(f"  OK - Visita {i+1}: ID {id_entrada} - {fecha_entrada.strftime('%Y-%m-%d %H:%M')}")
        except Exception as e:
            logging.error(f"Error generando visita {i+1}: {e}")
    
    return ids_entrada

def generar_codigos_pago(supabase_service, id_miembro, cantidad=3):
    """Generar codigos de pago"""
    print(f"\n[PAGOS] Generando {cantidad} codigos de pago para miembro ID {id_miembro}...")
    
    montos = [100, 200, 500, 1000, 1500, 2000]
    codigos = []
    
    for i in range(cantidad):
        codigo = f"CASH-{random.randint(1000, 9999)}"
        monto = random.choice(montos)
        
        try:
            notif_data = {
                'id_miembro': id_miembro,
                'tipo_notificacion': 'Pago',
                'asunto': f'Codigo de pago de prueba #{i+1}',
                'mensaje': f'Pago pendiente por ${monto}',
                'codigo_pago_generado': codigo,
                'monto_pendiente': monto,
                'respondida': False,
                'fecha_notificacion': datetime.now().isoformat()
            }
            
            response = supabase_service.client.table('notificaciones_pos').insert([notif_data]).execute()
            
            if response.data:
                id_notif = response.data[0]['id_notificacion']
                codigos.append({'codigo': codigo, 'monto': monto, 'id_notif': id_notif})
                print(f"  OK - Codigo {i+1}: {codigo} - ${monto} - ID Notif: {id_notif}")
        except Exception as e:
            logging.error(f"Error generando codigo {i+1}: {e}")
    
    return codigos

def main():
    print("\n" + "="*70)
    print("GENERADOR COMPLETO DE DATOS DE PRUEBA")
    print("="*70)
    
    try:
        print("\nConectando a bases de datos...")
        db_config = {
            'url': os.getenv('SUPABASE_URL'),
            'key': os.getenv('SUPABASE_KEY'),
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT'),
            'database': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD')
        }
        
        pg_manager = PostgresManager(db_config)
        supabase_service = SupabaseService()
        
        if not pg_manager.is_connected:
            print("ERROR: No se pudo conectar a Supabase")
            return
        
        print("OK - Conexion establecida")
        
        # Crear miembros de prueba
        ids_miembros = crear_miembros_prueba(pg_manager)
        
        if not ids_miembros:
            print("ERROR: No se pudieron crear miembros")
            return
        
        print("\n" + "="*70)
        print("DATOS GENERADOS")
        print("="*70)
        
        # Para cada miembro, generar visitas y codigos
        for idx, id_miembro in enumerate(ids_miembros, 1):
            print(f"\n[MIEMBRO {idx}] ID: {id_miembro}")
            ids_entrada = generar_visitas(pg_manager, id_miembro, cantidad=3)
            codigos = generar_codigos_pago(supabase_service, id_miembro, cantidad=2)
        
        print("\n" + "="*70)
        print("LISTO - Datos generados exitosamente")
        print("="*70)
        print("\nPASOS A SEGUIR:")
        print("1. Inicia la aplicacion POS (python main.py)")
        print("2. Busca al miembro: Juan Carlos Perez")
        print("3. Escanea uno de los codigos de pago")
        print("4. Prueba el flujo completo de pago")
        print("\n")
        
    except Exception as e:
        logging.error(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
