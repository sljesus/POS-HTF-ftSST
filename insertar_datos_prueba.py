"""
Script para insertar datos de prueba en la base de datos local
Para demostración del sistema POS HTF
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

def insertar_datos_prueba():
    """Insertar datos de prueba completos en la base de datos"""
    
    # Conectar a la base de datos
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'pos_htf.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🚀 Iniciando inserción de datos de prueba...")
    
    # ========== 1. MIEMBROS DE PRUEBA ==========
    print("\n📝 Insertando miembros de prueba...")
    
    miembros = [
        ("Juan Carlos", "Pérez", "García", "3331234567", "juan.perez@email.com", "Pedro López", "3339876543", "MIEMBRO001", 1, "1990-05-15"),
        ("María", "González", "Martínez", "3332345678", "maria.gonzalez@email.com", "José González", "3338765432", "MIEMBRO002", 1, "1992-08-20"),
        ("Roberto", "Sánchez", "López", "3333456789", "roberto.sanchez@email.com", "Ana Sánchez", "3337654321", "MIEMBRO003", 1, "1988-11-10"),
        ("Ana Laura", "Ramírez", "Torres", "3334567890", "ana.ramirez@email.com", "Carlos Ramírez", "3336543210", "MIEMBRO004", 1, "1995-03-25"),
        ("Carlos", "Mendoza", "Flores", "3335678901", "carlos.mendoza@email.com", "Laura Mendoza", "3335432109", "MIEMBRO005", 1, "1993-07-30"),
        ("Laura", "Jiménez", "Castro", "3336789012", "laura.jimenez@email.com", "Miguel Jiménez", "3334321098", "MIEMBRO006", 1, "1991-12-05"),
        ("Miguel", "Ortiz", "Ruiz", "3337890123", "miguel.ortiz@email.com", "Patricia Ortiz", "3333210987", "MIEMBRO007", 1, "1989-06-18"),
        ("Patricia", "Hernández", "Morales", "3338901234", "patricia.hernandez@email.com", "Roberto Hernández", "3332109876", "MIEMBRO008", 1, "1994-09-22"),
        ("Fernando", "Cruz", "Domínguez", "3339012345", "fernando.cruz@email.com", "Carmen Cruz", "3331098765", "MIEMBRO009", 1, "1987-02-14"),
        ("Carmen", "Vargas", "Reyes", "3330123456", "carmen.vargas@email.com", "Fernando Vargas", "3330987654", "MIEMBRO010", 1, "1996-04-08")
    ]
    
    for miembro in miembros:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO miembros (
                    nombres, apellido_paterno, apellido_materno, telefono, email,
                    contacto_emergencia, telefono_emergencia, codigo_qr, activo, fecha_nacimiento
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, miembro)
        except Exception as e:
            print(f"  ⚠️  Error insertando miembro {miembro[0]}: {e}")
    
    print(f"  ✅ {len(miembros)} miembros insertados")
    
    # ========== 2. PRODUCTOS VARIOS ==========
    print("\n🥤 Insertando productos varios...")
    
    productos_varios = [
        ("BEB001", "7501234567890", "Coca Cola 600ml", "Refresco de cola", 20.00, "Bebidas", 1, 600),
        ("BEB002", "7501234567891", "Agua Ciel 1L", "Agua purificada", 12.00, "Bebidas", 0, 1000),
        ("BEB003", "7501234567892", "Gatorade Naranja", "Bebida isotónica sabor naranja", 25.00, "Bebidas", 1, 600),
        ("BEB004", "7501234567893", "Red Bull 250ml", "Bebida energética", 35.00, "Bebidas", 1, 250),
        ("SNK001", "7501234567894", "Sabritas Originales", "Papas fritas naturales", 18.00, "Snacks", 0, 45),
        ("SNK002", "7501234567895", "Doritos Nacho", "Totopos sabor queso", 20.00, "Snacks", 0, 62),
        ("SNK003", "7501234567896", "Barritas de Granola", "Barra de granola con miel", 15.00, "Snacks", 0, 35),
        ("SNK004", "7501234567897", "Almendras Saladas 100g", "Almendras naturales con sal", 45.00, "Snacks", 0, 100),
        ("ACC001", "7501234567898", "Toalla Deportiva", "Toalla de microfibra 40x80cm", 120.00, "Accesorios", 0, 200),
        ("ACC002", "7501234567899", "Guantes Gym M", "Guantes para entrenamiento talla M", 180.00, "Accesorios", 0, 150),
        ("ACC003", "7501234567800", "Shaker 700ml", "Vaso mezclador para proteína", 85.00, "Accesorios", 0, 150),
        ("ACC004", "7501234567801", "Banda Elástica", "Banda de resistencia media", 95.00, "Accesorios", 0, 80)
    ]
    
    for prod in productos_varios:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO ca_productos_varios (
                    codigo_interno, codigo_barras, nombre, descripcion,
                    precio_venta, categoria, requiere_refrigeracion, peso_gr
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, prod)
        except Exception as e:
            print(f"  ⚠️  Error insertando producto {prod[2]}: {e}")
    
    print(f"  ✅ {len(productos_varios)} productos varios insertados")
    
    # ========== 3. SUPLEMENTOS ==========
    print("\n💊 Insertando suplementos...")
    
    suplementos = [
        ("SUP001", "7501234560001", "Whey Protein Gold Standard", "Proteína de suero de leche premium", "Optimum Nutrition", "Proteína", 2270, 899.00, "2026-06-15"),
        ("SUP002", "7501234560002", "Creatina Monohidratada", "Creatina pura micronizada", "Dymatize", "Creatina", 300, 320.00, "2026-08-20"),
        ("SUP003", "7501234560003", "Pre Workout C4 Original", "Pre-entreno con cafeína y beta-alanina", "Cellucor", "Pre-entreno", 390, 550.00, "2026-04-10"),
        ("SUP004", "7501234560004", "BCAA Powder 5000", "Aminoácidos de cadena ramificada 2:1:1", "Optimum Nutrition", "BCAA", 345, 480.00, "2026-07-25"),
        ("SUP005", "7501234560005", "Glutamina Powder", "L-Glutamina pura en polvo", "MuscleTech", "Glutamina", 300, 380.00, "2026-05-18"),
        ("SUP006", "7501234560006", "Proteína Vegana", "Proteína de chícharo y arroz", "Garden of Life", "Proteína", 620, 650.00, "2026-09-30"),
        ("SUP007", "7501234560007", "Quemador Hydroxycut", "Termogénico con cafeína", "MuscleTech", "Quemador", 180, 520.00, "2026-03-15"),
        ("SUP008", "7501234560008", "Mass Gainer Serious", "Ganador de peso con carbohidratos", "Optimum Nutrition", "Ganador de Masa", 5450, 1250.00, "2026-10-20"),
        ("SUP009", "7501234560009", "Multivitamínico Opti-Men", "Complejo vitamínico para hombres", "Optimum Nutrition", "Vitaminas", 240, 420.00, "2027-01-15"),
        ("SUP010", "7501234560010", "ZMA Capsulas", "Zinc, Magnesio y Vitamina B6", "Universal Nutrition", "Vitaminas", 180, 280.00, "2026-11-05")
    ]
    
    for sup in suplementos:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO ca_suplementos (
                    codigo_interno, codigo_barras, nombre, descripcion, marca, tipo,
                    peso_neto_gr, precio_venta, fecha_vencimiento
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, sup)
        except Exception as e:
            print(f"  ⚠️  Error insertando suplemento {sup[1]}: {e}")
    
    print(f"  ✅ {len(suplementos)} suplementos insertados")
    
    # ========== 4. INVENTARIO ==========
    print("\n📦 Creando registros de inventario...")
    
    # Obtener todos los códigos de productos
    cursor.execute("SELECT codigo_interno FROM ca_productos_varios")
    codigos_varios = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT codigo_interno FROM ca_suplementos")
    codigos_suplementos = [row[0] for row in cursor.fetchall()]
    
    inventarios_count = 0
    
    # Inventario para productos varios
    for codigo in codigos_varios:
        stock = random.randint(10, 100)
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO inventario (
                    codigo_interno, tipo_producto, stock_actual, stock_minimo, ubicacion
                ) VALUES (?, 'varios', ?, 5, 'Recepción')
            """, (codigo, stock))
            inventarios_count += 1
        except:
            pass
    
    # Inventario para suplementos
    for codigo in codigos_suplementos:
        stock = random.randint(5, 50)
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO inventario (
                    codigo_interno, tipo_producto, stock_actual, stock_minimo, ubicacion
                ) VALUES (?, 'suplemento', ?, 2, 'Vitrina')
            """, (codigo, stock))
            inventarios_count += 1
        except:
            pass
    
    print(f"  ✅ {inventarios_count} registros de inventario creados")
    
    # ========== 5. REGISTROS DE ACCESO ==========
    print("\n🚪 Insertando registros de acceso...")
    
    # Obtener IDs de miembros
    cursor.execute("SELECT id_miembro FROM miembros WHERE activo = 1")
    ids_miembros = [row[0] for row in cursor.fetchall()]
    
    accesos_count = 0
    if ids_miembros:
        # Crear accesos de los últimos 7 días
        for dias_atras in range(7):
            fecha = datetime.now() - timedelta(days=dias_atras)
            # 5-15 accesos por día
            num_accesos = random.randint(5, 15)
            
            for _ in range(num_accesos):
                id_miembro = random.choice(ids_miembros)
                hora = fecha.replace(
                    hour=random.randint(6, 21),
                    minute=random.randint(0, 59),
                    second=random.randint(0, 59)
                )
                
                try:
                    cursor.execute("""
                        INSERT INTO registro_entradas (
                            id_miembro, tipo_acceso, fecha_entrada, area_accedida, dispositivo_registro
                        ) VALUES (?, 'miembro', ?, 'General', 'POS_LOCAL')
                    """, (id_miembro, hora.strftime('%Y-%m-%d %H:%M:%S')))
                    accesos_count += 1
                except:
                    pass
    
    print(f"  ✅ {accesos_count} registros de acceso insertados")
    
    # ========== 6. VENTAS DE PRUEBA ==========
    print("\n💰 Insertando ventas de prueba...")
    
    ventas_count = 0
    detalles_count = 0
    
    # Obtener ID de usuario admin
    cursor.execute("SELECT id_usuario FROM usuarios WHERE rol = 'administrador' LIMIT 1")
    result = cursor.fetchone()
    id_usuario = result[0] if result else 1
    
    # Crear ventas de los últimos 3 días
    for dias_atras in range(3):
        fecha = datetime.now() - timedelta(days=dias_atras)
        # 3-8 ventas por día
        num_ventas = random.randint(3, 8)
        
        for _ in range(num_ventas):
            # Seleccionar productos aleatorios
            num_items = random.randint(1, 4)
            total_venta = 0
            items_venta = []
            
            for _ in range(num_items):
                # 70% productos varios, 30% suplementos
                if random.random() < 0.7 and codigos_varios:
                    codigo = random.choice(codigos_varios)
                    tipo = 'varios'
                    cursor.execute("SELECT nombre, precio_venta FROM ca_productos_varios WHERE codigo_interno = ?", (codigo,))
                elif codigos_suplementos:
                    codigo = random.choice(codigos_suplementos)
                    tipo = 'suplemento'
                    cursor.execute("SELECT nombre, precio_venta FROM ca_suplementos WHERE codigo_interno = ?", (codigo,))
                else:
                    continue
                
                result = cursor.fetchone()
                if result:
                    nombre, precio = result
                    cantidad = random.randint(1, 3)
                    subtotal = precio * cantidad
                    total_venta += subtotal
                    items_venta.append((codigo, tipo, cantidad, precio, subtotal, nombre))
            
            if items_venta:
                # Insertar venta
                hora_venta = fecha.replace(
                    hour=random.randint(8, 20),
                    minute=random.randint(0, 59)
                )
                
                try:
                    cursor.execute("""
                        INSERT INTO ventas (
                            id_usuario, fecha, subtotal, descuento, impuestos, total, 
                            metodo_pago, tipo_venta, estado
                        ) VALUES (?, ?, ?, 0, 0, ?, 'efectivo', 'directa', 'completada')
                    """, (id_usuario, hora_venta.strftime('%Y-%m-%d %H:%M:%S'), 
                          total_venta, total_venta))
                    
                    id_venta = cursor.lastrowid
                    ventas_count += 1
                    
                    # Insertar detalles
                    for codigo, tipo, cantidad, precio, subtotal, nombre in items_venta:
                        cursor.execute("""
                            INSERT INTO detalles_venta (
                                id_venta, codigo_interno, tipo_producto, cantidad,
                                precio_unitario, subtotal_linea, nombre_producto
                            ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (id_venta, codigo, tipo, cantidad, precio, subtotal, nombre))
                        detalles_count += 1
                except Exception as e:
                    print(f"  ⚠️  Error insertando venta: {e}")
    
    print(f"  ✅ {ventas_count} ventas insertadas con {detalles_count} items")
    
    # Confirmar cambios
    conn.commit()
    conn.close()
    
    print("\n" + "="*60)
    print("✨ ¡Datos de prueba insertados exitosamente!")
    print("="*60)
    print(f"""
📊 RESUMEN:
  • {len(miembros)} miembros activos
  • {len(productos_varios)} productos varios
  • {len(suplementos)} suplementos
  • {inventarios_count} items en inventario
  • {accesos_count} registros de acceso (últimos 7 días)
  • {ventas_count} ventas (últimos 3 días)
  • {detalles_count} items vendidos
    
🎯 La base de datos está lista para la demostración
    """)

if __name__ == '__main__':
    insertar_datos_prueba()
