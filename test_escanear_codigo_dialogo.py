"""
Script de prueba para el diálogo de escanear código de pago
Ejecuta el diálogo de manera independiente para verificar la UI
"""

import sys
from PySide6.QtWidgets import QApplication
from ui.escanear_codigo_dialogo import EscanearCodigoDialogo


class MockPgManager:
    """Mock del PostgreSQL Manager para pruebas"""
    def __init__(self):
        print("[Mock] PostgreSQL Manager simulado creado")
    
    def buscar_notificacion_por_codigo_pago(self, codigo):
        print(f"[Mock] Buscando código: {codigo}")
        return None


class MockSupabaseService:
    """Mock del servicio de Supabase para pruebas"""
    def __init__(self):
        self.client = None
        print("[Mock] Servicio de Supabase simulado creado")


def main():
    """Ejecutar diálogo de escanear código"""
    app = QApplication(sys.argv)
    
    # Crear mocks de los servicios
    pg_manager = MockPgManager()
    supabase_service = MockSupabaseService()
    user_data = {
        'id_usuario': 1,
        'nombre': 'Usuario Test',
        'rol': 'admin'
    }
    
    # Crear y mostrar el diálogo
    dialog = EscanearCodigoDialogo(
        pg_manager=pg_manager,
        supabase_service=supabase_service,
        user_data=user_data
    )
    
    print("\n" + "="*60)
    print("DIÁLOGO DE ESCANEAR CÓDIGO DE PAGO")
    print("="*60)
    print("Este es un modo de prueba visual.")
    print("El diálogo permite escanear códigos de pago (formato CASH-XXX).")
    print("="*60 + "\n")
    
    # Mostrar diálogo
    result = dialog.exec()
    
    if result:
        print("[OK] Diálogo aceptado")
        if dialog.notificacion:
            print(f"    Notificación procesada: {dialog.notificacion}")
        else:
            print("    Sin notificación (modo prueba)")
    else:
        print("[INFO] Diálogo cancelado")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
