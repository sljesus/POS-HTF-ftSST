"""
Gestor de Base de Datos PostgreSQL para Sistema de Gimnasio
Compatible con el esquema HTF_sql.txt
ACTUALIZADO: Usa bcrypt para autenticación y manejo correcto de transacciones
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import bcrypt
from datetime import datetime
from typing import Dict, List, Optional, Any

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class PostgresManager:
    """Gestor de conexión y operaciones con PostgreSQL"""
    
    def __init__(self, db_config: Dict[str, str]):
        """
        Inicializar conexión a PostgreSQL
        
        Args:
            db_config: Diccionario con la configuración de conexión
                {
                    'host': 'localhost',
                    'port': '5432',
                    'database': 'nombre_db',
                    'user': 'usuario',
                    'password': 'contraseña'
                }
        """
        self.db_config = db_config
        self.connection = None
        self.connect()
    
    def connect(self):
        """Establecer conexión con PostgreSQL"""
        try:
            # Cerrar conexión existente si hay una
            if self.connection and not self.connection.closed:
                self.connection.close()
                
            self.connection = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config.get('port', '5432'),
                database=self.db_config['database'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                cursor_factory=RealDictCursor
            )
            self.connection.autocommit = False
            logging.info("Conexión exitosa a PostgreSQL")
        except Exception as e:
            logging.error(f"Error conectando a PostgreSQL: {e}")
            raise
    
    def close(self):
        """Cerrar conexión a la base de datos"""
        if self.connection and not self.connection.closed:
            self.connection.close()
            logging.info("Conexión a PostgreSQL cerrada")
    
    def close_connection(self):
        """Alias para compatibilidad"""
        self.close()
    
    def __del__(self):
        """Destructor para cerrar conexión"""
        self.close()
    
    def initialize_database(self):
        """Inicializar la base de datos si es necesario."""
        try:
            with self.connection.cursor() as cursor:
                # Verificar que las tablas existen
                cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'usuarios';
                """)
                
                if cursor.fetchone():
                    logging.info("Base de datos inicializada correctamente.")
                    return True
                else:
                    logging.warning("Tabla 'usuarios' no encontrada. Ejecuta el script SQL primero.")
                    return False
        except Exception as e:
            logging.error(f"Error al verificar la base de datos: {e}")
            return False
    
    # ========== AUTENTICACIÓN ==========
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """
        Autenticar un usuario por nombre de usuario y contraseña.
        
        Args:
            username: Nombre de usuario
            password: Contraseña en texto plano
            
        Returns:
            dict con información del usuario si la autenticación es exitosa, None si falla
        """
        try:
            # Verificar que la conexión esté activa
            if not self.connection or self.connection.closed:
                self.connect()
                
            with self.connection.cursor() as cursor:
                # Consultar usuario por nombre de usuario
                cursor.execute("""
                    SELECT id_usuario, nombre_usuario, contrasenia, nombre_completo, rol, activo 
                    FROM usuarios 
                    WHERE nombre_usuario = %s AND activo = TRUE;
                """, (username,))
                
                user = cursor.fetchone()
                
                if user:
                    stored_password = user['contrasenia']
                    
                    # Verificar la contraseña usando bcrypt
                    if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                        logging.info(f"Autenticación exitosa para usuario: {username}")
                        
                        # Actualizar último acceso
                        cursor.execute("""
                            UPDATE usuarios 
                            SET ultimo_acceso = CURRENT_TIMESTAMP
                            WHERE id_usuario = %s;
                        """, (user['id_usuario'],))
                        self.connection.commit()
                        
                        return {
                            "id_usuario": user['id_usuario'],
                            "username": user['nombre_usuario'],
                            "nombre_completo": user['nombre_completo'],
                            "rol": user['rol']  # Cambiado de "role" a "rol" para consistencia
                        }
                    else:
                        logging.warning(f"Contraseña incorrecta para usuario: {username}")
                else:
                    logging.warning(f"Usuario no encontrado o inactivo: {username}")
                
                return None
                
        except Exception as e:
            logging.error(f"Error durante la autenticación: {e}")
            return None
    
    def create_user(self, username: str, password: str, nombre_completo: str, rol: str = "recepcionista") -> Optional[int]:
        """
        Crear un nuevo usuario en la base de datos.
        
        Args:
            username: Nombre de usuario (mínimo 3 caracteres)
            password: Contraseña en texto plano
            nombre_completo: Nombre completo del usuario
            rol: Rol del usuario (administrador, recepcionista, sistemas)
            
        Returns:
            ID del usuario creado, o None si hay error
        """
        try:
            # Verificar que la conexión esté activa
            if not self.connection or self.connection.closed:
                self.connect()
                
            # Validar longitud del nombre de usuario
            if len(username) < 3:
                logging.error("El nombre de usuario debe tener al menos 3 caracteres")
                return None
            
            # Hashear la contraseña
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
            hashed_password_str = hashed_password.decode('utf-8')
            
            with self.connection.cursor() as cursor:
                # Verificar si el usuario ya existe
                cursor.execute("""
                    SELECT id_usuario FROM usuarios WHERE nombre_usuario = %s;
                """, (username,))
                
                existing_user = cursor.fetchone()
                
                if existing_user:
                    logging.warning(f"El usuario '{username}' ya existe")
                    return None
                
                # Insertar nuevo usuario
                cursor.execute("""
                    INSERT INTO usuarios (nombre_usuario, contrasenia, nombre_completo, rol, activo)
                    VALUES (%s, %s, %s, %s::tipo_rol_usuario, TRUE)
                    RETURNING id_usuario;
                """, (username, hashed_password_str, nombre_completo, rol))
                
                user_id = cursor.fetchone()['id_usuario']
                self.connection.commit()
                
                logging.info(f"Usuario '{username}' creado exitosamente con ID: {user_id}")
                return user_id
                
        except Exception as e:
            try:
                self.connection.rollback()
            except Exception as rollback_error:
                logging.error(f"Error en rollback: {rollback_error}")
                
            logging.error(f"Error al crear usuario: {e}")
            return None
    
    def update_user_password(self, username: str, new_password: str) -> bool:
        """
        Actualizar la contraseña de un usuario existente.
        
        Args:
            username: Nombre de usuario
            new_password: Nueva contraseña en texto plano
            
        Returns:
            True si se actualizó exitosamente, False en caso contrario
        """
        try:
            # Verificar que la conexión esté activa
            if not self.connection or self.connection.closed:
                self.connect()
                
            # Hashear la nueva contraseña
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt)
            hashed_password_str = hashed_password.decode('utf-8')
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE usuarios 
                    SET contrasenia = %s
                    WHERE nombre_usuario = %s
                    RETURNING id_usuario;
                """, (hashed_password_str, username))
                
                result = cursor.fetchone()
                self.connection.commit()
                
                if result:
                    logging.info(f"Contraseña actualizada para usuario: {username}")
                    return True
                else:
                    logging.warning(f"Usuario no encontrado: {username}")
                    return False
                    
        except Exception as e:
            try:
                self.connection.rollback()
            except Exception as rollback_error:
                logging.error(f"Error en rollback: {rollback_error}")
                
            logging.error(f"Error al actualizar contraseña: {e}")
            return False
    
    # ========== PRODUCTOS ==========
    
    def get_all_products(self) -> List[Dict]:
        """Obtener todos los productos activos con stock"""
        try:
            # Verificar que la conexión esté activa
            if not self.connection or self.connection.closed:
                self.connect()
                
            with self.connection.cursor() as cursor:
                cursor.execute("""
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
                        AND i.tipo_producto = 'varios'
                    WHERE p.activo = TRUE
                    ORDER BY p.nombre
                """)
                
                return cursor.fetchall()
        
        except Exception as e:
            logging.error(f"Error obteniendo productos: {e}")
            return []
    
    def search_products(self, search_text: str) -> List[Dict]:
        """Buscar productos por código o nombre"""
        try:
            # Verificar que la conexión esté activa
            if not self.connection or self.connection.closed:
                self.connect()
                
            with self.connection.cursor() as cursor:
                search_pattern = f"%{search_text}%"
                
                cursor.execute("""
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
                        AND i.tipo_producto = 'varios'
                    WHERE p.activo = TRUE 
                    AND (
                        p.nombre ILIKE %s OR 
                        p.codigo_barras ILIKE %s OR
                        p.codigo_interno ILIKE %s
                    )
                    ORDER BY p.nombre
                """, (search_pattern, search_pattern, search_pattern))
                
                return cursor.fetchall()
            
        except Exception as e:
            logging.error(f"Error buscando productos: {e}")
            return []
    
    def get_product_by_barcode(self, barcode: str) -> Optional[Dict]:
        """Buscar producto por código de barras"""
        try:
            # Verificar que la conexión esté activa
            if not self.connection or self.connection.closed:
                self.connect()
                
            with self.connection.cursor() as cursor:
                # Buscar en productos varios
                cursor.execute("""
                    SELECT 
                        'varios' as tipo, 
                        p.codigo_interno, 
                        p.codigo_barras, 
                        p.nombre, 
                        p.descripcion, 
                        p.precio_venta, 
                        COALESCE(i.stock_actual, 0) as stock_actual
                    FROM ca_productos_varios p
                    LEFT JOIN inventario i ON p.codigo_interno = i.codigo_interno 
                        AND i.tipo_producto = 'varios'
                    WHERE p.codigo_barras = %s AND p.activo = TRUE
                """, (barcode,))
                
                result = cursor.fetchone()
                if result:
                    return result
                
                # Buscar en suplementos
                cursor.execute("""
                    SELECT 
                        'suplemento' as tipo, 
                        s.codigo_interno, 
                        s.codigo_barras, 
                        s.nombre, 
                        s.descripcion, 
                        s.precio_venta, 
                        COALESCE(i.stock_actual, 0) as stock_actual
                    FROM ca_suplementos s
                    LEFT JOIN inventario i ON s.codigo_interno = i.codigo_interno 
                        AND i.tipo_producto = 'suplemento'
                    WHERE s.codigo_barras = %s AND s.activo = TRUE
                """, (barcode,))
                
                return cursor.fetchone()
        
        except Exception as e:
            logging.error(f"Error buscando producto por código de barras: {e}")
            return None
    
    def get_product_by_code(self, code: str) -> Optional[Dict]:
        """Buscar producto por código interno"""
        try:
            # Verificar que la conexión esté activa
            if not self.connection or self.connection.closed:
                self.connect()
                
            with self.connection.cursor() as cursor:
                # Buscar en productos varios
                cursor.execute("""
                    SELECT 
                        'varios' as tipo, 
                        p.codigo_interno, 
                        p.codigo_barras, 
                        p.nombre, 
                        p.descripcion, 
                        p.precio_venta, 
                        COALESCE(i.stock_actual, 0) as stock_actual
                    FROM ca_productos_varios p
                    LEFT JOIN inventario i ON p.codigo_interno = i.codigo_interno 
                        AND i.tipo_producto = 'varios'
                    WHERE p.codigo_interno = %s AND p.activo = TRUE
                """, (code,))
                
                result = cursor.fetchone()
                if result:
                    return result
                
                # Buscar en suplementos
                cursor.execute("""
                    SELECT 
                        'suplemento' as tipo, 
                        s.codigo_interno, 
                        s.codigo_barras, 
                        s.nombre, 
                        s.descripcion, 
                        s.precio_venta, 
                        COALESCE(i.stock_actual, 0) as stock_actual
                    FROM ca_suplementos s
                    LEFT JOIN inventario i ON s.codigo_interno = i.codigo_interno 
                        AND i.tipo_producto = 'suplemento'
                    WHERE s.codigo_interno = %s AND s.activo = TRUE
                """, (code,))
                
                return cursor.fetchone()
        
        except Exception as e:
            logging.error(f"Error buscando producto por código interno: {e}")
            return None
    
    # ========== VENTAS ==========
    
    def create_sale(self, venta_data: Dict) -> int:
        """Crear nueva venta con transacción"""
        try:
            # Verificar que la conexión esté activa
            if not self.connection or self.connection.closed:
                self.connect()
                
            with self.connection.cursor() as cursor:
                # Calcular totales
                subtotal = venta_data['total']
                descuento = venta_data.get('descuento', 0)
                impuestos = venta_data.get('impuestos', 0)
                
                # Insertar venta
                cursor.execute("""
                    INSERT INTO ventas (
                        id_usuario, id_miembro, fecha, subtotal, descuento, 
                        impuestos, total, metodo_pago, tipo_venta, estado
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id_venta
                """, (
                    venta_data['id_usuario'],
                    venta_data.get('id_miembro'),
                    venta_data.get('fecha', datetime.now()),
                    subtotal,
                    descuento,
                    impuestos,
                    venta_data['total'],
                    venta_data.get('metodo_pago', 'efectivo'),
                    venta_data.get('tipo_venta', 'producto'),
                    'completada'
                ))
                
                venta_id = cursor.fetchone()['id_venta']
                
                # Insertar detalles y actualizar stock
                for item in venta_data['productos']:
                    # Obtener información del producto
                    cursor.execute("""
                        SELECT codigo_interno, nombre, descripcion 
                        FROM ca_productos_varios 
                        WHERE id_producto = %s
                    """, (item['id_producto'],))
                    
                    producto_info = cursor.fetchone()
                    if not producto_info:
                        raise Exception(f"Producto {item['id_producto']} no encontrado")
                    
                    codigo_interno = producto_info['codigo_interno']
                    
                    # Verificar stock
                    cursor.execute("""
                        SELECT stock_actual 
                        FROM inventario 
                        WHERE codigo_interno = %s AND tipo_producto = 'varios'
                    """, (codigo_interno,))
                    
                    stock_row = cursor.fetchone()
                    if not stock_row or stock_row['stock_actual'] < item['cantidad']:
                        raise Exception(f"Stock insuficiente para {producto_info['nombre']}")
                    
                    # Insertar detalle
                    cursor.execute("""
                        INSERT INTO detalles_venta (
                            id_venta, codigo_interno, tipo_producto, cantidad,
                            precio_unitario, subtotal_linea, nombre_producto, descripcion_producto
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        venta_id,
                        codigo_interno,
                        'varios',
                        item['cantidad'],
                        item['precio'],
                        item['subtotal'],
                        producto_info['nombre'],
                        producto_info['descripcion']
                    ))
                    
                    # Actualizar stock
                    stock_anterior = stock_row['stock_actual']
                    stock_nuevo = stock_anterior - item['cantidad']
                    
                    cursor.execute("""
                        UPDATE inventario 
                        SET stock_actual = %s,
                            fecha_ultima_salida = CURRENT_TIMESTAMP
                        WHERE codigo_interno = %s AND tipo_producto = 'varios'
                    """, (stock_nuevo, codigo_interno))
                    
                    # Registrar movimiento
                    cursor.execute("""
                        INSERT INTO movimientos_inventario (
                            codigo_interno, tipo_producto, tipo_movimiento,
                            cantidad, stock_anterior, stock_nuevo, id_usuario, id_venta
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        codigo_interno, 'varios', 'venta',
                        -item['cantidad'], stock_anterior, stock_nuevo,
                        venta_data['id_usuario'], venta_id
                    ))
                
                # Confirmar transacción
                self.connection.commit()
                logging.info(f"Venta creada: ID {venta_id}, Total: ${venta_data['total']:.2f}")
                return venta_id
            
        except Exception as e:
            try:
                self.connection.rollback()
            except Exception as rollback_error:
                logging.error(f"Error en rollback: {rollback_error}")
                
            logging.error(f"Error creando venta: {e}")
            raise
    
    # ========== MIEMBROS Y ACCESO ==========
    
    def obtener_miembro_por_codigo_qr(self, codigo_qr: str) -> Optional[Dict]:
        """Obtener miembro por código QR"""
        try:
            # Verificar que la conexión esté activa
            if not self.connection or self.connection.closed:
                self.connect()
                
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        id_miembro, nombres, apellido_paterno, apellido_materno,
                        telefono, email, codigo_qr, activo, fecha_registro, fecha_nacimiento
                    FROM miembros
                    WHERE codigo_qr = %s
                """, (codigo_qr,))
                
                return cursor.fetchone()
                
        except Exception as e:
            logging.error(f"Error obteniendo miembro: {e}")
            return None
    
    def get_total_members(self) -> int:
        """Obtener total de miembros activos"""
        try:
            # Verificar que la conexión esté activa
            if not self.connection or self.connection.closed:
                self.connect()
                
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as total FROM miembros WHERE activo = TRUE")
                return cursor.fetchone()['total']
        except Exception as e:
            logging.error(f"Error obteniendo total de miembros: {e}")
            return 0
    
    # ========== GESTIÓN DE PRODUCTOS E INVENTARIO ==========
    
    def producto_existe(self, codigo_interno: str) -> bool:
        """
        Verificar si un código interno ya existe en productos varios o suplementos.
        
        Args:
            codigo_interno: Código interno del producto a verificar
            
        Returns:
            True si el código ya existe, False si está disponible
        """
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                # Buscar en productos varios
                cursor.execute("""
                    SELECT 1 FROM ca_productos_varios 
                    WHERE codigo_interno = %s
                    LIMIT 1
                """, (codigo_interno,))
                
                if cursor.fetchone():
                    return True
                
                # Buscar en suplementos
                cursor.execute("""
                    SELECT 1 FROM ca_suplementos 
                    WHERE codigo_interno = %s
                    LIMIT 1
                """, (codigo_interno,))
                
                if cursor.fetchone():
                    return True
                
                return False
                
        except Exception as e:
            logging.error(f"Error verificando existencia de producto: {e}")
            return False
    
    def insertar_producto_varios(self, producto_data: Dict) -> bool:
        """
        Insertar un nuevo producto normal (varios) en la base de datos.
        
        Args:
            producto_data: Diccionario con los datos del producto
                {
                    'codigo_interno': str,
                    'codigo_barras': str (opcional),
                    'nombre': str,
                    'descripcion': str (opcional),
                    'precio_venta': Decimal,
                    'categoria': str,
                    'requiere_refrigeracion': bool,
                    'peso_gr': Decimal (opcional),
                    'activo': bool
                }
                
        Returns:
            True si se insertó correctamente, False en caso de error
        """
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ca_productos_varios (
                        codigo_interno, codigo_barras, nombre, descripcion,
                        precio_venta, categoria, requiere_refrigeracion,
                        peso_gr, activo
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    RETURNING id_producto
                """, (
                    producto_data['codigo_interno'],
                    producto_data.get('codigo_barras'),
                    producto_data['nombre'],
                    producto_data.get('descripcion'),
                    producto_data['precio_venta'],
                    producto_data.get('categoria', 'General'),
                    producto_data.get('requiere_refrigeracion', False),
                    producto_data.get('peso_gr'),
                    producto_data.get('activo', True)
                ))
                
                id_producto = cursor.fetchone()['id_producto']
                self.connection.commit()
                
                logging.info(f"Producto varios '{producto_data['nombre']}' insertado con ID: {id_producto}")
                return True
                
        except Exception as e:
            try:
                self.connection.rollback()
            except Exception:
                pass
            logging.error(f"Error insertando producto varios: {e}")
            return False
    
    def insertar_suplemento(self, suplemento_data: Dict) -> bool:
        """
        Insertar un nuevo suplemento en la base de datos.
        
        Args:
            suplemento_data: Diccionario con los datos del suplemento
                {
                    'codigo_interno': str,
                    'codigo_barras': str (opcional),
                    'nombre': str,
                    'descripcion': str (opcional),
                    'marca': str,
                    'tipo': str,
                    'peso_neto_gr': Decimal (opcional),
                    'precio_venta': Decimal,
                    'activo': bool,
                    'fecha_vencimiento': str (formato YYYY-MM-DD, opcional)
                }
                
        Returns:
            True si se insertó correctamente, False en caso de error
        """
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ca_suplementos (
                        codigo_interno, codigo_barras, nombre, descripcion,
                        marca, tipo, peso_neto_gr, precio_venta,
                        activo, fecha_vencimiento
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    RETURNING id_suplemento
                """, (
                    suplemento_data['codigo_interno'],
                    suplemento_data.get('codigo_barras'),
                    suplemento_data['nombre'],
                    suplemento_data.get('descripcion'),
                    suplemento_data['marca'],
                    suplemento_data['tipo'],
                    suplemento_data.get('peso_neto_gr'),
                    suplemento_data['precio_venta'],
                    suplemento_data.get('activo', True),
                    suplemento_data.get('fecha_vencimiento')
                ))
                
                id_suplemento = cursor.fetchone()['id_suplemento']
                self.connection.commit()
                
                logging.info(f"Suplemento '{suplemento_data['nombre']}' insertado con ID: {id_suplemento}")
                return True
                
        except Exception as e:
            try:
                self.connection.rollback()
            except Exception:
                pass
            logging.error(f"Error insertando suplemento: {e}")
            return False
    
    def crear_inventario(self, inventario_data: Dict) -> bool:
        """
        Crear un registro de inventario para un producto físico.
        
        Args:
            inventario_data: Diccionario con los datos del inventario
                {
                    'codigo_interno': str,
                    'tipo_producto': str ('varios' o 'suplemento'),
                    'stock_actual': int,
                    'stock_minimo': int,
                    'id_ubicacion': int,  # ID del catálogo ca_ubicaciones
                    'activo': bool
                }
                
        Returns:
            True si se creó correctamente, False en caso de error
        """
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO inventario (
                        codigo_interno, tipo_producto, stock_actual,
                        stock_minimo, id_ubicacion, activo
                    ) VALUES (
                        %s, %s::tipo_producto_fisico, %s, %s, %s, %s
                    )
                    RETURNING id_inventario
                """, (
                    inventario_data['codigo_interno'],
                    inventario_data['tipo_producto'],
                    inventario_data.get('stock_actual', 0),
                    inventario_data.get('stock_minimo', 5),
                    inventario_data.get('id_ubicacion', 1),  # Default a Zona Lockers (id=1)
                    inventario_data.get('activo', True)
                ))
                
                id_inventario = cursor.fetchone()['id_inventario']
                self.connection.commit()
                
                logging.info(f"Inventario creado para '{inventario_data['codigo_interno']}' con ID: {id_inventario}")
                return True
                
        except Exception as e:
            try:
                self.connection.rollback()
            except Exception:
                pass
            logging.error(f"Error creando inventario: {e}")
            return False


# Ejemplo de uso
if __name__ == "__main__":
    # Configuración de conexión
    config = {
        'host': 'localhost',
        'port': '5432',
        'database': 'HTF_DB',
        'user': 'postgres',
        'password': 'postgres'
    }
    
    try:
        # Crear instancia del gestor
        db = PostgresManager(config)
        
        # Ejemplo: Autenticar usuario
        user = db.authenticate_user('admin', 'admin123')
        if user:
            print(f"✓ Usuario autenticado: {user['nombre_completo']}")
            print(f"  Rol: {user['rol']}")
        else:
            print("✗ Autenticación fallida")
        
        # Cerrar conexión
        db.close()
        
    except Exception as e:
        print(f"Error: {e}")