"""
Monitor de Entradas - Detecta nuevos registros usando PostgreSQL LISTEN/NOTIFY
Emite señal cuando se detecta una nueva entrada en tiempo real
"""

from PySide6.QtCore import QObject, QTimer, Signal, QThread
import logging
from datetime import datetime
import json

try:
    import psycopg2
    import psycopg2.extensions
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    logging.warning("psycopg2 no está instalado. Monitor de entradas no funcionará.")


class PostgresListenerThread(QThread):
    """Hilo separado para escuchar notificaciones de PostgreSQL"""
    
    notificacion_recibida = Signal(str)  # Emite el payload JSON
    
    def __init__(self, host, port, database, user, password, channel):
        super().__init__()
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.channel = channel
        self.running = False
        self.conn = None
        
    def run(self):
        """Conectar y escuchar notificaciones"""
        try:
            # Conectar a PostgreSQL con codificación UTF-8
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                client_encoding='UTF8'
            )
            self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            
            cursor = self.conn.cursor()
            cursor.execute(f"LISTEN {self.channel};")
            
            logging.info(f"[OK] Escuchando canal PostgreSQL: {self.channel}")
            
            self.running = True
            
            # Loop de escucha
            while self.running:
                # Esperar notificaciones con timeout de 1 segundo
                if self.conn.poll() is None:
                    self.conn.poll()
                
                while self.conn.notifies:
                    notify = self.conn.notifies.pop(0)
                    try:
                        # Intentar decodificar el payload
                        payload = notify.payload
                        logging.info(f"[NOTIF] Notificacion recibida: {payload[:100]}...")
                        self.notificacion_recibida.emit(payload)
                    except Exception as decode_error:
                        logging.error(f"Error decodificando notificacion: {decode_error}")
                        # Intentar con latin1 como fallback
                        try:
                            if isinstance(notify.payload, bytes):
                                payload = notify.payload.decode('latin1')
                                logging.warning("Usando codificacion latin1 como fallback")
                                self.notificacion_recibida.emit(payload)
                        except:
                            logging.error("No se pudo decodificar la notificacion")
                
                # Pequeña pausa para no saturar CPU
                self.msleep(100)
                
        except Exception as e:
            logging.error(f"[ERROR] Error en listener PostgreSQL: {e}")
        finally:
            if self.conn:
                self.conn.close()
                logging.info("Conexion PostgreSQL cerrada")
    
    def stop(self):
        """Detener el listener"""
        self.running = False
        self.wait()


class MonitorEntradas(QObject):
    """
    Monitorea nuevas entradas usando PostgreSQL LISTEN/NOTIFY en tiempo real.
    Emite una señal cuando se detecta una nueva entrada.
    """
    
    nueva_entrada_detectada = Signal(dict)  # Emite los datos de la entrada y del miembro
    
    def __init__(self, postgres_manager, supabase_service=None, 
                 pg_host='localhost', pg_port=5432, pg_database='torniquete_db',
                 pg_user='postgres', pg_password='postgres', pg_channel='nueva_entrada_canal'):
        """
        Args:
            postgres_manager: Instancia de PostgresManager para manejar la base de datos
            supabase_service: Instancia de SupabaseService (para consultas adicionales)
            pg_host: Host del PostgreSQL del torniquete (default: localhost)
            pg_port: Puerto PostgreSQL (default: 5432)
            pg_database: Nombre de la base de datos (default: torniquete_db)
            pg_user: Usuario PostgreSQL (default: postgres)
            pg_password: Contraseña PostgreSQL (default: postgres)
            pg_channel: Canal LISTEN/NOTIFY (default: nueva_entrada_canal)
        """
        super().__init__()
        self.postgres_manager = postgres_manager
        self.supabase_service = supabase_service
        
        # Configuración PostgreSQL
        self.pg_host = pg_host
        self.pg_port = pg_port
        self.pg_database = pg_database
        self.pg_user = pg_user
        self.pg_password = pg_password
        self.pg_channel = pg_channel
        
        # Hilo de escucha
        self.listener_thread = None
        
        # Estado del monitor
        self.activo = False
        
        if not PSYCOPG2_AVAILABLE:
            logging.error("[ERROR] psycopg2 no disponible. Instalar con: pip install psycopg2-binary")
        
        logging.info(f"Monitor de entradas inicializado (PostgreSQL LISTEN/NOTIFY en {pg_host}:{pg_port})")
    
    def iniciar(self):
        """Iniciar el monitoreo en tiempo real"""
        if self.activo:
            logging.warning("Monitor ya está activo")
            return
        
        if not PSYCOPG2_AVAILABLE:
            logging.error("[ERROR] No se puede iniciar monitor: psycopg2 no disponible")
            return
        
        try:
            # Crear y configurar hilo de escucha
            self.listener_thread = PostgresListenerThread(
                host=self.pg_host,
                port=self.pg_port,
                database=self.pg_database,
                user=self.pg_user,
                password=self.pg_password,
                channel=self.pg_channel
            )
            
            # Conectar señal
            self.listener_thread.notificacion_recibida.connect(self.procesar_notificacion)
            
            # Iniciar hilo
            self.listener_thread.start()
            
            self.activo = True
            
            logging.info(f"[OK] Monitor de entradas iniciado (PostgreSQL LISTEN en {self.pg_host}:{self.pg_port})")
            
        except Exception as e:
            logging.error(f"[ERROR] Error iniciando monitor de entradas: {e}")
    
    def detener(self):
        """Detener el monitoreo"""
        if not self.activo:
            return
        
        if self.listener_thread:
            self.listener_thread.stop()
            self.listener_thread = None
        
        self.activo = False
        
        logging.info("Monitor de entradas detenido")
    
    def procesar_notificacion(self, payload_json):
        """Procesar notificación recibida de PostgreSQL"""
        try:
            # Parsear JSON
            datos = json.loads(payload_json)
            
            logging.info(f"[ENTRADA] Procesando entrada ID: {datos.get('id_entrada')}")
            
            # Si la notificación incluye todos los datos, emitir directamente
            if 'nombres' in datos and 'apellido_paterno' in datos:
                self.nueva_entrada_detectada.emit(datos)
            else:
                # Obtener datos adicionales desde postgres_manager si faltan
                entrada_id = datos.get('id_entrada')
                if entrada_id:
                    entrada_detalle = self.postgres_manager.get_entry_details(entrada_id)
                    self.nueva_entrada_detectada.emit(entrada_detalle)
        
        except Exception as e:
            logging.error(f"[ERROR] Error procesando notificación: {e}")
    
    def consultar_datos_completos(self, id_entrada, id_miembro):
        """Consultar datos completos desde Supabase cuando la notificación solo trae IDs"""
        try:
            if not self.supabase_service or not self.supabase_service.is_connected:
                logging.warning("No hay conexión a Supabase para consultar datos completos")
                return
            
            # Consultar entrada con datos del miembro
            response = self.supabase_service.client.table('registro_entradas')\
                .select('*, miembros(*)')\
                .eq('id_entrada', id_entrada)\
                .single()\
                .execute()
            
            if response.data:
                entrada = response.data
                miembro = entrada.get('miembros', {})
                
                # Convertir a estructura esperada
                entrada_data = {
                    'id_entrada': entrada.get('id_entrada'),
                    'id_miembro': entrada.get('id_miembro'),
                    'tipo_acceso': entrada.get('tipo_acceso'),
                    'fecha_entrada': entrada.get('fecha_entrada'),
                    'area_accedida': entrada.get('area_accedida'),
                    'dispositivo_registro': entrada.get('dispositivo_registro'),
                    'notas': entrada.get('notas'),
                    'nombres': miembro.get('nombres', ''),
                    'apellido_paterno': miembro.get('apellido_paterno', ''),
                    'apellido_materno': miembro.get('apellido_materno', ''),
                    'telefono': miembro.get('telefono', ''),
                    'email': miembro.get('email', ''),
                    'codigo_qr': miembro.get('codigo_qr', ''),
                    'activo': miembro.get('activo', True),
                    'fecha_registro': miembro.get('fecha_registro', ''),
                    'fecha_nacimiento': miembro.get('fecha_nacimiento', '')
                }
                
                self.nueva_entrada_detectada.emit(entrada_data)
            else:
                logging.warning(f"No se encontraron datos para entrada ID: {id_entrada}")
                
        except Exception as e:
            logging.error(f"Error consultando datos completos: {e}")
    
    def verificar_nuevas_entradas(self):
        """Verificar si hay nuevas entradas desde Supabase"""
        if not self.activo:
            return
        
        try:
            # Verificar conexión a Supabase
            if not self.supabase_service or not self.supabase_service.is_connected:
                logging.warning("Conexión a Supabase no disponible")
                return
            
            # Buscar entradas con ID mayor al último procesado desde Supabase
            response = self.supabase_service.client.table('registro_entradas')\
                .select('*, miembros(*)')\
                .gt('id_entrada', self.ultimo_id_procesado)\
                .eq('tipo_acceso', 'miembro')\
                .order('id_entrada', desc=False)\
                .execute()
            
            if response.data and len(response.data) > 0:
                logging.info(f"Detectadas {len(response.data)} nueva(s) entrada(s) desde Supabase")
                
                for entrada in response.data:
                    # Extraer datos del miembro
                    miembro = entrada.get('miembros', {})
                    
                    # Convertir a diccionario con estructura esperada
                    entrada_data = {
                        'id_entrada': entrada.get('id_entrada'),
                        'id_miembro': entrada.get('id_miembro'),
                        'tipo_acceso': entrada.get('tipo_acceso'),
                        'fecha_entrada': entrada.get('fecha_entrada'),
                        'area_accedida': entrada.get('area_accedida'),
                        'dispositivo_registro': entrada.get('dispositivo_registro'),
                        'notas': entrada.get('notas'),
                        'nombres': miembro.get('nombres', ''),
                        'apellido_paterno': miembro.get('apellido_paterno', ''),
                        'apellido_materno': miembro.get('apellido_materno', ''),
                        'telefono': miembro.get('telefono', ''),
                        'email': miembro.get('email', ''),
                        'codigo_qr': miembro.get('codigo_qr', ''),
                        'activo': miembro.get('activo', True),
                        'fecha_registro': miembro.get('fecha_registro', ''),
                        'fecha_nacimiento': miembro.get('fecha_nacimiento', '')
                    }
                    
                    # Actualizar último ID procesado
                    self.ultimo_id_procesado = entrada_data['id_entrada']
                    
                    # Emitir señal con los datos
                    logging.info(f"Emitiendo señal para entrada ID: {entrada_data['id_entrada']}, Miembro: {entrada_data['nombres']} {entrada_data['apellido_paterno']}")
                    self.nueva_entrada_detectada.emit(entrada_data)
                    
        except KeyboardInterrupt:
            # Manejar interrupción del usuario
            logging.info("Monitor de entradas interrumpido por el usuario")
            self.detener()
        except Exception as e:
            logging.error(f"Error verificando nuevas entradas desde Supabase: {e}")
            # No detener el monitor por un error puntual
        
        # === CÓDIGO SQLITE COMENTADO (solo para ventas) ===
        # try:
        #     # Verificar que la conexión esté activa
        #     if not self.db_manager.connection:
        #         logging.warning("Conexión a base de datos no disponible")
        #         return
        #     
        #     cursor = self.db_manager.connection.cursor()
        #     
        #     # Buscar entradas con ID mayor al último procesado
        #     cursor.execute("""
        #         SELECT 
        #             re.id_entrada,
        #             re.id_miembro,
        #             re.tipo_acceso,
        #             re.fecha_entrada,
        #             re.area_accedida,
        #             re.dispositivo_registro,
        #             re.notas,
        #             m.nombres,
        #             m.apellido_paterno,
        #             m.apellido_materno,
        #             m.telefono,
        #             m.email,
        #             m.codigo_qr,
        #             m.activo,
        #             m.fecha_registro,
        #             m.fecha_nacimiento
        #         FROM registro_entradas re
        #         INNER JOIN miembros m ON re.id_miembro = m.id_miembro
        #         WHERE re.id_entrada > ?
        #         AND re.tipo_acceso = 'miembro'
        #         ORDER BY re.id_entrada ASC
        #     """, (self.ultimo_id_procesado,))
        #     
        #     nuevas_entradas = cursor.fetchall()
        #     
        #     if nuevas_entradas:
        #         logging.info(f"Detectadas {len(nuevas_entradas)} nueva(s) entrada(s)")
        #         
        #         for entrada in nuevas_entradas:
        #             # Convertir a diccionario
        #             entrada_data = {
        #                 'id_entrada': entrada[0],
        #                 'id_miembro': entrada[1],
        #                 'tipo_acceso': entrada[2],
        #                 'fecha_entrada': entrada[3],
        #                 'area_accedida': entrada[4],
        #                 'dispositivo_registro': entrada[5],
        #                 'notas': entrada[6],
        #                 'nombres': entrada[7],
        #                 'apellido_paterno': entrada[8],
        #                 'apellido_materno': entrada[9],
        #                 'telefono': entrada[10],
        #                 'email': entrada[11],
        #                 'codigo_qr': entrada[12],
        #                 'activo': entrada[13],
        #                 'fecha_registro': entrada[14],
        #                 'fecha_nacimiento': entrada[15]
        #             }
        #             
        #             # Actualizar último ID procesado
        #             self.ultimo_id_procesado = entrada_data['id_entrada']
        #             
        #             # Emitir señal con los datos
        #             logging.info(f"Emitiendo señal para entrada ID: {entrada_data['id_entrada']}, Miembro: {entrada_data['nombres']} {entrada_data['apellido_paterno']}")
        #             self.nueva_entrada_detectada.emit(entrada_data)
        #             
        # except KeyboardInterrupt:
        #     # Manejar interrupción del usuario
        #     logging.info("Monitor de entradas interrumpido por el usuario")
        #     self.detener()
        # except Exception as e:
        #     logging.error(f"Error verificando nuevas entradas: {e}")
        #     # No detener el monitor por un error puntual
    
    def reiniciar(self):
        """Reiniciar el monitor"""
        was_active = self.activo
        
        if was_active:
            self.detener()
            # Pequeña pausa para asegurar cierre limpio
            QThread.msleep(500)
            self.iniciar()
        
        logging.info("Monitor de entradas reiniciado")
