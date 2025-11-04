"""
Gestor de Base de Datos SQLite para POS HTF
Maneja el inventario offline y usuarios
"""

import sqlite3
import os
import logging
from datetime import datetime
import hashlib

class DatabaseManager:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), 'pos_htf.db')
        
        self.db_path = db_path
        self.connection = None
    
    def initialize_database(self):
        """Inicializar la base de datos y crear tablas"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Para acceso por nombre de columna
            
            # Crear tablas
            self.create_tables()
            
            # Insertar datos iniciales
            self.insert_initial_data()
            
            logging.info("Base de datos inicializada correctamente")
            return True
        
        except Exception as e:
            logging.error(f"Error inicializando base de datos: {e}")
            return False
    
    def create_tables(self):
        """Crear todas las tablas necesarias basadas en el esquema de Supabase"""
        cursor = self.connection.cursor()
        
        # 1. Tabla de usuarios (coincide con Supabase)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_usuario TEXT UNIQUE NOT NULL,
                contrasenia TEXT NOT NULL,
                nombre_completo TEXT NOT NULL,
                rol TEXT NOT NULL DEFAULT 'recepcionista',
                activo BOOLEAN DEFAULT 1,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ultimo_acceso TIMESTAMP,
                supabase_id INTEGER,
                needs_sync BOOLEAN DEFAULT 0
            )
        ''')
        
        # 2. Tabla de miembros
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS miembros (
                id_miembro INTEGER PRIMARY KEY AUTOINCREMENT,
                nombres TEXT NOT NULL,
                apellido_paterno TEXT NOT NULL,
                apellido_materno TEXT NOT NULL,
                telefono TEXT,
                email TEXT,
                contacto_emergencia TEXT,
                telefono_emergencia TEXT,
                codigo_qr TEXT NOT NULL UNIQUE,
                activo BOOLEAN DEFAULT 1,
                fecha_registro DATE DEFAULT CURRENT_DATE,
                fecha_nacimiento DATE,
                supabase_id INTEGER,
                needs_sync BOOLEAN DEFAULT 0
            )
        ''')
        
        # 3. Tabla de personal
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS personal (
                id_personal INTEGER PRIMARY KEY AUTOINCREMENT,
                nombres TEXT NOT NULL,
                apellido_paterno TEXT NOT NULL,
                apellido_materno TEXT NOT NULL,
                telefono TEXT,
                email TEXT,
                rol TEXT NOT NULL,
                numero_empleado TEXT UNIQUE,
                codigo_qr TEXT NOT NULL UNIQUE,
                activo BOOLEAN DEFAULT 1,
                fecha_contratacion DATE DEFAULT CURRENT_DATE,
                fecha_baja DATE,
                supabase_id INTEGER,
                needs_sync BOOLEAN DEFAULT 1
            )
        ''')
        
        # 4. Tabla de productos varios (POS)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ca_productos_varios (
                id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_interno TEXT NOT NULL UNIQUE,
                codigo_barras TEXT UNIQUE,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                imagen TEXT,
                precio_venta REAL NOT NULL CHECK (precio_venta > 0),
                categoria TEXT NOT NULL DEFAULT 'General',
                categoria_contable TEXT,
                requiere_refrigeracion BOOLEAN DEFAULT 0,
                peso_gr REAL,
                activo BOOLEAN DEFAULT 1,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                supabase_id INTEGER,
                needs_sync BOOLEAN DEFAULT 0
            )
        ''')
        
        # 5. Tabla de suplementos (POS)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ca_suplementos (
                id_suplemento INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_interno TEXT NOT NULL UNIQUE,
                codigo_barras TEXT UNIQUE,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                marca TEXT NOT NULL,
                tipo TEXT NOT NULL,
                sabor TEXT,
                presentacion TEXT,
                peso_neto_gr REAL,
                porciones_totales INTEGER,
                calorias_por_porcion REAL,
                proteina_por_porcion_gr REAL,
                precio_venta REAL NOT NULL CHECK (precio_venta > 0),
                activo BOOLEAN DEFAULT 1,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_vencimiento DATE,
                supabase_id INTEGER,
                needs_sync BOOLEAN DEFAULT 0
            )
        ''')
        
        # 5. Tabla de productos digitales
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ca_productos_digitales (
                id_producto_digital INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_interno TEXT NOT NULL UNIQUE,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                tipo TEXT NOT NULL,
                precio_venta REAL NOT NULL CHECK (precio_venta >= 0),
                duracion_dias INTEGER CHECK (duracion_dias IS NULL OR duracion_dias > 0),
                aplica_domingo BOOLEAN DEFAULT 0,
                aplica_festivo BOOLEAN DEFAULT 0,
                es_unico BOOLEAN DEFAULT 0,
                requiere_asignacion BOOLEAN DEFAULT 0,
                activo BOOLEAN DEFAULT 1,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                supabase_id INTEGER,
                needs_sync BOOLEAN DEFAULT 0
            )
        ''')
        
        # 6. Tabla de inventario
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventario (
                id_inventario INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_interno TEXT NOT NULL UNIQUE,
                tipo_producto TEXT NOT NULL,
                stock_actual INTEGER NOT NULL DEFAULT 0 CHECK (stock_actual >= 0),
                stock_minimo INTEGER NOT NULL DEFAULT 5 CHECK (stock_minimo >= 0),
                stock_maximo INTEGER CHECK (stock_maximo IS NULL OR stock_maximo >= stock_minimo),
                ubicacion TEXT NOT NULL DEFAULT 'Recepción',
                seccion TEXT,
                fecha_ultimo_conteo DATE,
                fecha_ultima_entrada TIMESTAMP,
                fecha_ultima_salida TIMESTAMP,
                requiere_conteo BOOLEAN DEFAULT 0,
                activo BOOLEAN DEFAULT 1,
                supabase_id INTEGER,
                needs_sync BOOLEAN DEFAULT 0
            )
        ''')
        
        # 7. Tabla de ventas (POS)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventas (
                id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER NOT NULL,
                id_miembro INTEGER,
                numero_ticket TEXT UNIQUE,
                fecha TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                subtotal REAL NOT NULL CHECK (subtotal >= 0),
                descuento REAL DEFAULT 0 CHECK (descuento >= 0),
                impuestos REAL DEFAULT 0 CHECK (impuestos >= 0),
                total REAL NOT NULL CHECK (total >= 0),
                metodo_pago TEXT NOT NULL,
                referencia_pago TEXT,
                tipo_venta TEXT NOT NULL,
                estado TEXT NOT NULL DEFAULT 'completada',
                notas TEXT,
                supabase_id INTEGER,
                needs_sync BOOLEAN DEFAULT 1,
                FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario),
                FOREIGN KEY (id_miembro) REFERENCES miembros (id_miembro)
            )
        ''')
        
        # 8. Tabla de detalles de venta (POS)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detalles_venta (
                id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
                id_venta INTEGER NOT NULL,
                codigo_interno TEXT NOT NULL,
                tipo_producto TEXT NOT NULL,
                cantidad INTEGER NOT NULL CHECK (cantidad > 0),
                precio_unitario REAL NOT NULL CHECK (precio_unitario >= 0),
                subtotal_linea REAL NOT NULL CHECK (subtotal_linea >= 0),
                descuento_linea REAL DEFAULT 0 CHECK (descuento_linea >= 0),
                nombre_producto TEXT NOT NULL,
                descripcion_producto TEXT,
                supabase_id INTEGER,
                needs_sync BOOLEAN DEFAULT 1,
                FOREIGN KEY (id_venta) REFERENCES ventas (id_venta) ON DELETE CASCADE
            )
        ''')
        
        # 9. Tabla de movimientos de inventario
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movimientos_inventario (
                id_movimiento INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_interno TEXT NOT NULL,
                tipo_producto TEXT NOT NULL,
                tipo_movimiento TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                stock_anterior INTEGER NOT NULL CHECK (stock_anterior >= 0),
                stock_nuevo INTEGER NOT NULL CHECK (stock_nuevo >= 0),
                motivo TEXT,
                numero_factura TEXT,
                costo_unitario REAL,
                id_usuario INTEGER NOT NULL,
                id_venta INTEGER,
                fecha TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                supabase_id INTEGER,
                needs_sync BOOLEAN DEFAULT 1,
                FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario),
                FOREIGN KEY (id_venta) REFERENCES ventas (id_venta)
            )
        ''')
        
        # 10. Tabla de lockers
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lockers (
                id_locker INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT NOT NULL UNIQUE,
                ubicacion TEXT NOT NULL DEFAULT 'Zona Lockers',
                tipo TEXT NOT NULL DEFAULT 'estándar',
                requiere_llave BOOLEAN NOT NULL DEFAULT 1,
                activo BOOLEAN NOT NULL DEFAULT 1,
                supabase_id INTEGER,
                needs_sync BOOLEAN DEFAULT 0
            )
        ''')
        
        # 11. Tabla de costos de productos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS costos_productos (
                id_costo INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_interno TEXT NOT NULL UNIQUE,
                tipo_producto TEXT NOT NULL,
                precio_compra REAL NOT NULL CHECK (precio_compra >= 0),
                precio_compra_anterior REAL,
                moneda TEXT DEFAULT 'MXN',
                proveedor TEXT,
                codigo_proveedor TEXT,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ultima_compra DATE,
                proxima_compra_estimada DATE,
                categoria_contable TEXT,
                cuenta_contable TEXT,
                activo BOOLEAN NOT NULL DEFAULT 1,
                supabase_id INTEGER,
                needs_sync BOOLEAN DEFAULT 0
            )
        ''')
        
        # 12. Tabla de turnos de caja
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS turnos_caja (
                id_turno INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER NOT NULL,
                fecha_apertura TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                monto_inicial REAL NOT NULL DEFAULT 0 CHECK (monto_inicial >= 0),
                notas_apertura TEXT,
                fecha_cierre TIMESTAMP,
                total_ventas_efectivo REAL NOT NULL DEFAULT 0 CHECK (total_ventas_efectivo >= 0),
                monto_esperado REAL NOT NULL CHECK (monto_esperado >= 0),
                monto_real_cierre REAL CHECK (monto_real_cierre >= 0),
                diferencia REAL,
                cerrado BOOLEAN NOT NULL DEFAULT 0,
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                supabase_id INTEGER,
                needs_sync BOOLEAN DEFAULT 1,
                FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario)
            )
        ''')
        
        # 13. Tabla de registro de entradas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registro_entradas (
                id_entrada INTEGER PRIMARY KEY AUTOINCREMENT,
                id_miembro INTEGER,
                id_personal INTEGER,
                nombre_visitante TEXT,
                tipo_acceso TEXT NOT NULL,
                fecha_entrada TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                fecha_salida TIMESTAMP,
                id_venta_acceso INTEGER,
                area_accedida TEXT DEFAULT 'General',
                dispositivo_registro TEXT,
                notas TEXT,
                autorizado_por TEXT,
                supabase_id INTEGER,
                needs_sync BOOLEAN DEFAULT 1,
                FOREIGN KEY (id_miembro) REFERENCES miembros (id_miembro),
                FOREIGN KEY (id_venta_acceso) REFERENCES ventas (id_venta)
            )
        ''')
        
        # 14. Tabla de sincronización
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT NOT NULL,
                action TEXT NOT NULL,
                local_id INTEGER,
                supabase_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                error_message TEXT,
                retry_count INTEGER DEFAULT 0
            )
        ''')
        
        self.connection.commit()
        logging.info("Tablas creadas correctamente con esquema de Supabase")
    
    def insert_initial_data(self):
        """Insertar datos iniciales"""
        cursor = self.connection.cursor()
        
        # Verificar si ya existe un usuario admin
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE nombre_usuario = 'admin'")
        if cursor.fetchone()[0] == 0:
            # Crear usuario administrador por defecto
            admin_password = self.hash_password("admin123")
            cursor.execute('''
                INSERT INTO usuarios (nombre_usuario, contrasenia, nombre_completo, rol)
                VALUES (?, ?, ?, ?)
            ''', ('admin', admin_password, 'Administrador HTF', 'administrador'))
            
            logging.info("Usuario administrador creado")
        
        # Insertar algunos productos de prueba
        cursor.execute("SELECT COUNT(*) FROM ca_productos_varios")
        if cursor.fetchone()[0] == 0:
            productos_prueba = [
                ('PRD001', None, 'Agua 600ml', 'Agua purificada', 15.00, 'Bebidas'),
                ('PRD002', None, 'Gatorade 500ml', 'Bebida isotónica', 25.00, 'Bebidas'),
                ('PRD003', None, 'Toalla Deportiva', 'Toalla de microfibra', 150.00, 'Accesorios'),
                ('PRD004', None, 'Barra Proteína', 'Barra de proteína sabor chocolate', 45.00, 'Snacks')
            ]
            
            cursor.executemany('''
                INSERT INTO ca_productos_varios 
                (codigo_interno, codigo_barras, nombre, descripcion, precio_venta, categoria)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', productos_prueba)
            
            logging.info("Productos de prueba insertados")
        
        # Insertar algunos suplementos de prueba
        cursor.execute("SELECT COUNT(*) FROM ca_suplementos")
        if cursor.fetchone()[0] == 0:
            suplementos_prueba = [
                ('SUP001', None, 'Whey Protein Gold', 'Proteína de suero premium', 'ON', 'proteina', 
                 'Chocolate', '2.27kg', 2270, 74, 130, 24, 1200.00),
                ('SUP002', None, 'Creatina Monohidrato', 'Creatina pura', 'Universal', 'creatina', 
                 None, '300g', 300, 60, 0, 0, 350.00),
                ('SUP003', None, 'BCAA 2:1:1', 'Aminoácidos ramificados', 'Xtend', 'aminoacidos', 
                 'Sandía', '400g', 400, 30, 0, 0, 650.00)
            ]
            
            cursor.executemany('''
                INSERT INTO ca_suplementos 
                (codigo_interno, codigo_barras, nombre, descripcion, marca, tipo, sabor, 
                 presentacion, peso_neto_gr, porciones_totales, calorias_por_porcion, 
                 proteina_por_porcion_gr, precio_venta)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', suplementos_prueba)
            
            logging.info("Suplementos de prueba insertados")
        
        # Insertar productos digitales básicos
        cursor.execute("SELECT COUNT(*) FROM ca_productos_digitales")
        if cursor.fetchone()[0] == 0:
            productos_digitales = [
                ('MEM001', 'Membresía Mensual', 'Acceso completo por 30 días', 'membresia_gym', 500.00, 30, 1, 1),
                ('MEM002', 'Membresía Quincenal', 'Acceso completo por 15 días', 'membresia_gym', 300.00, 15, 1, 1),
                ('REC001', 'Recargo Día Extra', 'Día adicional de gimnasio', 'recargo_dia', 50.00, 1, 0, 0),
                ('LOC001', 'Locker Mensual', 'Renta de locker por 30 días', 'locker_mensual', 100.00, 30, 1, 1)
            ]
            
            cursor.executemany('''
                INSERT INTO ca_productos_digitales 
                (codigo_interno, nombre, descripcion, tipo, precio_venta, duracion_dias, 
                 aplica_domingo, aplica_festivo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', productos_digitales)
            
            logging.info("Productos digitales básicos insertados")
        
        # Sincronizar inventario inicial
        self.sync_initial_inventory()
        
        self.connection.commit()
    
    def hash_password(self, password):
        """Crear hash de contraseña"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def sync_initial_inventory(self):
        """Sincronizar inventario inicial con productos"""
        cursor = self.connection.cursor()
        
        # Sincronizar productos varios con inventario
        cursor.execute('''
            INSERT OR IGNORE INTO inventario (codigo_interno, tipo_producto, stock_actual, stock_minimo)
            SELECT codigo_interno, 'varios', 0, 5
            FROM ca_productos_varios 
            WHERE activo = 1
        ''')
        
        # Sincronizar suplementos con inventario
        cursor.execute('''
            INSERT OR IGNORE INTO inventario (codigo_interno, tipo_producto, stock_actual, stock_minimo)
            SELECT codigo_interno, 'suplemento', 0, 2
            FROM ca_suplementos 
            WHERE activo = 1
        ''')
        
        logging.info("Inventario inicial sincronizado")
    
    def authenticate_user(self, username, password):
        """Autenticar usuario con nueva estructura"""
        try:
            cursor = self.connection.cursor()
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                SELECT id_usuario, nombre_usuario, nombre_completo, rol, activo
                FROM usuarios 
                WHERE nombre_usuario = ? AND contrasenia = ? AND activo = 1
            ''', (username, password_hash))
            
            user = cursor.fetchone()
            
            if user:
                # Actualizar último acceso
                cursor.execute('''
                    UPDATE usuarios SET ultimo_acceso = CURRENT_TIMESTAMP
                    WHERE id_usuario = ?
                ''', (user['id_usuario'],))
                self.connection.commit()
                
                return {
                    'id': user['id_usuario'],
                    'username': user['nombre_usuario'],
                    'nombre_completo': user['nombre_completo'],
                    'rol': user['rol']
                }
            
            return None
            
        except Exception as e:
            logging.error(f"Error autenticando usuario: {e}")
            return None
    
    def get_all_products(self):
        """Obtener todos los productos activos con stock"""
        try:
            cursor = self.connection.cursor()
            
            # Obtener productos varios con inventario
            cursor.execute('''
                SELECT 
                    p.id_producto,
                    p.codigo_interno,
                    p.codigo_barras,
                    p.nombre,
                    p.descripcion,
                    p.precio_venta,
                    p.categoria,
                    COALESCE(i.stock_actual, 0) as stock_actual,
                    p.activo
                FROM ca_productos_varios p
                LEFT JOIN inventario i ON p.codigo_interno = i.codigo_interno
                WHERE p.activo = 1
                ORDER BY p.nombre
            ''')
            
            results = cursor.fetchall()
            return [dict(row) for row in results]
        
        except Exception as e:
            logging.error(f"Error obteniendo productos: {e}")
            return []
    
    def get_product_by_barcode(self, barcode):
        """Buscar producto por código de barras en ambas tablas"""
        try:
            cursor = self.connection.cursor()
            
            # Buscar en productos varios
            cursor.execute('''
                SELECT 'varios' as tipo, codigo_interno, codigo_barras, nombre, descripcion, precio_venta
                FROM ca_productos_varios 
                WHERE codigo_barras = ? AND activo = 1
            ''', (barcode,))
            
            result = cursor.fetchone()
            if result:
                return result
            
            # Buscar en suplementos
            cursor.execute('''
                SELECT 'suplemento' as tipo, codigo_interno, codigo_barras, nombre, descripcion, precio_venta
                FROM ca_suplementos 
                WHERE codigo_barras = ? AND activo = 1
            ''', (barcode,))
            
            return cursor.fetchone()
        
        except Exception as e:
            logging.error(f"Error buscando producto: {e}")
            return None
    
    def get_product_by_code(self, codigo_interno):
        """Buscar producto por código interno"""
        try:
            cursor = self.connection.cursor()
            
            # Buscar en productos varios
            cursor.execute('''
                SELECT 'varios' as tipo, codigo_interno, nombre, descripcion, precio_venta, categoria
                FROM ca_productos_varios 
                WHERE codigo_interno = ? AND activo = 1
            ''', (codigo_interno,))
            
            result = cursor.fetchone()
            if result:
                return result
            
            # Buscar en suplementos
            cursor.execute('''
                SELECT 'suplemento' as tipo, codigo_interno, nombre, descripcion, precio_venta, marca as categoria
                FROM ca_suplementos 
                WHERE codigo_interno = ? AND activo = 1
            ''', (codigo_interno,))
            
            return cursor.fetchone()
        
        except Exception as e:
            logging.error(f"Error buscando producto por código: {e}")
            return None
    
    def get_inventory_status(self, codigo_interno=None):
        """Obtener estado del inventario"""
        try:
            cursor = self.connection.cursor()
            
            if codigo_interno:
                cursor.execute('''
                    SELECT i.*, 
                           CASE 
                               WHEN i.tipo_producto = 'varios' THEN pv.nombre
                               WHEN i.tipo_producto = 'suplemento' THEN ps.nombre
                           END as nombre_producto
                    FROM inventario i
                    LEFT JOIN ca_productos_varios pv ON i.codigo_interno = pv.codigo_interno
                    LEFT JOIN ca_suplementos ps ON i.codigo_interno = ps.codigo_interno
                    WHERE i.codigo_interno = ? AND i.activo = 1
                ''', (codigo_interno,))
                return cursor.fetchone()
            else:
                cursor.execute('''
                    SELECT i.*, 
                           CASE 
                               WHEN i.tipo_producto = 'varios' THEN pv.nombre
                               WHEN i.tipo_producto = 'suplemento' THEN ps.nombre
                           END as nombre_producto
                    FROM inventario i
                    LEFT JOIN ca_productos_varios pv ON i.codigo_interno = pv.codigo_interno
                    LEFT JOIN ca_suplementos ps ON i.codigo_interno = ps.codigo_interno
                    WHERE i.activo = 1
                    ORDER BY i.tipo_producto, nombre_producto
                ''')
                return cursor.fetchall()
        
        except Exception as e:
            logging.error(f"Error obteniendo inventario: {e}")
            return None if codigo_interno else []
    
    def test_supabase_sync(self):
        """Método para probar sincronización con Supabase"""
        try:
            cursor = self.connection.cursor()
            
            # Obtener usuario admin para prueba
            cursor.execute('''
                SELECT id_usuario, nombre_usuario, nombre_completo, rol, needs_sync
                FROM usuarios 
                WHERE nombre_usuario = 'admin'
            ''')
            
            admin_user = cursor.fetchone()
            if admin_user:
                logging.info(f"Usuario admin encontrado: {dict(admin_user)}")
                return admin_user
            else:
                logging.error("Usuario admin no encontrado")
                return None
                
        except Exception as e:
            logging.error(f"Error en test de Supabase: {e}")
            return None
    
    def close_connection(self):
        """Cerrar conexión a la base de datos"""
        if self.connection:
            self.connection.close()
            logging.info("Conexión a base de datos cerrada")
    
    def __del__(self):
        """Destructor para cerrar conexión"""
        self.close_connection()
    def get_total_members(self):
        '''Obtener total de miembros activos'''
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT COUNT(*) as total
                FROM miembros
                WHERE activo = 1
            ''')
            result = cursor.fetchone()
            return result['total'] if result else 0
        except Exception as e:
            logging.error(f'Error obteniendo total de miembros: {e}')
            return 0
    
    def get_active_members_today(self):
        '''Obtener miembros que han registrado entrada hoy'''
        try:
            cursor = self.connection.cursor()
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT COUNT(DISTINCT id_miembro) as total
                FROM registro_entradas
                WHERE DATE(fecha_entrada) = ?
            ''', (today,))
            result = cursor.fetchone()
            return result['total'] if result else 0
        except Exception as e:
            logging.error(f'Error obteniendo miembros activos hoy: {e}')
            return 0
    
    # ========== MÉTODOS DE VENTAS ==========
    
    def search_products(self, search_text):
        """Buscar productos por código o nombre"""
        try:
            cursor = self.connection.cursor()
            search_pattern = f"%{search_text}%"
            
            cursor.execute('''
                SELECT 
                    p.id_producto,
                    p.codigo_interno,
                    p.codigo_barras,
                    p.nombre,
                    p.descripcion,
                    p.precio_venta,
                    p.categoria,
                    COALESCE(i.stock_actual, 0) as stock_actual,
                    p.activo
                FROM ca_productos_varios p
                LEFT JOIN inventario i ON p.codigo_interno = i.codigo_interno
                WHERE p.activo = 1 
                AND (
                    p.nombre LIKE ? OR 
                    p.codigo_barras LIKE ? OR
                    p.codigo_interno LIKE ? OR
                    CAST(p.id_producto AS TEXT) LIKE ?
                )
                ORDER BY p.nombre
            ''', (search_pattern, search_pattern, search_pattern, search_pattern))
            
            results = cursor.fetchall()
            return [dict(row) for row in results]
            
        except Exception as e:
            logging.error(f"Error buscando productos: {e}")
            return []
    
    def create_sale(self, venta_data):
        """Crear nueva venta"""
        try:
            cursor = self.connection.cursor()
            
            # Iniciar transacción
            cursor.execute('BEGIN TRANSACTION')
            
            # Insertar venta
            cursor.execute('''
                INSERT INTO ventas (
                    fecha,
                    total,
                    id_usuario
                ) VALUES (?, ?, ?)
            ''', (
                venta_data['fecha_venta'],
                venta_data['total'],
                venta_data['id_usuario']
            ))
            
            venta_id = cursor.lastrowid
            
            # Insertar items de venta y actualizar stock
            for item in venta_data['productos']:
                # Obtener codigo_interno del producto
                cursor.execute('''
                    SELECT codigo_interno, nombre, descripcion 
                    FROM ca_productos_varios 
                    WHERE id_producto = ?
                ''', (item['id_producto'],))
                
                producto_info = cursor.fetchone()
                if not producto_info:
                    raise Exception(f"Producto con ID {item['id_producto']} no encontrado")
                
                # Insertar detalle de venta
                cursor.execute('''
                    INSERT INTO detalles_venta (
                        id_venta,
                        codigo_interno,
                        tipo_producto,
                        cantidad,
                        precio_unitario,
                        subtotal_linea,
                        nombre_producto,
                        descripcion_producto
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    venta_id,
                    producto_info['codigo_interno'],
                    'varios',
                    item['cantidad'],
                    item['precio'],
                    item['subtotal'],
                    producto_info['nombre'],
                    producto_info['descripcion']
                ))
                
                # Actualizar stock en inventario
                cursor.execute('''
                    UPDATE inventario 
                    SET stock_actual = stock_actual - ?,
                        fecha_ultima_salida = CURRENT_TIMESTAMP
                    WHERE codigo_interno = ?
                ''', (item['cantidad'], producto_info['codigo_interno']))
            
            # Confirmar transacción
            cursor.execute('COMMIT')
            
            logging.info(f"Venta creada exitosamente: ID {venta_id}")
            return venta_id
            
        except Exception as e:
            # Rollback en caso de error
            cursor.execute('ROLLBACK')
            logging.error(f"Error creando venta: {e}")
            raise e
    
    def get_sales_by_date(self, fecha):
        """Obtener ventas por fecha específica"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute('''
                SELECT 
                    v.id_venta,
                    v.fecha as fecha_venta,
                    v.total,
                    u.nombre_completo as usuario
                FROM ventas v
                LEFT JOIN usuarios u ON v.id_usuario = u.id_usuario
                WHERE DATE(v.fecha) = ?
                ORDER BY v.fecha DESC
            ''', (fecha.strftime('%Y-%m-%d'),))
            
            results = cursor.fetchall()
            return [dict(row) for row in results]
            
        except Exception as e:
            logging.error(f"Error obteniendo ventas por fecha: {e}")
            return []
    
    def get_sales_by_date_range(self, fecha_desde, fecha_hasta):
        """Obtener ventas por rango de fechas"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute('''
                SELECT 
                    v.id_venta,
                    v.fecha as fecha_venta,
                    v.total,
                    u.nombre_completo as usuario
                FROM ventas v
                LEFT JOIN usuarios u ON v.id_usuario = u.id_usuario
                WHERE DATE(v.fecha) BETWEEN ? AND ?
                ORDER BY v.fecha DESC
            ''', (fecha_desde.strftime('%Y-%m-%d'), fecha_hasta.strftime('%Y-%m-%d')))
            
            results = cursor.fetchall()
            return [dict(row) for row in results]
            
        except Exception as e:
            logging.error(f"Error obteniendo ventas por rango: {e}")
            return []
    
    def get_sale_details(self, venta_id):
        """Obtener detalles de una venta específica"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute('''
                SELECT 
                    dv.id_detalle,
                    dv.cantidad,
                    dv.precio_unitario,
                    dv.subtotal_linea as subtotal,
                    dv.nombre_producto as producto,
                    dv.descripcion_producto,
                    dv.codigo_interno
                FROM detalles_venta dv
                WHERE dv.id_venta = ?
                ORDER BY dv.nombre_producto
            ''', (venta_id,))
            
            results = cursor.fetchall()
            return [dict(row) for row in results]
            
        except Exception as e:
            logging.error(f"Error obteniendo detalles de venta: {e}")
            return []
    
    def get_sale_by_id(self, venta_id):
        """Obtener información de una venta por ID"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute('''
                SELECT 
                    v.id_venta,
                    v.fecha as fecha_venta,
                    v.total,
                    u.nombre_completo as usuario,
                    v.id_usuario
                FROM ventas v
                LEFT JOIN usuarios u ON v.id_usuario = u.id_usuario
                WHERE v.id_venta = ?
            ''', (venta_id,))
            
            result = cursor.fetchone()
            return dict(result) if result else None
            
        except Exception as e:
            logging.error(f"Error obteniendo venta por ID: {e}")
            return None
    
    def get_sale_items(self, venta_id):
        """Obtener items/productos de una venta (alias de get_sale_details)"""
        try:
            items = self.get_sale_details(venta_id)
            # Renombrar campo 'producto' a 'nombre' para consistencia
            for item in items:
                item['nombre'] = item.get('producto', '')
            return items
        except Exception as e:
            logging.error(f"Error obteniendo items de venta: {e}")
            return []
