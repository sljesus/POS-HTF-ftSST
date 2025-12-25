#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script mejorado para generar ejecutable de distribución
Incluye todos los archivos necesarios para punto de venta
"""
import subprocess
import sys
import os
import shutil
import io

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("="*70)
print("🔨 CONSTRUCCIÓN DE EJECUTABLE PARA PUNTO DE VENTA")
print("="*70)
print(f"📍 Directorio: {os.getcwd()}")
print(f"📄 Script principal: main.py")
print()

# Verificar que existe main.py
if not os.path.exists("main.py"):
    print("❌ Error: No se encontró main.py")
    sys.exit(1)

# Verificar si existe .env
env_exists = os.path.exists(".env")
if env_exists:
    print("✅ Archivo .env encontrado")
else:
    print("⚠️  Archivo .env no encontrado (la app funcionará en modo offline)")

# Verificar icono
icon_path = os.path.join("assets", "pos_icono.ico")
icon_exists = os.path.exists(icon_path)
if icon_exists:
    print(f"✅ Icono encontrado: {icon_path}")
else:
    print(f"⚠️  Icono no encontrado: {icon_path}")

print("\n" + "="*70)
print("🔨 Iniciando construcción...")
print("="*70 + "\n")

# Construir rutas absolutas para --add-data
def get_add_data_args():
    """Generar argumentos --add-data con rutas correctas"""
    data_items = []
    for folder in ['database', 'ui', 'services', 'utils']:
        src = os.path.abspath(folder)
        if os.path.exists(src):
            # En Windows: source;destination
            data_items.append(f"{src};{folder}")
        else:
            print(f"⚠️  Advertencia: Carpeta '{folder}' no encontrada")
    return data_items

# Construir comando PyInstaller
add_data_items = get_add_data_args()
cmd = [
    sys.executable, "-m", "PyInstaller",
    "--onedir",  # Modo carpeta (mejor para distribución)
    "--console",  # CON CONSOLA para ver errores (cambiar a --windowed después de depurar)
    "--name", "HTF_Gimnasio_POS",
    "--distpath", "dist_app",
    "--workpath", "build_app",
    "--specpath", "spec_app",
    "--clean",
    "--noconfirm",
]

# Agregar --add-data para cada carpeta
for data_item in add_data_items:
    cmd.extend(["--add-data", data_item])

# Incluir icono si existe
if icon_exists:
    cmd.extend(["--icon", os.path.abspath(icon_path)])

# Hidden imports y script principal
cmd.extend([
    # Hidden imports necesarios
    "--hidden-import=sqlite3",
    "--hidden-import=PySide6.QtCore",
    "--hidden-import=PySide6.QtGui",
    "--hidden-import=PySide6.QtWidgets",
    "--hidden-import=dotenv",
    "--hidden-import=supabase",
    "--hidden-import=psycopg2",
    "--hidden-import=psycopg2.extensions",
    "--hidden-import=qtawesome",
    "--hidden-import=openpyxl",
    "--hidden-import=pandas",
    
    os.path.abspath("main.py")
])

print("✓ Comando PyInstaller:")
print(" ".join(cmd))
print("\n" + "="*70 + "\n")

try:
    # Ejecutar PyInstaller
    result = subprocess.run(cmd, check=True)
    
    if result.returncode == 0:
        dist_dir = "dist_app/HTF_Gimnasio_POS"
        exe_path = os.path.join(dist_dir, "HTF_Gimnasio_POS.exe")
        
        if os.path.exists(exe_path):
            # Información del ejecutable generado
            size_mb = os.path.getsize(exe_path) / (1024*1024)
            
            print("\n" + "="*70)
            print("✅ ¡EJECUTABLE GENERADO EXITOSAMENTE!")
            print("="*70)
            print(f"📦 Ubicación: {dist_dir}")
            print(f"📊 Tamaño del .exe: {size_mb:.1f} MB")
            print("⚠️  NOTA: El ejecutable está en modo CONSOLA para depuración")
            print("   (podrás ver los errores en la ventana de consola)")
            
            # Copiar .env si existe
            if env_exists:
                env_dest = os.path.join(dist_dir, ".env")
                shutil.copy2(".env", env_dest)
                print(f"✅ Archivo .env copiado a: {env_dest}")
            else:
                print("⚠️  RECUERDA: Copiar el archivo .env manualmente a la carpeta de distribución")
            
            # Crear archivo README de instalación
            readme_path = os.path.join(dist_dir, "README_INSTALACION.txt")
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write("""HTF GIMNASIO - SISTEMA POS
===========================

INSTRUCCIONES DE INSTALACIÓN
-----------------------------

1. COPIAR TODA LA CARPETA
   - Copia la carpeta completa "HTF_Gimnasio_POS" a la computadora del punto de venta
   - Puedes copiarla a cualquier ubicación (ej: C:\\Program Files\\HTF_POS o Escritorio)

2. ARCHIVO .env (CREDENCIALES)
   - Si no existe el archivo .env en esta carpeta, créalo con las siguientes variables:
   
     SUPABASE_URL=https://tu-proyecto.supabase.co
     SUPABASE_KEY=tu-clave-anon
     SUPABASE_ROLE_KEY=tu-clave-service-role
     
   - Este archivo es necesario para la conexión con Supabase
   - Si no se configura, la aplicación funcionará en modo offline únicamente

3. EJECUTAR LA APLICACIÓN
   - Haz doble clic en "HTF_Gimnasio_POS.exe"
   - La primera ejecución puede tardar unos segundos
   - Si aparece una ventana negra (consola), es normal - muestra información de depuración
   - NO elimines ningún archivo de esta carpeta

4. REQUISITOS DEL SISTEMA
   - Windows 7 o superior
   - Visual C++ Redistributables 2015-2022 (si falta, descargar de Microsoft)
   - No requiere Python instalado
   - No requiere instalación adicional de software

5. SOLUCIÓN DE PROBLEMAS
   - Si la aplicación no inicia:
     * Verifica que exista el archivo .env
     * Revisa los permisos de la carpeta
     * Si ves un error en la consola, anota el mensaje completo
     * Verifica que Visual C++ Redistributables esté instalado
   - Si aparece un error de DLL faltante:
     * Descarga e instala: Microsoft Visual C++ Redistributables
     * https://aka.ms/vs/17/release/vc_redist.x64.exe
   - Logs de error se guardan en: pos_htf.log (en esta misma carpeta)

NOTAS
-----
- Todos los archivos de esta carpeta son necesarios
- NO muevas o renombres archivos individuales
- Los logs se guardan en pos_htf.log en la misma carpeta
- La ventana de consola muestra información útil para depuración
""")
            
            print(f"✅ README de instalación creado: {readme_path}")
            
            # Crear script de diagnóstico
            diagnostic_script = os.path.join(dist_dir, "diagnostico.bat")
            with open(diagnostic_script, 'w', encoding='utf-8') as f:
                f.write("""@echo off
chcp 65001 >nul
echo ========================================
echo DIAGNOSTICO DEL SISTEMA POS
echo ========================================
echo.
echo Verificando archivos necesarios...
echo.

if exist "HTF_Gimnasio_POS.exe" (
    echo [OK] Ejecutable encontrado
) else (
    echo [ERROR] Ejecutable NO encontrado
)

if exist ".env" (
    echo [OK] Archivo .env encontrado
) else (
    echo [ADVERTENCIA] Archivo .env NO encontrado
)

if exist "_internal" (
    echo [OK] Carpeta _internal encontrada
) else (
    echo [ERROR] Carpeta _internal NO encontrada
)

if exist "pos_htf.log" (
    echo [OK] Archivo de log encontrado
    echo.
    echo Ultimas lineas del log:
    echo ----------------------------------------
    powershell -Command "Get-Content pos_htf.log -Tail 20 -Encoding UTF8"
    echo ----------------------------------------
) else (
    echo [INFO] Archivo de log no existe (normal si no se ha ejecutado)
)

echo.
echo ========================================
echo Ejecutando aplicacion...
echo ========================================
echo.
HTF_Gimnasio_POS.exe
pause
""")
            
            print(f"✅ Script de diagnóstico creado: {diagnostic_script}")
            
            print("\n" + "="*70)
            print("📦 PAQUETE LISTO PARA DISTRIBUIR")
            print("="*70)
            print(f"📁 Carpeta completa: {dist_dir}")
            print("\n💡 INSTRUCCIONES:")
            print("   1. Copia TODA la carpeta 'HTF_Gimnasio_POS' a la computadora del punto de venta")
            if not env_exists:
                print("   2. IMPORTANTE: Copia el archivo .env a la carpeta de distribución")
            print("   3. Ejecuta HTF_Gimnasio_POS.exe desde la carpeta copiada")
            print("   4. Si hay errores, ejecuta diagnostico.bat para ver información detallada")
            print()
        else:
            print("❌ Error: El ejecutable no se generó correctamente")
            sys.exit(1)
            
except subprocess.CalledProcessError as e:
    print(f"\n❌ Error durante la compilación: {e}")
    print("\n💡 Verifica que PyInstaller esté instalado:")
    print("   pip install pyinstaller")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error inesperado: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
