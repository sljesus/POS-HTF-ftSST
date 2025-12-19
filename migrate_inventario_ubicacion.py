"""
Script de migración para tabla inventario
Maneja el cambio de ubicacion de Foreign Key a VARCHAR
"""

import os
import sys
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Agregar ruta del proyecto
sys.path.insert(0, os.path.dirname(__file__))

from database.postgres_manager import PostgresManager


class InventarioMigration:
    """Migración de inventario.ubicacion de FK a VARCHAR"""
    
    def __init__(self):
        self.db = None
        self.migration_log = []
        self.errors = []
    
    def connect(self):
        """Conectar a Supabase"""
        try:
            config = {
                'url': os.getenv('SUPABASE_URL'),
                'key': os.getenv('SUPABASE_KEY')
            }
            
            if not config['url'] or not config['key']:
                logger.error("❌ Credenciales de Supabase no configuradas")
                return False
            
            self.db = PostgresManager(config)
            
            if self.db.is_connected:
                logger.info("✅ Conectado a Supabase")
                return True
            else:
                logger.error("❌ Error conectando a Supabase")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return False
    
    def audit_current_data(self):
        """Auditar datos actuales de inventario"""
        logger.info("\n" + "="*70)
        logger.info("AUDITORÍA - Estado actual de inventario.ubicacion")
        logger.info("="*70)
        
        try:
            response = self.db.client.table('inventario').select('id_inventario, codigo_interno, ubicacion, tipo_producto').execute()
            
            if not response.data:
                logger.info("❌ No hay datos en tabla inventario")
                return []
            
            logger.info(f"\n✅ Total registros en inventario: {len(response.data)}")
            
            # Analizar ubicaciones
            ubicaciones_unicas = {}
            problemas = []
            
            for record in response.data:
                ubicacion = record.get('ubicacion')
                codigo = record.get('codigo_interno')
                
                if ubicacion not in ubicaciones_unicas:
                    ubicaciones_unicas[ubicacion] = 0
                ubicaciones_unicas[ubicacion] += 1
                
                # Detectar problemas
                if ubicacion is None:
                    problemas.append({
                        'id': record.get('id_inventario'),
                        'codigo': codigo,
                        'problema': 'ubicacion es NULL'
                    })
                elif isinstance(ubicacion, int):
                    problemas.append({
                        'id': record.get('id_inventario'),
                        'codigo': codigo,
                        'problema': f'ubicacion es INT: {ubicacion} (debe ser convertido)'
                    })
            
            logger.info(f"\n📊 Ubicaciones únicas detectadas:")
            for ubicacion, count in sorted(ubicaciones_unicas.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"   • {ubicacion}: {count} registros")
            
            if problemas:
                logger.warning(f"\n⚠️  {len(problemas)} registros con problemas detectados:")
                for problema in problemas[:10]:
                    logger.warning(f"   • ID {problema['id']:5} - {problema['codigo']:15} - {problema['problema']}")
                if len(problemas) > 10:
                    logger.warning(f"   ... y {len(problemas) - 10} más")
            else:
                logger.info("\n✅ No hay problemas detectados - datos listos")
            
            return response.data
            
        except Exception as e:
            logger.error(f"❌ Error auditando datos: {e}")
            self.errors.append(f"Auditoría: {e}")
            return []
    
    def clean_null_ubicaciones(self):
        """Limpiar ubicaciones NULL"""
        logger.info("\n" + "="*70)
        logger.info("PASO 1: Limpiar ubicaciones NULL")
        logger.info("="*70)
        
        try:
            # Obtener registros con NULL
            response = self.db.client.table('inventario').select('id_inventario').is_('ubicacion', 'null').execute()
            
            if not response.data:
                logger.info("✅ No hay registros con ubicacion NULL")
                return True
            
            null_count = len(response.data)
            logger.info(f"⚠️  Encontrados {null_count} registros con ubicacion NULL")
            
            # Actualizar a valor por defecto
            response = self.db.client.table('inventario').update({
                'ubicacion': 'Recepción'
            }).is_('ubicacion', 'null').execute()
            
            logger.info(f"✅ {null_count} registros actualizado a 'Recepción'")
            self.migration_log.append(f"Limpieza de NULLs: {null_count} registros")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error limpiando NULLs: {e}")
            self.errors.append(f"Limpieza de NULLs: {e}")
            return False
    
    def migrate_integer_ubicaciones(self):
        """Migrar ubicaciones que son INTEGER (foreign keys)"""
        logger.info("\n" + "="*70)
        logger.info("PASO 2: Convertir referencias de foreign key a nombres descriptivos")
        logger.info("="*70)
        
        try:
            # Obtener todas las ubicaciones para mapeo
            ubicaciones_response = self.db.client.table('ca_ubicaciones').select('id_ubicacion, nombre').execute()
            
            if not ubicaciones_response.data:
                logger.warning("⚠️  No hay ubicaciones en ca_ubicaciones")
                ubicacion_map = {}
            else:
                ubicacion_map = {
                    str(u['id_ubicacion']): u['nombre'] 
                    for u in ubicaciones_response.data
                }
                logger.info(f"📋 Mapa de ubicaciones: {ubicacion_map}")
            
            # Obtener inventario con ubicaciones INTEGER
            inv_response = self.db.client.table('inventario').select('id_inventario, ubicacion').execute()
            
            migrados = 0
            errores = 0
            
            for record in inv_response.data:
                ubicacion = record['ubicacion']
                id_inv = record['id_inventario']
                
                # Si es un número (fue FK), convertir a nombre
                if isinstance(ubicacion, int) or (isinstance(ubicacion, str) and ubicacion.isdigit()):
                    ubicacion_str = str(int(ubicacion))
                    nuevo_nombre = ubicacion_map.get(ubicacion_str, f'Ubicación_{ubicacion_str}')
                    
                    try:
                        self.db.client.table('inventario').update({
                            'ubicacion': nuevo_nombre
                        }).eq('id_inventario', id_inv).execute()
                        
                        logger.info(f"   ✅ ID {id_inv}: {ubicacion} → {nuevo_nombre}")
                        migrados += 1
                    except Exception as e:
                        logger.error(f"   ❌ ID {id_inv}: Error - {e}")
                        errores += 1
            
            if migrados > 0:
                logger.info(f"\n✅ {migrados} registros convertidos correctamente")
                self.migration_log.append(f"Conversión de FKs: {migrados} registros")
            
            if errores > 0:
                logger.warning(f"⚠️  {errores} registros con error")
                self.errors.append(f"Conversión: {errores} registros fallaron")
            
            return errores == 0
            
        except Exception as e:
            logger.error(f"❌ Error en conversión: {e}")
            self.errors.append(f"Conversión de FKs: {e}")
            return False
    
    def standardize_ubicaciones(self):
        """Estandarizar nombres de ubicaciones"""
        logger.info("\n" + "="*70)
        logger.info("PASO 3: Estandarizar nombres de ubicaciones")
        logger.info("="*70)
        
        # Mapeo de nombres no estándar a estándar
        estandarizacion = {
            'recepción': 'Recepción',
            'RECEPCION': 'Recepción',
            'Recepción ': 'Recepción',
            ' Recepción': 'Recepción',
            'almacén': 'Almacén',
            'ALMACEN': 'Almacén',
            'estante': 'Estante',
            'ESTANTE': 'Estante',
            'zona lockers': 'Zona Lockers',
            'ZONA LOCKERS': 'Zona Lockers',
            'bodega': 'Bodega',
            'BODEGA': 'Bodega',
        }
        
        try:
            estandarizados = 0
            
            for antigua, nueva in estandarizacion.items():
                response = self.db.client.table('inventario').select('id_inventario').ilike('ubicacion', antigua).execute()
                
                if response.data:
                    count = len(response.data)
                    self.db.client.table('inventario').update({
                        'ubicacion': nueva
                    }).ilike('ubicacion', antigua).execute()
                    
                    logger.info(f"   ✅ '{antigua}' → '{nueva}' ({count} registros)")
                    estandarizados += count
            
            if estandarizados > 0:
                logger.info(f"\n✅ {estandarizados} registros estandarizados")
                self.migration_log.append(f"Estandarización: {estandarizados} registros")
            else:
                logger.info("✅ Todos los nombres ya están estandarizados")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en estandarización: {e}")
            self.errors.append(f"Estandarización: {e}")
            return False
    
    def verify_migration(self):
        """Verificar que la migración fue exitosa"""
        logger.info("\n" + "="*70)
        logger.info("PASO 4: Verificación final")
        logger.info("="*70)
        
        try:
            # Verificar que no haya NULL
            null_response = self.db.client.table('inventario').select('id_inventario').is_('ubicacion', 'null').execute()
            
            if null_response.data:
                logger.error(f"❌ Todavía hay {len(null_response.data)} registros con NULL")
                self.errors.append(f"Verificación: {len(null_response.data)} NULLs restantes")
                return False
            else:
                logger.info("✅ No hay registros con ubicacion NULL")
            
            # Verificar tipos de datos
            all_response = self.db.client.table('inventario').select('id_inventario, ubicacion, tipo_producto').execute()
            
            if not all_response.data:
                logger.error("❌ No hay datos en inventario")
                return False
            
            logger.info(f"✅ Total registros: {len(all_response.data)}")
            
            # Mostrar ejemplos
            logger.info("\n📋 Ejemplos de ubicaciones finales:")
            ejemplos = set()
            for record in all_response.data:
                ubicacion = record.get('ubicacion')
                if ubicacion not in ejemplos:
                    ejemplos.add(ubicacion)
                    logger.info(f"   • {ubicacion}")
                if len(ejemplos) >= 5:
                    break
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en verificación: {e}")
            self.errors.append(f"Verificación: {e}")
            return False
    
    def generate_report(self):
        """Generar reporte final"""
        logger.info("\n" + "="*70)
        logger.info("REPORTE DE MIGRACIÓN")
        logger.info("="*70)
        
        logger.info("\n✅ Cambios realizados:")
        for log in self.migration_log:
            logger.info(f"   • {log}")
        
        if self.errors:
            logger.warning(f"\n⚠️  Errores encontrados ({len(self.errors)}):")
            for error in self.errors:
                logger.warning(f"   • {error}")
        else:
            logger.info("\n✅ Sin errores - Migración completada exitosamente")
        
        logger.info("\n" + "="*70)
    
    def run(self):
        """Ejecutar migración completa"""
        logger.info("\n" + "#"*70)
        logger.info("# MIGRACIÓN - inventario.ubicacion (FK → VARCHAR)")
        logger.info("#"*70)
        
        if not self.connect():
            logger.error("❌ No se pudo conectar. Abortando.")
            return False
        
        # Auditar datos
        self.audit_current_data()
        
        # Ejecutar pasos de migración
        if not self.clean_null_ubicaciones():
            logger.warning("⚠️  Hubo problemas limpiando NULLs, continuando...")
        
        if not self.migrate_integer_ubicaciones():
            logger.warning("⚠️  Hubo problemas migrando FKs, continuando...")
        
        if not self.standardize_ubicaciones():
            logger.warning("⚠️  Hubo problemas estandarizando, continuando...")
        
        # Verificar
        success = self.verify_migration()
        
        # Generar reporte
        self.generate_report()
        
        # Cerrar conexión
        if self.db:
            self.db.close()
        
        return success


def main():
    """Función principal"""
    try:
        migration = InventarioMigration()
        success = migration.run()
        
        if success:
            logger.info("\n✅ Migración completada exitosamente")
            sys.exit(0)
        else:
            logger.error("\n❌ Migración completada con errores")
            sys.exit(1)
        
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Migración interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
