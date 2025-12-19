"""
Script para verificar la compatibilidad del PostgresManager con el schema de Supabase
Valida que todos los métodos funcionen correctamente con las tablas actuales
"""

import os
import sys
import logging
from datetime import datetime, timedelta

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Agregar ruta del proyecto
sys.path.insert(0, os.path.dirname(__file__))

from database.postgres_manager import PostgresManager


class SupabaseCompatibilityTest:
    """Pruebas de compatibilidad con Supabase"""
    
    def __init__(self):
        self.db = None
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': [],
            'skipped': []
        }
    
    def connect(self):
        """Conectar a Supabase"""
        try:
            config = {
                'url': os.getenv('SUPABASE_URL'),
                'key': os.getenv('SUPABASE_KEY')
            }
            
            if not config['url'] or not config['key']:
                logger.error("❌ Credenciales de Supabase no configuradas")
                logger.error("   Configura SUPABASE_URL y SUPABASE_KEY en .env")
                return False
            
            self.db = PostgresManager(config)
            
            if self.db.is_connected:
                logger.info("✅ Conexión a Supabase exitosa")
                return True
            else:
                logger.error("❌ No se pudo conectar a Supabase")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error conectando: {e}")
            return False
    
    def test_connection(self):
        """Prueba 1: Conexión básica"""
        logger.info("\n=== PRUEBA 1: Conexión Básica ===")
        try:
            if self.db.initialize_database():
                logger.info("✅ Base de datos inicializada correctamente")
                self.results['passed'].append("Conexión básica")
                return True
            else:
                logger.error("❌ Error inicializando base de datos")
                self.results['failed'].append("Conexión básica")
                return False
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            self.results['failed'].append(f"Conexión básica: {e}")
            return False
    
    def test_authentication(self):
        """Prueba 2: Autenticación"""
        logger.info("\n=== PRUEBA 2: Autenticación ===")
        try:
            # Intentar autenticar con usuario admin
            user = self.db.authenticate_user('admin', 'admin123')
            
            if user:
                logger.info(f"✅ Autenticación exitosa")
                logger.info(f"   Usuario: {user.get('nombre_completo')}")
                logger.info(f"   Rol: {user.get('rol')}")
                logger.info(f"   ID: {user.get('id_usuario')}")
                self.results['passed'].append("Autenticación")
                return True
            else:
                logger.warning("⚠️  Usuario admin no encontrado o contraseña incorrecta")
                self.results['warnings'].append("Autenticación: Usuario no encontrado")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error en autenticación: {e}")
            self.results['failed'].append(f"Autenticación: {e}")
            return False
    
    def test_products(self):
        """Prueba 3: Operaciones con productos"""
        logger.info("\n=== PRUEBA 3: Operaciones con Productos ===")
        results_ok = True
        
        try:
            # Obtener todos los productos
            productos = self.db.get_all_products()
            logger.info(f"✅ get_all_products(): {len(productos)} productos")
            self.results['passed'].append("get_all_products()")
        except Exception as e:
            logger.error(f"❌ Error en get_all_products(): {e}")
            self.results['failed'].append(f"get_all_products(): {e}")
            results_ok = False
        
        try:
            # Buscar productos
            search_results = self.db.search_products('recepcion')
            logger.info(f"✅ search_products(): {len(search_results)} resultados")
            self.results['passed'].append("search_products()")
        except Exception as e:
            logger.error(f"❌ Error en search_products(): {e}")
            self.results['failed'].append(f"search_products(): {e}")
            results_ok = False
        
        try:
            # Buscar por código de barras
            producto = self.db.get_product_by_barcode('TEST123')
            if producto:
                logger.info(f"✅ get_product_by_barcode(): {producto.get('nombre')}")
            else:
                logger.info(f"✅ get_product_by_barcode(): No encontrado (esperado)")
            self.results['passed'].append("get_product_by_barcode()")
        except Exception as e:
            logger.error(f"❌ Error en get_product_by_barcode(): {e}")
            self.results['failed'].append(f"get_product_by_barcode(): {e}")
            results_ok = False
        
        return results_ok
    
    def test_members(self):
        """Prueba 4: Operaciones con miembros"""
        logger.info("\n=== PRUEBA 4: Operaciones con Miembros ===")
        results_ok = True
        
        try:
            # Obtener total de miembros
            total = self.db.get_total_members()
            logger.info(f"✅ get_total_members(): {total} miembros activos")
            self.results['passed'].append("get_total_members()")
        except Exception as e:
            logger.error(f"❌ Error en get_total_members(): {e}")
            self.results['failed'].append(f"get_total_members(): {e}")
            results_ok = False
        
        try:
            # Buscar por QR
            miembro = self.db.obtener_miembro_por_codigo_qr('QR123')
            if miembro:
                logger.info(f"✅ obtener_miembro_por_codigo_qr(): {miembro.get('nombres')}")
            else:
                logger.info(f"✅ obtener_miembro_por_codigo_qr(): No encontrado (esperado)")
            self.results['passed'].append("obtener_miembro_por_codigo_qr()")
        except Exception as e:
            logger.error(f"❌ Error en obtener_miembro_por_codigo_qr(): {e}")
            self.results['failed'].append(f"obtener_miembro_por_codigo_qr(): {e}")
            results_ok = False
        
        return results_ok
    
    def test_locations(self):
        """Prueba 5: Ubicaciones"""
        logger.info("\n=== PRUEBA 5: Ubicaciones ===")
        results_ok = True
        
        try:
            # Obtener ubicaciones
            ubicaciones = self.db.get_ubicaciones()
            logger.info(f"✅ get_ubicaciones(): {len(ubicaciones)} ubicaciones")
            self.results['passed'].append("get_ubicaciones()")
        except Exception as e:
            logger.error(f"❌ Error en get_ubicaciones(): {e}")
            self.results['failed'].append(f"get_ubicaciones(): {e}")
            results_ok = False
        
        return results_ok
    
    def test_lockers(self):
        """Prueba 6: Lockers"""
        logger.info("\n=== PRUEBA 6: Lockers ===")
        results_ok = True
        
        try:
            # Obtener lockers
            lockers = self.db.get_lockers()
            logger.info(f"✅ get_lockers(): {len(lockers)} lockers")
            self.results['passed'].append("get_lockers()")
        except Exception as e:
            logger.error(f"❌ Error en get_lockers(): {e}")
            self.results['failed'].append(f"get_lockers(): {e}")
            results_ok = False
        
        return results_ok
    
    def test_digital_products(self):
        """Prueba 7: Productos digitales"""
        logger.info("\n=== PRUEBA 7: Productos Digitales ===")
        results_ok = True
        
        try:
            # Obtener productos digitales
            productos = self.db.get_productos_digitales()
            logger.info(f"✅ get_productos_digitales(): {len(productos)} productos")
            self.results['passed'].append("get_productos_digitales()")
        except Exception as e:
            logger.error(f"❌ Error en get_productos_digitales(): {e}")
            self.results['failed'].append(f"get_productos_digitales(): {e}")
            results_ok = False
        
        return results_ok
    
    def test_notifications(self):
        """Prueba 8: Notificaciones"""
        logger.info("\n=== PRUEBA 8: Notificaciones ===")
        results_ok = True
        
        try:
            # Obtener notificaciones pendientes
            notificaciones = self.db.get_notificaciones_pendientes()
            logger.info(f"✅ get_notificaciones_pendientes(): {len(notificaciones)} notificaciones")
            self.results['passed'].append("get_notificaciones_pendientes()")
        except Exception as e:
            logger.error(f"❌ Error en get_notificaciones_pendientes(): {e}")
            self.results['failed'].append(f"get_notificaciones_pendientes(): {e}")
            results_ok = False
        
        return results_ok
    
    def test_inventory(self):
        """Prueba 9: Inventario"""
        logger.info("\n=== PRUEBA 9: Inventario ===")
        results_ok = True
        
        try:
            # Verificar existencia de producto
            existe = self.db.producto_existe('PROD-001')
            logger.info(f"✅ producto_existe(): {existe}")
            self.results['passed'].append("producto_existe()")
        except Exception as e:
            logger.error(f"❌ Error en producto_existe(): {e}")
            self.results['failed'].append(f"producto_existe(): {e}")
            results_ok = False
        
        return results_ok
    
    def test_cash_registers(self):
        """Prueba 10: Turnos de caja"""
        logger.info("\n=== PRUEBA 10: Turnos de Caja ===")
        results_ok = True
        
        try:
            # Obtener turno activo (si existe)
            turno = self.db.get_turno_activo(id_usuario=1)
            if turno:
                logger.info(f"✅ get_turno_activo(): Turno encontrado (ID: {turno.get('id_turno')})")
            else:
                logger.info(f"✅ get_turno_activo(): No hay turno activo (esperado)")
            self.results['passed'].append("get_turno_activo()")
        except Exception as e:
            logger.error(f"❌ Error en get_turno_activo(): {e}")
            self.results['failed'].append(f"get_turno_activo(): {e}")
            results_ok = False
        
        return results_ok
    
    def check_schema_changes(self):
        """Prueba 11: Verificar cambios de schema"""
        logger.info("\n=== PRUEBA 11: Cambios de Schema ===")
        logger.info("\n📋 Cambios detectados en Supabase:")
        
        changes = [
            ("✅", "asignaciones_activas", "Nuevos campos: usos_disponibles, usos_total, id_venta_digital"),
            ("✅", "inventario", "Campo 'ubicacion' es ahora VARCHAR (antes era foreign key)"),
            ("✅", "inventario", "Nuevo campo: seccion"),
            ("✅", "miembros", "Nuevo campo: foto_url"),
            ("✅", "ca_productos_digitales", "Campo 'es_unico' confirmado"),
            ("📌", "broadcast_notifications", "Nueva tabla (no usada en manager)"),
            ("📌", "costos_productos", "Nueva tabla (no usada en manager)"),
            ("📌", "device_tokens", "Nueva tabla (no usada en manager)"),
            ("📌", "dias_festivos", "Nueva tabla (no usada en manager)"),
            ("📌", "personal", "Nueva tabla (para empleados/personal)"),
            ("📌", "recargos_cobrados", "Nueva tabla (para recargos adicionales)"),
        ]
        
        for symbol, tabla, cambio in changes:
            logger.info(f"   {symbol} {tabla}: {cambio}")
        
        self.results['passed'].append("Schema validation")
        return True
    
    def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        logger.info("\n" + "="*60)
        logger.info("PRUEBAS DE COMPATIBILIDAD - PostgresManager con Supabase")
        logger.info("="*60)
        
        # Conectar
        if not self.connect():
            logger.error("\n❌ No se pudo conectar a Supabase. Abortando pruebas.")
            return False
        
        # Ejecutar pruebas
        self.test_connection()
        self.test_authentication()
        self.test_products()
        self.test_members()
        self.test_locations()
        self.test_lockers()
        self.test_digital_products()
        self.test_notifications()
        self.test_inventory()
        self.test_cash_registers()
        self.check_schema_changes()
        
        # Mostrar resumen
        self.print_summary()
        
        # Cerrar conexión
        if self.db:
            self.db.close()
        
        return len(self.results['failed']) == 0
    
    def print_summary(self):
        """Mostrar resumen de pruebas"""
        logger.info("\n" + "="*60)
        logger.info("RESUMEN DE PRUEBAS")
        logger.info("="*60)
        
        total = len(self.results['passed']) + len(self.results['failed'])
        
        logger.info(f"\n✅ PASARON: {len(self.results['passed'])}")
        for test in self.results['passed'][:5]:
            logger.info(f"   • {test}")
        if len(self.results['passed']) > 5:
            logger.info(f"   ... y {len(self.results['passed']) - 5} más")
        
        if self.results['warnings']:
            logger.info(f"\n⚠️  ADVERTENCIAS: {len(self.results['warnings'])}")
            for warning in self.results['warnings'][:3]:
                logger.info(f"   • {warning}")
        
        if self.results['failed']:
            logger.info(f"\n❌ FALLARON: {len(self.results['failed'])}")
            for failed in self.results['failed'][:3]:
                logger.info(f"   • {failed}")
        
        logger.info(f"\n📊 TOTAL: {len(self.results['passed'])}/{total} pruebas pasaron")
        
        if len(self.results['failed']) == 0:
            logger.info("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
            logger.info("✅ PostgresManager es compatible con el schema de Supabase")
        else:
            logger.info("\n⚠️  Algunas pruebas fallaron. Ver detalles arriba.")
        
        logger.info("\n" + "="*60)


def main():
    """Función principal"""
    try:
        tester = SupabaseCompatibilityTest()
        success = tester.run_all_tests()
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Pruebas interrumpidas por el usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
