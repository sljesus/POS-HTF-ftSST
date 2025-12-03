"""
Script para insertar un usuario administrador en la base de datos PostgreSQL local.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import bcrypt

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def hash_password(password: str) -> str:
    """Hashear una contraseña usando bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def insert_admin_user():
    """Insertar un usuario administrador en la base de datos local."""
    connection = None
    try:
        # Configuración de la conexión a PostgreSQL
        connection = psycopg2.connect(
            host="localhost",
            port=5432,
            database="HTF_DB",
            user="postgres",
            password="postgres"
        )
        
        cursor = connection.cursor()
        
        # Verificar si el usuario admin ya existe
        cursor.execute("""
            SELECT id_usuario FROM usuarios WHERE nombre_usuario = %s;
        """, ("admin",))
        
        existing_user = cursor.fetchone()
        
        if existing_user is None:
            # Hashear la contraseña
            password_hash = hash_password("admin123")
            
            # Insertar el usuario admin en la tabla usuarios (no miembros)
            cursor.execute("""
                INSERT INTO usuarios (
                    nombre_usuario, contrasenia, nombre_completo, rol, activo, fecha_creacion
                )
                VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP);
            """, (
                "admin",
                password_hash,
                "Administrador Sistema",
                "administrador",
                True
            ))
            
            connection.commit()
            logging.info("✅ Usuario admin insertado correctamente.")
            logging.info("   Usuario: admin")
            logging.info("   Contraseña: admin123 (hasheada)")
            logging.info("   Rol: administrador")
        else:
            logging.info("⚠️ El usuario admin ya existe en la base de datos.")
            logging.info(f"   ID: {existing_user[0]}")
            
    except psycopg2.Error as e:
        logging.error(f"❌ Error de base de datos: {e}")
        if connection:
            connection.rollback()
    except Exception as e:
        logging.error(f"❌ Error inesperado: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()
            logging.info("Conexión a PostgreSQL cerrada.")

if __name__ == "__main__":
    insert_admin_user()