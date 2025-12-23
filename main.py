"""
Aplicación Principal del POS HTF Gimnasio
Sistema de Punto de Venta con sincronización offline
Usando PySide6 para la interfaz
"""

import sys
import os
import logging
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

# Configurar logging ANTES de cualquier otro import
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pos_htf.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Configurar encoding UTF-8 para stdout/stderr en Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    from ui.login_window_pyside import LoginWindow
    from ui.main_pos_window import MainPOSWindow
    from database.postgres_manager import PostgresManager
    from services.supabase_service import SupabaseService
    from utils.config import Config
except ImportError as e:
    logging.error(f"Error importando módulos: {e}")
    # Mostrar error al usuario si es GUI
    try:
        app = QApplication(sys.argv)
        QMessageBox.critical(None, "Error", f"Error al cargar la aplicación:\n{e}")
    except:
        pass
    sys.exit(1)


class POSApplication:
    def __init__(self):
        """Inicializar la aplicación POS"""
        try:
            # Crear aplicación Qt
            self.app = QApplication(sys.argv)
            self.app.setApplicationName("POS HTF Gimnasio")
            
            # Inicializar configuración
            self.config = Config()
            
            # Inicializar servicios
            try:
                db_config = self.config.get_postgres_config()
                self.postgres_manager = PostgresManager(db_config)
                if not self.postgres_manager.initialize_database():
                    logging.warning("Advertencia: BD no disponible, continuando en modo offline")
                    self.postgres_manager = None
            except Exception as e:
                logging.warning(f"Advertencia inicializando BD: {e}")
                self.postgres_manager = None
            
            try:
                self.supabase_service = SupabaseService()
            except Exception as e:
                logging.warning(f"Advertencia inicializando Supabase: {e}")
                self.supabase_service = None
            
            # Variable para usuario actual
            self.current_user = None
            self.main_window = None
            
            # Mostrar ventana de login
            self.show_login()
            
        except Exception as e:
            logging.error(f"Error crítico en __init__: {e}")
            try:
                QMessageBox.critical(None, "Error Fatal", f"Error inicializando la aplicación:\n{e}")
            except:
                pass
            sys.exit(1)
        
    def show_login(self):
        """Mostrar ventana de login"""
        try:
            login_window = LoginWindow(self.postgres_manager, self.supabase_service)
            login_window.login_success.connect(self.on_login_success)
            login_window.show()
            
            # Guardar referencia para evitar que se destruya
            self.login_window = login_window
            
        except Exception as e:
            logging.error(f"Error al mostrar ventana de login: {e}")
            sys.exit(1)
    
    def on_login_success(self, user_data):
        """Manejar login exitoso"""
        try:
            self.current_user = user_data
            logging.info(f"Usuario autenticado: {self.current_user['username']}")
            
            # Cerrar ventana de login
            self.login_window.close()
            
            # Mostrar ventana principal
            self.show_main_window()
            
        except Exception as e:
            logging.error(f"Error al procesar login exitoso: {e}")
    
    def show_main_window(self):
        """Mostrar ventana principal del POS"""
        try:
            self.main_window = MainPOSWindow(
                self.current_user,
                self.postgres_manager,
                self.supabase_service
            )
            self.main_window.logout_requested.connect(self.on_logout)
            self.main_window.show()
            
        except Exception as e:
            logging.error(f"Error al mostrar ventana principal: {e}")
    
    def on_logout(self):
        """Manejar cierre de sesión"""
        try:
            # Cerrar ventana principal
            if self.main_window:
                self.main_window.close()
                self.main_window = None
            
            # Volver a mostrar login
            self.current_user = None
            self.show_login()
            
        except Exception as e:
            logging.error(f"Error al cerrar sesión: {e}")
    
    def run(self):
        """Ejecutar la aplicación"""
        try:
            return self.app.exec()
        except Exception as e:
            logging.error(f"Error durante ejecución: {e}")
            return 1

if __name__ == "__main__":
    app = POSApplication()
    sys.exit(app.run())
