"""
Script de prueba para el diálogo de confirmación de pago en efectivo
Ejecuta el diálogo de manera independiente para verificar la UI
"""

import sys
from PySide6.QtWidgets import QApplication
from ui.confirmar_pago_efectivo_dialog import ConfirmarPagoEfectivoDialog


class MockSupabaseService:
    """Mock del servicio de Supabase para pruebas"""
    def __init__(self):
        self.client = None
        print("[Mock] Servicio de Supabase simulado creado")


def main():
    """Ejecutar diálogo de confirmación de pago"""
    app = QApplication(sys.argv)
    
    # Crear mock del servicio
    supabase_service = MockSupabaseService()
    
    # Crear y mostrar el diálogo
    dialog = ConfirmarPagoEfectivoDialog(supabase_service)
    
    print("\n" + "="*60)
    print("DIÁLOGO DE CONFIRMACIÓN DE PAGO EN EFECTIVO")
    print("="*60)
    print("Este es un modo de prueba visual.")
    print("El diálogo mostrará la nueva UI homologada con inventario.")
    print("="*60 + "\n")
    
    # Mostrar diálogo
    result = dialog.exec()
    
    if result:
        print("[OK] Diálogo aceptado")
    else:
        print("[INFO] Diálogo cancelado")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
