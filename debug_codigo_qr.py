"""
Script para debuggear la búsqueda por código "CASH-14"
"""

import sys
sys.path.insert(0, 'C:\\Users\\ferch\\Desktop\\HTF_gimnasio\\POS_HTF')

from database.postgres_manager import PostgresManager
from psycopg2.extras import RealDictCursor

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
    print("DEBUGGEO: Búsqueda por código CASH-14")
    print("="*70)
    
    with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
        print("\n[1] Buscando todas las notificaciones con código CASH-14...")
        cursor.execute("""
            SELECT n.id_notificacion, n.id_miembro, n.codigo_pago_generado,
                   n.respondida, n.tipo_notificacion, n.monto_pendiente
            FROM notificaciones_pos n
            WHERE n.codigo_pago_generado LIKE '%CASH-14%'
            ORDER BY n.id_notificacion DESC
        """)
        resultados = cursor.fetchall()
        
        if resultados:
            print(f"✅ Se encontraron {len(resultados)} registros:")
            for notif in resultados:
                print(f"\n   ID: {notif['id_notificacion']}")
                print(f"   Miembro: {notif['id_miembro']}")
                print(f"   Código: {notif['codigo_pago_generado']}")
                print(f"   Respondida: {notif['respondida']}")
                print(f"   Tipo: {notif['tipo_notificacion']}")
                print(f"   Monto: {notif['monto_pendiente']}")
        else:
            print("❌ No se encontraron notificaciones con CASH-14")
        
        # Buscar exactamente "CASH-14"
        print("\n[2] Buscando exactamente 'CASH-14'...")
        cursor.execute("""
            SELECT n.id_notificacion, n.id_miembro, n.codigo_pago_generado,
                   n.respondida, n.tipo_notificacion
            FROM notificaciones_pos n
            WHERE n.codigo_pago_generado = %s
        """, ("CASH-14",))
        resultado = cursor.fetchone()
        
        if resultado:
            print(f"✅ Encontrada: Notificación #{resultado['id_notificacion']}")
        else:
            print(f"❌ No encontrada")
        
        # Ver todas las notificaciones
        print("\n[3] Todas las notificaciones en la BD:")
        cursor.execute("""
            SELECT n.id_notificacion, n.codigo_pago_generado, n.respondida,
                   n.tipo_notificacion, n.id_miembro
            FROM notificaciones_pos n
            ORDER BY n.id_notificacion DESC
            LIMIT 20
        """)
        todas = cursor.fetchall()
        
        for notif in todas:
            respondida = "✓" if notif['respondida'] else "✗"
            print(f"   #{notif['id_notificacion']:3d} [{respondida}] {notif['codigo_pago_generado']:15s} {notif['tipo_notificacion']}")
    
    db.close()
    print("\n" + "="*70)
    print("FIN DEL DEBUGGEO")
    print("="*70 + "\n")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
