"""
Prueba Rápida - Registrar una entrada de prueba
Script simple para registrar rápidamente una entrada y ver la notificación
"""

import sys
import os

# Agregar el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from datetime import datetime

def registrar_entrada_rapida():
    """Registrar una entrada rápida del primer miembro activo"""
    
    # Inicializar DB
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'pos_htf.db')
    db_manager = DatabaseManager(db_path)
    db_manager.initialize_database()
    
    # Obtener primer miembro activo
    cursor = db_manager.connection.cursor()
    cursor.execute("""
        SELECT id_miembro, nombres, apellido_paterno, apellido_materno
        FROM miembros
        WHERE activo = 1
        LIMIT 1
    """)
    
    miembro = cursor.fetchone()
    
    if not miembro:
        print("\n❌ No hay miembros activos en la base de datos")
        print("   Ejecuta 'insertar_datos_prueba.py' primero\n")
        return
    
    id_miembro = miembro[0]
    nombre_completo = f"{miembro[1]} {miembro[2]} {miembro[3]}"
    
    # Registrar entrada
    id_entrada = db_manager.registrar_entrada_miembro(
        id_miembro=id_miembro,
        area="General",
        notas="Entrada de prueba automática"
    )
    
    if id_entrada:
        print(f"\n{'='*60}")
        print("✓ ENTRADA REGISTRADA EXITOSAMENTE")
        print(f"{'='*60}")
        print(f"  ID Entrada:  {id_entrada}")
        print(f"  Miembro:     {nombre_completo}")
        print(f"  ID Miembro:  {id_miembro}")
        print(f"  Área:        General")
        print(f"  Hora:        {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*60}")
        print("\n⏱️  La notificación debería aparecer en el POS en ~2 segundos")
        print("   (si el POS está abierto)\n")
    else:
        print("\n❌ Error al registrar entrada\n")

if __name__ == "__main__":
    try:
        registrar_entrada_rapida()
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
