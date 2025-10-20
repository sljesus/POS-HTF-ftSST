"""
Script para generar ejecutable de Windows para POS HTF
Requiere: pip install pyinstaller
"""

import os
import subprocess
import sys

def build_exe():
    """Construir ejecutable de Windows"""
    
    # Configuración del build
    app_name = "HTF_Gimnasio_POS"
    main_script = "main.py"
    
    # Comando pyinstaller
    command = [
        "pyinstaller",
        "--onefile",  # Un solo archivo ejecutable
        "--windowed",  # Sin consola (GUI only)
        f"--name={app_name}",
        "--clean",  # Limpiar archivos temporales
        "--noconfirm",  # No confirmar sobrescritura
        
        # Incluir archivos adicionales
        "--add-data=database;database",
        "--add-data=ui;ui", 
        "--add-data=services;services",
        "--add-data=utils;utils",
        "--add-data=.env;.",
        
        # Ocultar imports no encontrados
        "--hidden-import=sqlite3",
        "--hidden-import=PySide6",
        "--hidden-import=dotenv",
        "--hidden-import=supabase",
        "--hidden-import=psycopg2",
        
        main_script
    ]
    
    print("🔨 Construyendo ejecutable de Windows...")
    print(f"📁 Nombre: {app_name}.exe")
    print(f"📄 Script principal: {main_script}")
    print()
    
    try:
        # Ejecutar pyinstaller
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        
        print("✅ Ejecutable creado exitosamente!")
        print(f"📍 Ubicación: dist/{app_name}.exe")
        print()
        print("📋 Para distribuir:")
        print("1. Copia el archivo .exe desde la carpeta 'dist'")
        print("2. Asegúrate de incluir el archivo .env si usas Supabase")
        print("3. El ejecutable no requiere Python instalado")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error construyendo ejecutable: {e}")
        print("Salida del error:", e.stderr)
        return False
    
    except FileNotFoundError:
        print("❌ PyInstaller no encontrado.")
        print("Instala con: pip install pyinstaller")
        return False
    
    return True

if __name__ == "__main__":
    if not os.path.exists("main.py"):
        print("❌ No se encontró main.py en el directorio actual")
        sys.exit(1)
    
    build_exe()