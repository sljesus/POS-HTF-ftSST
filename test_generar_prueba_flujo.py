"""
Script para generar datos de prueba y crear visitas para probar el flujo completo
- Busca un miembro existente
- Genera multiples entradas (visitas) 
- Genera codigos de pago de prueba
"""

import sys
import os
import io
import logging
from datetime import datetime, timedelta
import random
from pathlib import Path
import dotenv

# Configurar encoding para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Cargar variables de entorno
dotenv.load_dotenv()

# Agregar el directorio actual al path
sys.path.insert(0, str(Path(__file__).parent))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from database.postgres_manager import PostgresManager
from services.supabase_service import SupabaseService

def obtener_miembro_aleatorio(pg_manager):
    """Obtener un miembro aleatorio de la BD"""
    try:
        # Primero intentar con activo = true, sino traer cualquiera
        response = pg_manager.client.table('miembros').select('*').eq('activo', True).limit(100).execute()
        
        if not response.data or len(response.data) == 0:
            # Si no hay activos, obtener cualquiera
            print("   [INFO] No hay miembros activos, buscando todos...")
            response = pg_manager.client.table('miembros').select('*').limit(100).execute()
        
        if response.data and len(response.data) > 0:
            miembro = random.choice(response.data)
            return {
                'id_miembro': miembro.get('id_miembro'),
                'nombres': miembro.get('nombres'),
                'apellido_paterno': miembro.get('apellido_paterno'),
                'apellido_materno': miembro.get('apellido_materno'),
                'email': miembro.get('email'),
                'telefono': miembro.get('telefono')
            }
    except Exception as e:
        logging.error(f"Error obteniendo miembro: {e}")
    return None

def generar_visitas(pg_manager, id_miembro, cantidad=5):
    """Generar multiples visitas/entradas para un miembro"""
    print(f"\n[VISITAS] Generando {cantidad} visitas para miembro ID {id_miembro}...")
    
    ids_entrada = []
    tipos_acceso = ["Acceso Normal", "Acceso Clase", "Acceso Visitante"]
    areas = ["General", "Pesas", "Cardio", "Yoga", "Crossfit"]
    
    for i in range(cantidad):
        # Generar fecha/hora aleatoria en los ultimos 30 dias
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
                print(f"  OK - Visita {i+1}: ID entrada {id_entrada} - {fecha_entrada.strftime('%Y-%m-%d %H:%M')}")
            else:
                print(f"  ERROR - Visita {i+1} no pudo registrarse")
                
        except Exception as e:
            logging.error(f"Error generando visita {i+1}: {e}")
    
    return ids_entrada

def generar_codigos_pago(supabase_service, pg_manager, id_miembro, cantidad=3):
    """Generar codigos de pago de prueba para un miembro"""
    print(f"\n[PAGOS] Generando {cantidad} codigos de pago para miembro ID {id_miembro}...")
    
    montos = [100, 200, 500, 1000, 1500, 2000]
    codigos_generados = []
    
    for i in range(cantidad):
        codigo = f"CASH-{random.randint(1000, 9999)}"
        monto = random.choice(montos)
        
        try:
            # Crear notificacion de pago pendiente
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
            
            response = supabase_service.client.table('notificaciones_pos').insert(notif_data).execute()
            
            if response.data:
                id_notif = response.data[0]['id_notificacion']
                codigos_generados.append({
                    'id_notificacion': id_notif,
                    'codigo': codigo,
                    'monto': monto
                })
                print(f"  OK - Codigo {i+1}: {codigo} - Monto: ${monto} - ID Notif: {id_notif}")
            else:
                print(f"  ERROR - Codigo {i+1} no pudo generarse")
                
        except Exception as e:
            logging.error(f"Error generando codigo {i+1}: {e}")
    
    return codigos_generados

def mostrar_resumen(miembro, ids_entrada, codigos):
    """Mostrar resumen de lo generado"""
    print("\n" + "="*70)
    print("RESUMEN DE DATOS GENERADOS")
    print("="*70)
    
    print(f"\nMIEMBRO SELECCIONADO:")
    print(f"   ID: {miembro['id_miembro']}")
    print(f"   Nombre: {miembro['nombres']} {miembro['apellido_paterno']} {miembro['apellido_materno']}")
    print(f"   Email: {miembro['email']}")
    print(f"   Telefono: {miembro['telefono']}")
    
    print(f"\nENTRADAS/VISITAS GENERADAS: {len(ids_entrada)}")
    for i, id_entrada in enumerate(ids_entrada, 1):
        print(f"   {i}. ID Entrada: {id_entrada}")
    
    print(f"\nCODIGOS DE PAGO GENERADOS: {len(codigos)}")
    for i, code_info in enumerate(codigos, 1):
        print(f"   {i}. Codigo: {code_info['codigo']} | Monto: ${code_info['monto']} | ID Notif: {code_info['id_notificacion']}")
    
    print("\n" + "="*70)
    print("DATOS LISTOS PARA PRUEBA")
    print("="*70)
    print("\nPASOS GUIAS:")
    print("1. Inicia la aplicacion POS")
    print(f"2. Busca al miembro: {miembro['nombres']} {miembro['apellido_paterno']}")
    print(f"3. Prueba escanear alguno de los codigos: {', '.join([c['codigo'] for c in codigos[:2]])}")
    print("4. Verifica que se procese correctamente el pago")
    print("5. Chequea el historial de entradas del miembro")
    print("\n")

def main():
    """Funcion principal"""
    print("\n" + "="*70)
    print("GENERADOR DE DATOS DE PRUEBA - FLUJO COMPLETO")
    print("="*70)
    
    try:
        # Conectarse a las bases de datos
        print("\nConectando a bases de datos...")
        
        # Configurar PostgresManager con credenciales de Supabase
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
        
        if not supabase_service.client:
            print("ERROR: No se pudo conectar a Supabase")
            return
        
        print("OK - Conexiones establecidas")
        
        # Obtener miembro aleatorio
        print("\nBuscando miembro aleatorio...")
        miembro = obtener_miembro_aleatorio(pg_manager)
        
        if not miembro:
            print("ERROR - No se encontro ningun miembro activo")
            return
        
        print(f"OK - Miembro encontrado: {miembro['nombres']} {miembro['apellido_paterno']}")
        
        # Generar visitas
        ids_entrada = generar_visitas(pg_manager, miembro['id_miembro'], cantidad=5)
        
        # Generar códigos de pago
        codigos = generar_codigos_pago(supabase_service, pg_manager, miembro['id_miembro'], cantidad=3)
        
        # Mostrar resumen
        mostrar_resumen(miembro, ids_entrada, codigos)
        
    except Exception as e:
        logging.error(f"Error en main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
