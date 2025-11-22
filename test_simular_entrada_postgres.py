"""
Script para simular una entrada en PostgreSQL
Inserta un registro que dispara la notificación
"""

import psycopg2
from datetime import datetime

# Configuración de conexión
PG_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'HTF_DB',
    'user': 'postgres',
    'password': 'postgres'
}


def insertar_entrada_prueba():
    """Insertar una entrada de prueba que dispare la notificación"""
    print("🔌 Conectando a PostgreSQL...")
    
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        
        # Primero verificar si hay miembros en la BD
        cursor.execute("SELECT id_miembro, nombres, apellido_paterno FROM miembros LIMIT 5")
        miembros = cursor.fetchall()
        
        if not miembros:
            print("❌ No hay miembros en la base de datos")
            print("💡 Primero inserta algunos miembros para poder registrar entradas")
            conn.close()
            return
        
        print("\n📋 Miembros disponibles:")
        for idx, (id_m, nombres, apellido) in enumerate(miembros, 1):
            print(f"  {idx}. ID: {id_m} - {nombres} {apellido}")
        
        # Usar el primer miembro
        id_miembro = miembros[0][0]
        nombre_completo = f"{miembros[0][1]} {miembros[0][2]}"
        
        print(f"\n✅ Usando miembro ID: {id_miembro} ({nombre_completo})")
        
        # Insertar entrada
        print("\n📝 Insertando registro de entrada...")
        cursor.execute("""
            INSERT INTO registro_entradas 
            (id_miembro, tipo_acceso, fecha_entrada, area_accedida, dispositivo_registro, notas)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id_entrada
        """, (
            id_miembro,
            'miembro',
            datetime.now(),
            'Gimnasio',
            'POS_TEST',
            'Entrada de prueba desde script'
        ))
        
        id_entrada = cursor.fetchone()[0]
        conn.commit()
        
        print(f"✅ Entrada registrada con ID: {id_entrada}")
        print(f"🔔 La notificación debería haber sido enviada al canal 'nueva_entrada_canal'")
        print(f"\n💡 Verifica el listener para ver si recibió la notificación")
        
        cursor.close()
        conn.close()
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ Error de conexión: {e}")
        print("\n💡 Verifica la configuración de PostgreSQL")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  SIMULADOR DE ENTRADA - POSTGRESQL")
    print("="*60 + "\n")
    
    insertar_entrada_prueba()
