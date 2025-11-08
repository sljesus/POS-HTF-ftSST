"""
Script de prueba para el diálogo de acceso de miembro
"""

import sys
import logging
from PySide6.QtWidgets import QApplication

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Importar componentes necesarios
from database.db_manager import DatabaseManager
from ui.acceso_miembro_dialog import AccesoMiembroDialog

def main():
    """Función principal de prueba"""
    app = QApplication(sys.argv)
    
    # Inicializar base de datos
    db_manager = DatabaseManager()
    if not db_manager.initialize_database():
        print("Error: No se pudo inicializar la base de datos")
        return
    
    # Datos de miembro de prueba (puedes cambiar el ID)
    id_miembro = 1
    miembro_data = db_manager.obtener_miembro_por_id(id_miembro)
    
    if not miembro_data:
        print(f"No se encontró el miembro con ID {id_miembro}")
        print("Creando miembro de prueba...")
        
        # Crear miembro de prueba
        cursor = db_manager.connection.cursor()
        cursor.execute("""
            INSERT INTO miembros (
                nombres, apellido_paterno, apellido_materno,
                telefono, email, codigo_qr, activo
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "Juan Carlos",
            "Pérez",
            "García",
            "3331234567",
            "juan.perez@email.com",
            "MIEMBRO001",
            1
        ))
        db_manager.connection.commit()
        id_miembro = cursor.lastrowid
        
        # Obtener el miembro creado
        miembro_data = db_manager.obtener_miembro_por_id(id_miembro)
        print(f"Miembro de prueba creado con ID: {id_miembro}")
    
    print(f"Mostrando diálogo para: {miembro_data['nombres']} {miembro_data['apellido_paterno']}")
    
    # Crear y mostrar diálogo
    dialog = AccesoMiembroDialog(miembro_data)
    
    # Conectar señal
    def on_acceso_confirmado(data):
        print(f"\n✅ ACCESO CONFIRMADO")
        print(f"ID Miembro: {data['id_miembro']}")
        print(f"Nombre: {data['nombres']} {data['apellido_paterno']}")
        
        # Registrar entrada
        id_entrada = db_manager.registrar_entrada_miembro(
            id_miembro=data['id_miembro'],
            area="General"
        )
        print(f"Entrada registrada con ID: {id_entrada}")
    
    dialog.acceso_confirmado.connect(on_acceso_confirmado)
    
    result = dialog.exec()
    
    if result:
        print("\nDialogo aceptado")
    else:
        print("\nDialogo cancelado")
    
    sys.exit(0)

if __name__ == '__main__':
    main()
