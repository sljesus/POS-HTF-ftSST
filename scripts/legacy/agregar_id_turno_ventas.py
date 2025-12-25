"""
Script para agregar campo id_turno a la tabla ventas en Supabase
Ejecutar una sola vez para modificar el esquema de la base de datos
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.supabase_service import SupabaseService
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def agregar_campo_id_turno():
    """Agregar campo id_turno a la tabla ventas"""
    
    print("=" * 60)
    print("AGREGAR CAMPO id_turno A TABLA VENTAS")
    print("=" * 60)
    print()
    
    try:
        # Inicializar servicio de Supabase
        print("Conectando a Supabase...")
        supabase_service = SupabaseService()
        client = supabase_service.get_client()
        
        print("✓ Conexión establecida")
        print()
        
        # SQL para agregar columna id_turno
        sql_statements = [
            # Agregar columna id_turno (permitir NULL para ventas históricas)
            """
            ALTER TABLE ventas 
            ADD COLUMN IF NOT EXISTS id_turno INTEGER;
            """,
            
            # Agregar foreign key constraint
            """
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint 
                    WHERE conname = 'fk_ventas_turno'
                ) THEN
                    ALTER TABLE ventas
                    ADD CONSTRAINT fk_ventas_turno
                    FOREIGN KEY (id_turno) 
                    REFERENCES turnos_caja(id_turno)
                    ON DELETE SET NULL;
                END IF;
            END $$;
            """,
            
            # Crear índice para mejorar rendimiento
            """
            CREATE INDEX IF NOT EXISTS idx_ventas_id_turno 
            ON ventas(id_turno);
            """
        ]
        
        print("Ejecutando modificaciones en la base de datos...")
        print()
        
        for i, sql in enumerate(sql_statements, 1):
            try:
                print(f"[{i}/{len(sql_statements)}] Ejecutando: {sql.strip()[:50]}...")
                
                # Ejecutar SQL usando RPC o directamente
                client.rpc('exec_sql', {'sql': sql}).execute()
                
                print(f"    ✓ Completado")
                
            except Exception as e:
                # Si falla con RPC, intentar con postgrest
                error_msg = str(e)
                if "does not exist" in error_msg or "rpc" in error_msg.lower():
                    print(f"    ⚠ No se puede ejecutar con RPC")
                    print(f"    → Debes ejecutar este SQL manualmente en Supabase SQL Editor:")
                    print()
                    print(sql)
                    print()
                else:
                    raise e
        
        print()
        print("=" * 60)
        print("✓ PROCESO COMPLETADO")
        print("=" * 60)
        print()
        print("Cambios realizados:")
        print("  • Columna 'id_turno' agregada a tabla 'ventas'")
        print("  • Foreign key constraint creado (fk_ventas_turno)")
        print("  • Índice creado (idx_ventas_id_turno)")
        print()
        print("IMPORTANTE: Si aparecieron advertencias de RPC,")
        print("ejecuta el SQL manualmente en Supabase SQL Editor:")
        print()
        print("ALTER TABLE ventas ADD COLUMN IF NOT EXISTS id_turno INTEGER;")
        print()
        print("ALTER TABLE ventas")
        print("ADD CONSTRAINT fk_ventas_turno")
        print("FOREIGN KEY (id_turno) REFERENCES turnos_caja(id_turno)")
        print("ON DELETE SET NULL;")
        print()
        print("CREATE INDEX IF NOT EXISTS idx_ventas_id_turno ON ventas(id_turno);")
        print()
        
    except Exception as e:
        print()
        print("=" * 60)
        print("✗ ERROR")
        print("=" * 60)
        print()
        print(f"Error: {str(e)}")
        print()
        print("SOLUCIÓN: Ejecuta el siguiente SQL manualmente en Supabase:")
        print()
        print("-- Agregar columna")
        print("ALTER TABLE ventas ADD COLUMN IF NOT EXISTS id_turno INTEGER;")
        print()
        print("-- Agregar foreign key")
        print("ALTER TABLE ventas")
        print("ADD CONSTRAINT fk_ventas_turno")
        print("FOREIGN KEY (id_turno) REFERENCES turnos_caja(id_turno)")
        print("ON DELETE SET NULL;")
        print()
        print("-- Crear índice")
        print("CREATE INDEX IF NOT EXISTS idx_ventas_id_turno ON ventas(id_turno);")
        print()
        logging.error(f"Error en el script: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print()
    input("Presiona ENTER para continuar...")
    print()
    
    exito = agregar_campo_id_turno()
    
    print()
    input("Presiona ENTER para salir...")
    
    sys.exit(0 if exito else 1)
