"""
Script de prueba para verificar el procesamiento de ventas
"""

import sqlite3
import os
from datetime import datetime

def verificar_venta():
    """Verificar que las ventas se procesen correctamente"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'pos_htf.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("="*60)
    print("VERIFICACIÓN DE SISTEMA DE VENTAS")
    print("="*60)
    
    # 1. Verificar productos disponibles
    print("\n1️⃣  PRODUCTOS DISPONIBLES:")
    cursor.execute("""
        SELECT 
            p.id_producto,
            p.codigo_interno,
            p.nombre,
            p.precio_venta,
            COALESCE(i.stock_actual, 0) as stock
        FROM ca_productos_varios p
        LEFT JOIN inventario i ON p.codigo_interno = i.codigo_interno
        WHERE p.activo = 1
        LIMIT 5
    """)
    
    productos = cursor.fetchall()
    for prod in productos:
        print(f"  • [{prod['codigo_interno']}] {prod['nombre']}")
        print(f"    Precio: ${prod['precio_venta']:.2f} | Stock: {prod['stock']} unidades")
    
    # 2. Verificar última venta
    print("\n2️⃣  ÚLTIMA VENTA REGISTRADA:")
    cursor.execute("""
        SELECT 
            v.id_venta,
            v.fecha,
            v.total,
            v.estado,
            u.nombre_completo as vendedor,
            COUNT(dv.id_detalle) as items
        FROM ventas v
        LEFT JOIN usuarios u ON v.id_usuario = u.id_usuario
        LEFT JOIN detalles_venta dv ON v.id_venta = dv.id_venta
        GROUP BY v.id_venta
        ORDER BY v.fecha DESC
        LIMIT 1
    """)
    
    ultima_venta = cursor.fetchone()
    if ultima_venta:
        print(f"  ID Venta: {ultima_venta['id_venta']}")
        print(f"  Fecha: {ultima_venta['fecha']}")
        print(f"  Total: ${ultima_venta['total']:.2f}")
        print(f"  Estado: {ultima_venta['estado']}")
        print(f"  Vendedor: {ultima_venta['vendedor']}")
        print(f"  Items: {ultima_venta['items']}")
        
        # Detalles de la venta
        print("\n  📋 Detalles:")
        cursor.execute("""
            SELECT 
                nombre_producto,
                cantidad,
                precio_unitario,
                subtotal_linea
            FROM detalles_venta
            WHERE id_venta = ?
        """, (ultima_venta['id_venta'],))
        
        detalles = cursor.fetchall()
        for det in detalles:
            print(f"    - {det['nombre_producto']}: {det['cantidad']} x ${det['precio_unitario']:.2f} = ${det['subtotal_linea']:.2f}")
    else:
        print("  ⚠️  No hay ventas registradas")
    
    # 3. Total de ventas hoy
    print("\n3️⃣  VENTAS DEL DÍA:")
    cursor.execute("""
        SELECT 
            COUNT(*) as total_ventas,
            COALESCE(SUM(total), 0) as total_dinero
        FROM ventas
        WHERE DATE(fecha) = DATE('now')
    """)
    
    ventas_hoy = cursor.fetchone()
    print(f"  Total ventas: {ventas_hoy['total_ventas']}")
    print(f"  Total recaudado: ${ventas_hoy['total_dinero']:.2f}")
    
    # 4. Verificar stock bajo
    print("\n4️⃣  PRODUCTOS CON STOCK BAJO:")
    cursor.execute("""
        SELECT 
            p.codigo_interno,
            p.nombre,
            i.stock_actual,
            i.stock_minimo
        FROM inventario i
        JOIN ca_productos_varios p ON i.codigo_interno = p.codigo_interno
        WHERE i.stock_actual <= i.stock_minimo
        LIMIT 5
    """)
    
    stock_bajo = cursor.fetchall()
    if stock_bajo:
        for prod in stock_bajo:
            print(f"  ⚠️  {prod['nombre']}: {prod['stock_actual']} (min: {prod['stock_minimo']})")
    else:
        print("  ✅ Todos los productos tienen stock suficiente")
    
    conn.close()
    
    print("\n" + "="*60)
    print("✅ Verificación completada")
    print("="*60)

if __name__ == '__main__':
    verificar_venta()
