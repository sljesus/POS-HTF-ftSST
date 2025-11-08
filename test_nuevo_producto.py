"""
Script de prueba para el formulario de Nuevo Producto
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
from ui.nuevo_producto_window import NuevoProductoWindow

def main():
    """Función principal de prueba"""
    app = QApplication(sys.argv)
    
    # Inicializar base de datos
    db_manager = DatabaseManager()
    if not db_manager.initialize_database():
        print("Error: No se pudo inicializar la base de datos")
        return
    
    # Datos de usuario de prueba
    user_data = {
        'id_usuario': 1,
        'nombre_completo': 'Usuario Prueba',
        'rol': 'administrador'
    }
    
    # Crear y mostrar ventana
    window = NuevoProductoWindow(
        db_manager=db_manager,
        supabase_service=None,  # No necesitamos supabase para pruebas
        user_data=user_data
    )
    
    # Conectar señales
    window.cerrar_solicitado.connect(lambda: print("Cerrar solicitado"))
    window.producto_guardado.connect(lambda: print("Producto guardado correctamente"))
    
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
