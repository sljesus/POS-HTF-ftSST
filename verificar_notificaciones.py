"""
Script de Verificación del Sistema de Notificaciones
Verifica el estado de la base de datos y componentes
"""

import sys
import os

# Agregar el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

def verificar_sistema():
    """Verificar estado completo del sistema"""
    
    print("\n" + "="*70)
    print("VERIFICACIÓN DEL SISTEMA DE NOTIFICACIONES")
    print("="*70 + "\n")
    
    try:
        # Inicializar base de datos
        db_path = os.path.join(os.path.dirname(__file__), 'database', 'pos_htf.db')
        db = DatabaseManager(db_path)
        db.initialize_database()
        
        cursor = db.connection.cursor()
        
        # 1. Verificar tabla de miembros
        print("📋 1. MIEMBROS")
        print("-" * 70)
        
        cursor.execute("SELECT COUNT(*) FROM miembros")
        total_miembros = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM miembros WHERE activo = 1")
        miembros_activos = cursor.fetchone()[0]
        
        print(f"   Total de miembros: {total_miembros}")
        print(f"   Miembros activos:  {miembros_activos}")
        
        if miembros_activos == 0:
            print("   ⚠️  ADVERTENCIA: No hay miembros activos")
            print("   Ejecuta: python insertar_datos_prueba.py")
        else:
            print("   ✓ OK")
        
        # 2. Verificar tabla de registro_entradas
        print("\n📊 2. REGISTRO DE ENTRADAS")
        print("-" * 70)
        
        cursor.execute("SELECT COUNT(*) FROM registro_entradas")
        total_entradas = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM registro_entradas WHERE DATE(fecha_entrada) = DATE('now')")
        entradas_hoy = cursor.fetchone()[0]
        
        cursor.execute("SELECT MAX(id_entrada) FROM registro_entradas")
        ultimo_id = cursor.fetchone()[0] or 0
        
        print(f"   Total de entradas: {total_entradas}")
        print(f"   Entradas hoy:      {entradas_hoy}")
        print(f"   Último ID:         {ultimo_id}")
        print("   ✓ OK")
        
        # 3. Verificar últimas 3 entradas
        if total_entradas > 0:
            print("\n📝 3. ÚLTIMAS ENTRADAS")
            print("-" * 70)
            
            cursor.execute("""
                SELECT 
                    re.id_entrada,
                    re.fecha_entrada,
                    m.nombres,
                    m.apellido_paterno
                FROM registro_entradas re
                INNER JOIN miembros m ON re.id_miembro = m.id_miembro
                ORDER BY re.fecha_entrada DESC
                LIMIT 3
            """)
            
            entradas = cursor.fetchall()
            
            for entrada in entradas:
                id_entrada = entrada[0]
                fecha = entrada[1]
                nombre = f"{entrada[2]} {entrada[3]}"
                print(f"   ID {id_entrada}: {nombre} - {fecha}")
            
            print("   ✓ OK")
        
        # 4. Verificar archivos de notificaciones
        print("\n📂 4. ARCHIVOS DEL SISTEMA")
        print("-" * 70)
        
        archivos_requeridos = [
            ("ui/notificacion_entrada_widget.py", "Widget de notificación"),
            ("utils/monitor_entradas.py", "Monitor de entradas"),
            ("test_simulador_entradas.py", "Simulador de pruebas"),
            ("test_entrada_rapida.py", "Script de entrada rápida")
        ]
        
        base_path = os.path.dirname(__file__)
        todos_ok = True
        
        for archivo, descripcion in archivos_requeridos:
            path = os.path.join(base_path, archivo)
            if os.path.exists(path):
                print(f"   ✓ {descripcion}")
            else:
                print(f"   ❌ {descripcion} - NO ENCONTRADO")
                todos_ok = False
        
        if todos_ok:
            print("   ✓ OK - Todos los archivos presentes")
        
        # 5. Verificar integración
        print("\n🔌 5. INTEGRACIÓN EN MAIN_POS_WINDOW")
        print("-" * 70)
        
        main_window_path = os.path.join(base_path, "ui", "main_pos_window.py")
        
        if os.path.exists(main_window_path):
            with open(main_window_path, 'r', encoding='utf-8') as f:
                contenido = f.read()
                
                checks = [
                    ("from ui.notificacion_entrada_widget import", "Import NotificacionEntradaWidget"),
                    ("from utils.monitor_entradas import", "Import MonitorEntradas"),
                    ("self.monitor_entradas =", "Variable monitor_entradas"),
                    ("def iniciar_monitor_entradas", "Método iniciar_monitor_entradas"),
                    ("def mostrar_notificacion_entrada", "Método mostrar_notificacion_entrada")
                ]
                
                for buscar, descripcion in checks:
                    if buscar in contenido:
                        print(f"   ✓ {descripcion}")
                    else:
                        print(f"   ❌ {descripcion} - NO ENCONTRADO")
                        todos_ok = False
            
            if todos_ok:
                print("   ✓ OK - Integración completa")
        else:
            print("   ❌ Archivo main_pos_window.py no encontrado")
        
        # Resumen final
        print("\n" + "="*70)
        print("RESUMEN")
        print("="*70)
        
        if miembros_activos > 0 and todos_ok:
            print("✓ Sistema de notificaciones configurado correctamente")
            print("\n📝 SIGUIENTE PASO:")
            print("   1. Abrir el POS: python main.py")
            print("   2. En otra terminal: python test_entrada_rapida.py")
            print("   3. Observar la notificación en el POS")
        elif miembros_activos == 0:
            print("⚠️  Configurar datos de prueba primero:")
            print("   python insertar_datos_prueba.py")
        else:
            print("❌ Hay problemas con la configuración")
            print("   Revisar los errores marcados arriba")
        
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_sistema()
