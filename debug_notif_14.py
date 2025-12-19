"""
Script para debuggear el problema de notificación 14
Verifica si la notificación existe y tiene venta_digital asociada
"""

import sys
sys.path.insert(0, 'C:\\Users\\ferch\\Desktop\\HTF_gimnasio\\POS_HTF')

from database.postgres_manager import PostgresManager
from psycopg2.extras import RealDictCursor
import json

# Configuración
config = {
    'host': '192.168.100.4',
    'port': '5432',
    'database': 'htf_db',
    'user': 'postgres',
    'password': 'postgres'
}

try:
    db = PostgresManager(config)
    
    print("\n" + "="*70)
    print("DEBUGGEO: Notificación 14")
    print("="*70)
    
    # 1. Obtener datos de la notificación 14
    with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
        print("\n[1] Buscando notificación 14...")
        cursor.execute("""
            SELECT n.id_notificacion, n.id_miembro, n.id_venta_digital,
                   n.codigo_pago_generado, n.tipo_notificacion,
                   n.monto_pendiente, n.respondida
            FROM notificaciones_pos n
            WHERE n.id_notificacion = 14
        """)
        notif = cursor.fetchone()
        
        if notif:
            print(f"✅ Notificación encontrada:")
            for key, value in notif.items():
                print(f"   {key}: {value}")
        else:
            print("❌ Notificación NO encontrada")
            db.close()
            sys.exit(1)
        
        # 2. Verificar si tiene id_venta_digital
        id_venta = notif['id_venta_digital']
        print(f"\n[2] id_venta_digital = {id_venta}")
        
        if id_venta is not None:
            print(f"   → Buscando venta_digital {id_venta}...")
            cursor.execute("""
                SELECT vd.id_venta_digital, vd.id_miembro, vd.id_producto_digital,
                       vd.estado, vd.fecha_inicio, vd.fecha_fin, vd.id_locker
                FROM ventas_digitales vd
                WHERE vd.id_venta_digital = %s
            """, (id_venta,))
            venta = cursor.fetchone()
            
            if venta:
                print(f"   ✅ Venta digital encontrada:")
                for key, value in venta.items():
                    print(f"      {key}: {value}")
            else:
                print(f"   ❌ Venta digital {id_venta} NO encontrada")
        else:
            print("   → id_venta_digital es NULL, buscando fallback...")
        
        # 3. Buscar ventas del miembro
        id_miembro = notif['id_miembro']
        print(f"\n[3] Buscando ventas del miembro {id_miembro}...")
        cursor.execute("""
            SELECT vd.id_venta_digital, vd.id_miembro, vd.id_producto_digital,
                   vd.estado, vd.fecha_inicio, vd.fecha_fin, vd.id_locker,
                   pd.nombre
            FROM ventas_digitales vd
            LEFT JOIN ca_productos_digitales pd ON vd.id_producto_digital = pd.id_producto_digital
            WHERE vd.id_miembro = %s
            ORDER BY vd.id_venta_digital DESC
        """, (id_miembro,))
        ventas = cursor.fetchall()
        
        if ventas:
            print(f"   ✅ Se encontraron {len(ventas)} ventas:")
            for i, v in enumerate(ventas, 1):
                print(f"\n   [{i}] ID: {v['id_venta_digital']}")
                print(f"       Producto: {v['nombre']}")
                print(f"       Estado: {v['estado']}")
                print(f"       Locker: {v['id_locker']}")
                print(f"       Inicio: {v['fecha_inicio']}")
                print(f"       Fin: {v['fecha_fin']}")
        else:
            print(f"   ❌ No se encontraron ventas para el miembro {id_miembro}")
        
        # 4. Buscar miembro
        print(f"\n[4] Buscando datos del miembro {id_miembro}...")
        cursor.execute("""
            SELECT id_miembro, nombres, apellido_paterno, apellido_materno, 
                   telefono, email
            FROM miembros
            WHERE id_miembro = %s
        """, (id_miembro,))
        miembro = cursor.fetchone()
        
        if miembro:
            print(f"   ✅ Miembro encontrado:")
            for key, value in miembro.items():
                print(f"      {key}: {value}")
        else:
            print(f"   ❌ Miembro NO encontrado")

    db.close()
    print("\n" + "="*70)
    print("FIN DEL DEBUGGEO")
    print("="*70 + "\n")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
