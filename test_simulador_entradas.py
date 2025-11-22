"""
Script de Prueba - Simulador de Entradas de Miembros
Permite simular registros de entrada para probar el sistema de notificaciones
"""

import sys
import os
import logging
import random
from datetime import datetime
import time

# Agregar el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class SimuladorEntradas:
    """Simula entradas de miembros al gimnasio"""
    
    def __init__(self, db_path=None):
        self.db_manager = DatabaseManager(db_path)
        self.db_manager.initialize_database()
        
        logging.info("Simulador de entradas inicializado")
    
    def listar_miembros_disponibles(self):
        """Listar todos los miembros activos en la base de datos"""
        try:
            cursor = self.db_manager.connection.cursor()
            cursor.execute("""
                SELECT 
                    id_miembro,
                    nombres,
                    apellido_paterno,
                    apellido_materno,
                    telefono,
                    codigo_qr,
                    activo
                FROM miembros
                WHERE activo = 1
                ORDER BY nombres
            """)
            
            miembros = cursor.fetchall()
            
            if not miembros:
                print("\n⚠️  No hay miembros activos en la base de datos")
                print("   Ejecuta 'insertar_datos_prueba.py' para agregar datos de ejemplo\n")
                return []
            
            print("\n" + "="*70)
            print("MIEMBROS ACTIVOS DISPONIBLES")
            print("="*70)
            print(f"{'ID':<6} {'NOMBRE':<40} {'TELÉFONO':<15}")
            print("-"*70)
            
            for miembro in miembros:
                nombre_completo = f"{miembro[1]} {miembro[2]} {miembro[3]}"
                telefono = miembro[4] or "Sin teléfono"
                print(f"{miembro[0]:<6} {nombre_completo:<40} {telefono:<15}")
            
            print("-"*70)
            print(f"Total: {len(miembros)} miembros\n")
            
            return miembros
            
        except Exception as e:
            logging.error(f"Error listando miembros: {e}")
            return []
    
    def simular_entrada_miembro(self, id_miembro, area="General", notas=None):
        """Simular entrada de un miembro específico"""
        try:
            # Verificar que el miembro existe
            cursor = self.db_manager.connection.cursor()
            cursor.execute("""
                SELECT nombres, apellido_paterno, apellido_materno, activo
                FROM miembros
                WHERE id_miembro = ?
            """, (id_miembro,))
            
            miembro = cursor.fetchone()
            
            if not miembro:
                print(f"\n❌ Error: No existe un miembro con ID {id_miembro}\n")
                return False
            
            if not miembro[3]:
                print(f"\n⚠️  Advertencia: El miembro está inactivo\n")
                respuesta = input("¿Deseas continuar de todos modos? (s/n): ").lower()
                if respuesta != 's':
                    return False
            
            # Registrar entrada
            id_entrada = self.db_manager.registrar_entrada_miembro(
                id_miembro=id_miembro,
                area=area,
                notas=notas
            )
            
            if id_entrada:
                nombre_completo = f"{miembro[0]} {miembro[1]} {miembro[2]}"
                print(f"\n✓ Entrada registrada exitosamente")
                print(f"  ID Entrada: {id_entrada}")
                print(f"  Miembro: {nombre_completo}")
                print(f"  Área: {area}")
                print(f"  Hora: {datetime.now().strftime('%H:%M:%S')}")
                if notas:
                    print(f"  Notas: {notas}")
                print()
                return True
            else:
                print(f"\n❌ Error al registrar entrada\n")
                return False
                
        except Exception as e:
            logging.error(f"Error simulando entrada: {e}")
            print(f"\n❌ Error: {e}\n")
            return False
    
    def simular_entradas_aleatorias(self, cantidad=5, intervalo=3):
        """Simular múltiples entradas aleatorias con intervalo"""
        try:
            # Obtener lista de miembros activos
            cursor = self.db_manager.connection.cursor()
            cursor.execute("""
                SELECT id_miembro, nombres, apellido_paterno
                FROM miembros
                WHERE activo = 1
            """)
            
            miembros = cursor.fetchall()
            
            if not miembros:
                print("\n⚠️  No hay miembros activos para simular entradas\n")
                return
            
            areas = ["General", "Área de pesas", "Cardio", "Área funcional", "Spinning"]
            
            print(f"\n{'='*70}")
            print(f"INICIANDO SIMULACIÓN DE {cantidad} ENTRADAS ALEATORIAS")
            print(f"Intervalo entre entradas: {intervalo} segundos")
            print(f"{'='*70}\n")
            
            for i in range(cantidad):
                # Seleccionar miembro aleatorio
                miembro = random.choice(miembros)
                id_miembro = miembro[0]
                nombre = f"{miembro[1]} {miembro[2]}"
                
                # Seleccionar área aleatoria
                area = random.choice(areas)
                
                print(f"[{i+1}/{cantidad}] Simulando entrada de: {nombre}")
                
                # Registrar entrada
                self.simular_entrada_miembro(id_miembro, area=area)
                
                # Esperar antes de la siguiente entrada (excepto en la última)
                if i < cantidad - 1:
                    print(f"   Esperando {intervalo} segundos...\n")
                    time.sleep(intervalo)
            
            print(f"{'='*70}")
            print(f"SIMULACIÓN COMPLETADA - {cantidad} entradas registradas")
            print(f"{'='*70}\n")
            
        except Exception as e:
            logging.error(f"Error en simulación aleatoria: {e}")
            print(f"\n❌ Error: {e}\n")
    
    def verificar_ultimas_entradas(self, limite=10):
        """Verificar las últimas entradas registradas"""
        try:
            cursor = self.db_manager.connection.cursor()
            cursor.execute("""
                SELECT 
                    re.id_entrada,
                    re.fecha_entrada,
                    m.nombres,
                    m.apellido_paterno,
                    m.apellido_materno,
                    re.area_accedida,
                    re.notas
                FROM registro_entradas re
                INNER JOIN miembros m ON re.id_miembro = m.id_miembro
                WHERE re.tipo_acceso = 'miembro'
                ORDER BY re.fecha_entrada DESC
                LIMIT ?
            """, (limite,))
            
            entradas = cursor.fetchall()
            
            if not entradas:
                print("\n⚠️  No hay registros de entrada\n")
                return
            
            print(f"\n{'='*90}")
            print(f"ÚLTIMAS {len(entradas)} ENTRADAS REGISTRADAS")
            print(f"{'='*90}")
            print(f"{'ID':<6} {'FECHA/HORA':<20} {'MIEMBRO':<30} {'ÁREA':<20}")
            print("-"*90)
            
            for entrada in entradas:
                id_entrada = entrada[0]
                fecha = entrada[1]
                nombre = f"{entrada[2]} {entrada[3]} {entrada[4]}"
                area = entrada[5]
                
                print(f"{id_entrada:<6} {fecha:<20} {nombre:<30} {area:<20}")
            
            print("-"*90 + "\n")
            
        except Exception as e:
            logging.error(f"Error verificando entradas: {e}")
            print(f"\n❌ Error: {e}\n")


def menu_principal():
    """Menú principal del simulador"""
    print("\n" + "="*70)
    print("SIMULADOR DE ENTRADAS - HTF GIMNASIO POS")
    print("="*70)
    
    # Inicializar simulador
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'pos_htf.db')
    simulador = SimuladorEntradas(db_path)
    
    while True:
        print("\n" + "-"*70)
        print("OPCIONES:")
        print("-"*70)
        print("1. Listar miembros disponibles")
        print("2. Simular entrada de un miembro específico")
        print("3. Simular entradas aleatorias automáticas")
        print("4. Ver últimas entradas registradas")
        print("5. Salir")
        print("-"*70)
        
        opcion = input("\nSelecciona una opción (1-5): ").strip()
        
        if opcion == "1":
            simulador.listar_miembros_disponibles()
            
        elif opcion == "2":
            try:
                id_miembro = int(input("\nIngresa el ID del miembro: "))
                area = input("Ingresa el área (Enter para 'General'): ").strip() or "General"
                notas = input("Ingresa notas opcionales (Enter para omitir): ").strip() or None
                
                simulador.simular_entrada_miembro(id_miembro, area, notas)
                
            except ValueError:
                print("\n❌ Error: Debes ingresar un número válido\n")
            except KeyboardInterrupt:
                print("\n\n⚠️  Operación cancelada\n")
        
        elif opcion == "3":
            try:
                cantidad = input("\n¿Cuántas entradas simular? (default: 5): ").strip()
                cantidad = int(cantidad) if cantidad else 5
                
                intervalo = input("¿Intervalo en segundos? (default: 3): ").strip()
                intervalo = int(intervalo) if intervalo else 3
                
                print(f"\nPresiona Ctrl+C para detener la simulación en cualquier momento")
                time.sleep(1)
                
                simulador.simular_entradas_aleatorias(cantidad, intervalo)
                
            except ValueError:
                print("\n❌ Error: Debes ingresar números válidos\n")
            except KeyboardInterrupt:
                print("\n\n⚠️  Simulación detenida por el usuario\n")
        
        elif opcion == "4":
            try:
                limite = input("\n¿Cuántas entradas mostrar? (default: 10): ").strip()
                limite = int(limite) if limite else 10
                
                simulador.verificar_ultimas_entradas(limite)
                
            except ValueError:
                print("\n❌ Error: Debes ingresar un número válido\n")
        
        elif opcion == "5":
            print("\n👋 ¡Hasta luego!\n")
            break
        
        else:
            print("\n❌ Opción no válida. Por favor selecciona 1-5\n")


if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\n⚠️  Programa interrumpido por el usuario\n")
    except Exception as e:
        logging.error(f"Error en el programa: {e}")
        print(f"\n❌ Error fatal: {e}\n")
