"""
Ejemplo de uso del PostgresManager actualizado para Supabase
"""

import os
from database.postgres_manager import PostgresManager
from datetime import datetime, timedelta

# ============================================================
# CONFIGURACIÓN DE CONEXIÓN A SUPABASE
# ============================================================

# Opción 1: Pasar credenciales directamente
config = {
    'url': 'https://tu-proyecto.supabase.co',  # Reemplazar con tu URL
    'key': 'tu-anon-key-aqui'                  # Reemplazar con tu key
}

# Opción 2: Usar variables de entorno (recomendado)
config = {
    'url': os.getenv('SUPABASE_URL'),
    'key': os.getenv('SUPABASE_KEY')
}

# ============================================================
# EJEMPLOS DE USO
# ============================================================

def ejemplo_autenticacion():
    """Ejemplo de autenticación de usuario"""
    print("\n=== AUTENTICACIÓN ===")
    
    db = PostgresManager(config)
    
    # Autenticar usuario
    user = db.authenticate_user('admin', 'password123')
    if user:
        print(f"✅ Usuario autenticado: {user['nombre_completo']}")
        print(f"   ID: {user['id_usuario']}")
        print(f"   Rol: {user['rol']}")
    else:
        print("❌ Autenticación fallida")
    
    db.close()

def ejemplo_crear_usuario():
    """Ejemplo de crear nuevo usuario"""
    print("\n=== CREAR USUARIO ===")
    
    db = PostgresManager(config)
    
    user_id = db.create_user(
        username='juan_perez',
        password='password123',
        nombre_completo='Juan Pérez García',
        rol='recepcionista'
    )
    
    if user_id:
        print(f"✅ Usuario creado con ID: {user_id}")
    else:
        print("❌ Error al crear usuario")
    
    db.close()

def ejemplo_productos():
    """Ejemplo de operaciones con productos"""
    print("\n=== PRODUCTOS ===")
    
    db = PostgresManager(config)
    
    # Obtener todos los productos
    productos = db.get_all_products()
    print(f"\n📦 Total de productos: {len(productos)}")
    for prod in productos[:3]:  # Mostrar los primeros 3
        print(f"   - {prod.get('nombre')}: ${prod.get('precio_venta')}")
    
    # Buscar producto por código de barras
    print("\n🔍 Buscar por código de barras:")
    producto = db.get_product_by_barcode('1234567890')
    if producto:
        print(f"   ✅ Encontrado: {producto.get('nombre')}")
    else:
        print("   ❌ No encontrado")
    
    # Buscar producto por código interno
    print("\n🔍 Buscar por código interno:")
    producto = db.get_product_by_code('PROD-001')
    if producto:
        print(f"   ✅ Encontrado: {producto.get('nombre')}")
    else:
        print("   ❌ No encontrado")
    
    db.close()

def ejemplo_crear_venta():
    """Ejemplo de crear una venta"""
    print("\n=== CREAR VENTA ===")
    
    db = PostgresManager(config)
    
    venta_data = {
        'id_usuario': 1,                    # ID del usuario (vendedor)
        'id_miembro': None,                 # Opcional: ID del miembro
        'total': 100.00,
        'descuento': 0,
        'impuestos': 18.00,
        'metodo_pago': 'efectivo',
        'tipo_venta': 'producto',
        'productos': [
            {
                'id_producto': 1,
                'cantidad': 2,
                'precio': 50.00,
                'subtotal': 100.00
            }
        ]
    }
    
    try:
        venta_id = db.create_sale(venta_data)
        if venta_id:
            print(f"✅ Venta creada con ID: {venta_id}")
        else:
            print("❌ Error al crear venta")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    db.close()

def ejemplo_miembros():
    """Ejemplo de operaciones con miembros"""
    print("\n=== MIEMBROS ===")
    
    db = PostgresManager(config)
    
    # Obtener total de miembros
    total = db.get_total_members()
    print(f"👥 Total de miembros activos: {total}")
    
    # Obtener miembro por código QR
    miembro = db.obtener_miembro_por_codigo_qr('QR123456')
    if miembro:
        print(f"\n✅ Miembro encontrado:")
        print(f"   Nombre: {miembro.get('nombres')} {miembro.get('apellido_paterno')}")
        print(f"   Email: {miembro.get('email')}")
    else:
        print("\n❌ Miembro no encontrado")
    
    db.close()

def ejemplo_entrada_salida():
    """Ejemplo de registrar entrada y salida"""
    print("\n=== REGISTRO DE ENTRADAS Y SALIDAS ===")
    
    db = PostgresManager(config)
    
    # Registrar entrada
    entrada_data = {
        'id_miembro': 1,
        'tipo_acceso': 'miembro',
        'area_accedida': 'General',
        'dispositivo_registro': 'POS',
        'notas': 'Entrada normal'
    }
    
    entrada_id = db.registrar_entrada(entrada_data)
    if entrada_id:
        print(f"✅ Entrada registrada con ID: {entrada_id}")
        
        # Registrar salida (simulando que pasó tiempo)
        if db.registrar_salida(entrada_id):
            print(f"✅ Salida registrada para entrada {entrada_id}")
    else:
        print("❌ Error al registrar entrada")
    
    db.close()

def ejemplo_lockers():
    """Ejemplo de operaciones con lockers"""
    print("\n=== LOCKERS ===")
    
    db = PostgresManager(config)
    
    # Obtener todos los lockers
    lockers = db.get_lockers()
    print(f"🔐 Total de lockers: {len(lockers)}")
    for locker in lockers[:3]:
        print(f"   - Locker {locker.get('numero')}: {locker.get('tipo')}")
    
    # Insertar nuevo locker
    nuevo_locker = db.insertar_locker({
        'numero': 'L-101',
        'ubicacion': 'Zona Principal',
        'tipo': 'grande',
        'requiere_llave': True
    })
    
    if nuevo_locker:
        print(f"\n✅ Nuevo locker creado con ID: {nuevo_locker}")
    else:
        print("\n❌ Error al crear locker")
    
    db.close()

def ejemplo_productos_digitales():
    """Ejemplo de operaciones con productos digitales"""
    print("\n=== PRODUCTOS DIGITALES ===")
    
    db = PostgresManager(config)
    
    # Obtener productos digitales
    productos = db.get_productos_digitales()
    print(f"💻 Total de productos digitales: {len(productos)}")
    for prod in productos[:3]:
        print(f"   - {prod.get('nombre')}: ${prod.get('precio_venta')}")
    
    # Crear producto digital
    nuevo_producto = db.insertar_producto_digital({
        'codigo_interno': 'MEM-GOLD',
        'nombre': 'Membresía Gold',
        'descripcion': 'Acceso ilimitado + clase grupal',
        'tipo': 'membresia_gym',
        'precio_venta': 200.00,
        'duracion_dias': 30,
        'aplica_domingo': True,
        'aplica_festivo': False,
        'es_unico': False,
        'requiere_asignacion': True
    })
    
    if nuevo_producto:
        print(f"\n✅ Producto digital creado con ID: {nuevo_producto}")
    else:
        print("\n❌ Error al crear producto digital")
    
    db.close()

def ejemplo_notificaciones():
    """Ejemplo de operaciones con notificaciones"""
    print("\n=== NOTIFICACIONES ===")
    
    db = PostgresManager(config)
    
    # Crear notificación de pago
    notif_id = db.crear_notificacion_pago({
        'id_miembro': 1,
        'id_venta_digital': None,
        'tipo_notificacion': 'pago_pendiente',
        'asunto': 'Pago Pendiente',
        'descripcion': 'Tienes un pago pendiente de membresía',
        'monto_pendiente': 150.00,
        'fecha_vencimiento': (datetime.now() + timedelta(days=7)).isoformat(),
        'para_miembro': True,
        'para_recepcion': True
    })
    
    if notif_id:
        print(f"✅ Notificación creada con ID: {notif_id}")
        
        # Obtener notificaciones pendientes
        pendientes = db.get_notificaciones_pendientes()
        print(f"\n📬 Notificaciones pendientes: {len(pendientes)}")
        
        # Marcar como leída
        if db.marcar_notificacion_como_leida(notif_id):
            print(f"✅ Notificación {notif_id} marcada como leída")
    else:
        print("❌ Error al crear notificación")
    
    db.close()

def ejemplo_turnos_caja():
    """Ejemplo de operaciones con turnos de caja"""
    print("\n=== TURNOS DE CAJA ===")
    
    db = PostgresManager(config)
    
    # Abrir turno de caja
    turno_id = db.abrir_turno_caja(id_usuario=1, monto_inicial=500.00)
    
    if turno_id:
        print(f"✅ Turno de caja abierto con ID: {turno_id}")
        
        # Obtener turno activo
        turno = db.get_turno_activo(id_usuario=1)
        if turno:
            print(f"\n📊 Turno activo:")
            print(f"   ID: {turno.get('id_turno')}")
            print(f"   Monto inicial: ${turno.get('monto_inicial')}")
        
        # Cerrar turno (simulando cierre después de ventas)
        if db.cerrar_turno_caja(turno_id, monto_real_cierre=650.00):
            print(f"\n✅ Turno {turno_id} cerrado")
            print(f"   Diferencia: $150.00 (ganancias del día)")
    else:
        print("❌ Error al abrir turno de caja")
    
    db.close()

def ejemplo_inventario():
    """Ejemplo de operaciones con inventario"""
    print("\n=== INVENTARIO ===")
    
    db = PostgresManager(config)
    
    # Verificar si producto existe
    existe = db.producto_existe('PROD-001')
    print(f"📦 ¿Existe producto PROD-001? {'Sí' if existe else 'No'}")
    
    # Crear inventario
    inv_creado = db.crear_inventario({
        'codigo_interno': 'PROD-001',
        'tipo_producto': 'varios',
        'stock_actual': 50,
        'stock_minimo': 10,
        'id_ubicacion': 1,
        'activo': True
    })
    
    if inv_creado:
        print(f"✅ Inventario creado para PROD-001")
    else:
        print(f"❌ Error al crear inventario")
    
    db.close()

# ============================================================
# EJECUTAR EJEMPLOS
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("EJEMPLOS DE USO - PostgresManager con Supabase")
    print("=" * 60)
    
    try:
        ejemplo_autenticacion()
        # ejemplo_crear_usuario()
        # ejemplo_productos()
        # ejemplo_miembros()
        # ejemplo_entrada_salida()
        # ejemplo_lockers()
        # ejemplo_productos_digitales()
        # ejemplo_notificaciones()
        # ejemplo_turnos_caja()
        # ejemplo_inventario()
        
        print("\n" + "=" * 60)
        print("✅ Ejemplos completados")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
