"""
Script de prueba para la ventana de ubicaciones
"""

import sys
import logging
from PySide6.QtWidgets import QApplication

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Importar gestor de BD
from database.postgres_manager import PostgresManager

# Importar ventana de ubicaciones
from ui.ubicaciones_window import UbicacionesWindow

def test_ubicaciones_window():
    """Pruebar la ventana de ubicaciones"""
    
    app = QApplication(sys.argv)
    
    # Conectar a BD
    print("Conectando a base de datos...")
    pg_manager = PostgresManager()
    
    if not pg_manager.connect():
        print("No se pudo conectar a la base de datos")
        return
    
    print("Conexión exitosa")
    
    # User data simulado
    user_data = {
        'id_usuario': 1,
        'usuario': 'admin',
        'rol': 'administrador',
        'nombre': 'Administrador'
    }
    
    # Crear y mostrar ventana
    window = UbicacionesWindow(pg_manager, user_data)
    window.resize(1000, 700)
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    test_ubicaciones_window()
