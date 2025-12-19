#!/usr/bin/env python
"""Test rápido de todos los imports del proyecto"""

import sys
import os

print("🔍 Verificando imports...")

try:
    print("✓ Importing sys, os")
    
    print("✓ Importing logging, PySide6")
    import logging
    from PySide6.QtWidgets import QApplication
    
    print("✓ Importing Config")
    from utils.config import Config
    
    print("✓ Importing PostgresManager")
    from database.postgres_manager import PostgresManager
    
    print("✓ Importing SupabaseService")
    from services.supabase_service import SupabaseService
    
    print("✓ Importing LoginWindow")
    from ui.login_window_pyside import LoginWindow
    
    print("✓ Importing MainPOSWindow")
    from ui.main_pos_window import MainPOSWindow
    
    print("\n✅ ¡Todos los imports funcionan correctamente!")
    
except ImportError as e:
    print(f"\n❌ Error en import: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error inesperado: {e}")
    sys.exit(1)
