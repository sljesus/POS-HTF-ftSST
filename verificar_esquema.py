"""
Script de verificación de esquema de base de datos SQLite del POS
Verifica que todas las tablas necesarias estén creadas correctamente
"""

import sqlite3
import os

def verificar_esquema():
    """Verificar que todas las tablas requeridas existan"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'pos_htf.db')
    
    if not os.path.exists(db_path):
        print("❌ Base de datos no encontrada")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tablas requeridas
    tablas_requeridas = [
        'usuarios',
        'miembros',
        'personal',
        'ca_productos_varios',
        'ca_suplementos',
        'ca_productos_digitales',
        'lockers',
        'inventario',
        'costos_productos',
        'ventas',
        'detalles_venta',
        'movimientos_inventario',
        'turnos_caja',
        'registro_entradas',
        'sync_log'
    ]
    
    print("=" * 60)
    print("VERIFICACIÓN DE ESQUEMA DE BASE DE DATOS POS")
    print("=" * 60)
    print()
    
    # Obtener todas las tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tablas_existentes = [row[0] for row in cursor.fetchall()]
    
    print(f"📊 Total de tablas encontradas: {len(tablas_existentes)}")
    print()
    
    # Verificar cada tabla requerida
    tablas_ok = []
    tablas_faltantes = []
    
    for tabla in tablas_requeridas:
        if tabla in tablas_existentes:
            # Obtener información de la tabla
            cursor.execute(f"PRAGMA table_info({tabla})")
            columnas = cursor.fetchall()
            num_columnas = len(columnas)
            
            print(f"✅ {tabla:<30} ({num_columnas} columnas)")
            tablas_ok.append(tabla)
        else:
            print(f"❌ {tabla:<30} FALTANTE")
            tablas_faltantes.append(tabla)
    
    print()
    print("=" * 60)
    print(f"Resultado: {len(tablas_ok)}/{len(tablas_requeridas)} tablas correctas")
    
    if tablas_faltantes:
        print()
        print("⚠️  TABLAS FALTANTES:")
        for tabla in tablas_faltantes:
            print(f"   - {tabla}")
        print()
        return False
    else:
        print()
        print("✅ TODAS LAS TABLAS NECESARIAS ESTÁN PRESENTES")
        print()
        
        # Mostrar información adicional
        print("📋 TABLAS ADICIONALES ENCONTRADAS:")
        tablas_extra = [t for t in tablas_existentes if t not in tablas_requeridas]
        if tablas_extra:
            for tabla in tablas_extra:
                print(f"   - {tabla}")
        else:
            print("   (ninguna)")
        print()
        
        return True
    
    conn.close()

if __name__ == "__main__":
    verificar_esquema()
