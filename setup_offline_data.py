"""
Script para generar datos de prueba adicionales
y verificar el funcionamiento offline completo
"""

import os
import sys
import logging
from datetime import datetime, timedelta
import random

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_sample_members(db_manager):
    """Crear miembros de prueba"""
    print("\n👥 CREANDO MIEMBROS DE PRUEBA")
    print("="*50)
    
    cursor = db_manager.connection.cursor()
    
    # Verificar si ya existen miembros
    cursor.execute("SELECT COUNT(*) FROM miembros")
    if cursor.fetchone()[0] > 0:
        print("✅ Ya existen miembros en la base de datos")
        return
    
    miembros_prueba = [
        ('Juan Carlos', 'García', 'López', '5551234567', 'juan.garcia@email.com', 'QR001'),
        ('María', 'Rodríguez', 'Hernández', '5551234568', 'maria.rodriguez@email.com', 'QR002'),
        ('Pedro', 'Martínez', 'González', '5551234569', 'pedro.martinez@email.com', 'QR003'),
        ('Ana', 'López', 'Sánchez', '5551234570', 'ana.lopez@email.com', 'QR004'),
        ('Carlos', 'Hernández', 'Ramírez', '5551234571', 'carlos.hernandez@email.com', 'QR005')
    ]
    
    for nombres, apellido_p, apellido_m, telefono, email, codigo_qr in miembros_prueba:
        cursor.execute('''
            INSERT INTO miembros 
            (nombres, apellido_paterno, apellido_materno, telefono, email, codigo_qr)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nombres, apellido_p, apellido_m, telefono, email, codigo_qr))
    
    db_manager.connection.commit()
    print(f"✅ {len(miembros_prueba)} miembros creados")

def update_inventory_stock(db_manager):
    """Actualizar stock del inventario"""
    print("\n📦 ACTUALIZANDO INVENTARIO")
    print("="*50)
    
    cursor = db_manager.connection.cursor()
    
    # Stock aleatorio para productos
    stock_updates = [
        ('PRD001', 50),  # Agua
        ('PRD002', 30),  # Gatorade  
        ('PRD003', 15),  # Toallas
        ('PRD004', 25),  # Barras proteína
        ('SUP001', 8),   # Whey Protein
        ('SUP002', 12),  # Creatina
        ('SUP003', 6)    # BCAA
    ]
    
    for codigo, stock in stock_updates:
        cursor.execute('''
            UPDATE inventario 
            SET stock_actual = ?, fecha_ultimo_conteo = CURRENT_DATE
            WHERE codigo_interno = ?
        ''', (stock, codigo))
    
    db_manager.connection.commit()
    print("✅ Inventario actualizado")

def create_sample_sale(db_manager):
    """Crear una venta de prueba"""
    print("\n💰 CREANDO VENTA DE PRUEBA")
    print("="*50)
    
    cursor = db_manager.connection.cursor()
    
    # Verificar si ya existen ventas
    cursor.execute("SELECT COUNT(*) FROM ventas")
    if cursor.fetchone()[0] > 0:
        print("✅ Ya existen ventas en la base de datos")
        return
    
    # Crear venta
    cursor.execute('''
        INSERT INTO ventas 
        (id_usuario, numero_ticket, subtotal, total, metodo_pago, tipo_venta)
        VALUES (1, 'TKT001', 80.00, 80.00, 'efectivo', 'producto')
    ''')
    
    venta_id = cursor.lastrowid
    
    # Crear detalles de venta
    detalles = [
        (venta_id, 'PRD001', 'varios', 2, 15.00, 30.00, 'Agua 600ml'),
        (venta_id, 'PRD004', 'varios', 1, 45.00, 45.00, 'Barra Proteína'),
        (venta_id, 'PRD002', 'varios', 1, 25.00, 25.00, 'Gatorade 500ml')
    ]
    
    for detalle in detalles:
        cursor.execute('''
            INSERT INTO detalles_venta 
            (id_venta, codigo_interno, tipo_producto, cantidad, precio_unitario, 
             subtotal_linea, nombre_producto)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', detalle)
    
    db_manager.connection.commit()
    print(f"✅ Venta creada: Ticket {venta_id}")

def show_database_summary(db_manager):
    """Mostrar resumen de la base de datos"""
    print("\n📊 RESUMEN DE BASE DE DATOS")
    print("="*50)
    
    cursor = db_manager.connection.cursor()
    
    # Contar registros por tabla
    tables = [
        ('usuarios', 'Usuarios'),
        ('miembros', 'Miembros'),
        ('ca_productos_varios', 'Productos Varios'),
        ('ca_suplementos', 'Suplementos'),
        ('ca_productos_digitales', 'Productos Digitales'),
        ('inventario', 'Items Inventario'),
        ('ventas', 'Ventas'),
        ('detalles_venta', 'Detalles de Venta')
    ]
    
    for table, name in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"📋 {name}: {count}")
    
    # Mostrar productos con stock
    print("\n📦 INVENTARIO ACTUAL:")
    inventario = db_manager.get_inventory_status()
    for item in inventario:
        print(f"   {item['codigo_interno']}: {item['nombre_producto']} - Stock: {item['stock_actual']}")

def main():
    """Función principal"""
    print("🚀 CONFIGURANDO BASE DE DATOS OFFLINE COMPLETA")
    
    try:
        # Inicializar base de datos
        db_manager = DatabaseManager()
        
        if not db_manager.initialize_database():
            print("❌ Error inicializando base de datos")
            return
        
        # Crear datos de prueba
        create_sample_members(db_manager)
        update_inventory_stock(db_manager)
        create_sample_sale(db_manager)
        
        # Mostrar resumen
        show_database_summary(db_manager)
        
        print("\n🎯 BASE DE DATOS LISTA PARA USO OFFLINE")
        print("="*50)
        print("✅ Usuarios: admin/admin123")
        print("✅ Productos y inventario configurados")
        print("✅ Miembros de prueba creados")
        print("✅ Venta de ejemplo registrada")
        print("✅ Sistema listo para funcionar sin internet")
        
        # Cerrar conexión
        db_manager.close_connection()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()