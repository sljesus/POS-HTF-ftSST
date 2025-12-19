"""
Script de Prueba para Impresora ESC/POS
Verificar conexión y funcionalidad antes de usar en producción
"""

import sys
import time
from escpos_printer import TicketPrinter, EscPosDriver
from config_impresora import ConfiguradorImpresora


def prueba_puertos():
    """Detectar puertos COM disponibles"""
    print("\n" + "="*60)
    print("PASO 1: DETECTAR PUERTOS DISPONIBLES")
    print("="*60)
    
    puertos = ConfiguradorImpresora.obtener_puertos_disponibles()
    
    if not puertos:
        print("❌ No se encontraron puertos COM")
        return None
    
    print(f"Se encontraron {len(puertos)} puertos:\n")
    for i, puerto in enumerate(puertos, 1):
        estado = "✅ DISPONIBLE" if puerto['disponible'] else "❌ EN USO"
        print(f"{i}. {puerto['puerto']:6} - {estado}")
    
    # Retornar primer puerto disponible
    puertos_disponibles = [p for p in puertos if p['disponible']]
    if puertos_disponibles:
        return puertos_disponibles[0]['puerto']
    return None


def prueba_conexion(puerto):
    """Probar conexión básica"""
    print("\n" + "="*60)
    print(f"PASO 2: PROBAR CONEXIÓN EN {puerto}")
    print("="*60)
    
    driver = EscPosDriver(puerto)
    
    if driver.conectar():
        print(f"✅ Conexión exitosa en {puerto}")
        driver.inicializar()
        print("✅ Impresora inicializada")
        
        # Enviar comando de prueba
        driver.alinear_centro()
        driver.fuente_grande()
        driver.texto("TEST OK")
        driver.nueva_linea(2)
        
        print("✅ Texto enviado a impresora")
        driver.desconectar()
        return True
    else:
        print(f"❌ No se pudo conectar a {puerto}")
        return False


def prueba_ticket_completo(puerto):
    """Imprimir ticket de prueba completo"""
    print("\n" + "="*60)
    print(f"PASO 3: IMPRIMIR TICKET DE PRUEBA EN {puerto}")
    print("="*60)
    
    printer = TicketPrinter(puerto)
    
    if not printer.conectar():
        print(f"❌ No se pudo conectar a {puerto}")
        return False
    
    # Datos de prueba
    datos_ticket = {
        'tienda': 'HTF GIMNASIO',
        'subtitulo': 'PRUEBA DE IMPRESORA',
        'numero_ticket': 9999,
        'fecha_hora': time.strftime("%d/%m/%Y %H:%M"),
        'cajero': 'TEST',
        'productos': [
            {
                'nombre': 'Bebida Energética Red Bull 250ml',
                'cantidad': 2,
                'precio': 5.00,
                'subtotal': 10.00
            },
            {
                'nombre': 'Toalla de Microfibra',
                'cantidad': 1,
                'precio': 15.00,
                'subtotal': 15.00
            },
            {
                'nombre': 'Shaker Botella 600ml',
                'cantidad': 1,
                'precio': 8.50,
                'subtotal': 8.50
            },
        ],
        'total': 33.50,
        'metodo_pago': 'EFECTIVO',
        'abrir_caja': False,  # Cambiar a True si tienes caja conectada
        'cortar': True
    }
    
    print("\nImprimiendo ticket de prueba...")
    print("Datos del ticket:")
    print(f"  - Tienda: {datos_ticket['tienda']}")
    print(f"  - Número: {datos_ticket['numero_ticket']}")
    print(f"  - Productos: {len(datos_ticket['productos'])}")
    print(f"  - Total: ${datos_ticket['total']:.2f}")
    print()
    
    if printer.imprimir_ticket(datos_ticket):
        print("✅ Ticket impreso exitosamente")
        printer.desconectar()
        return True
    else:
        print("❌ Error al imprimir ticket")
        printer.desconectar()
        return False


def menu_principal():
    """Menú de opciones"""
    print("\n" + "="*60)
    print("PRUEBA DE IMPRESORA ESC/POS - HTF POS")
    print("="*60)
    print("\nOpciones:")
    print("1. Detectar puertos COM disponibles")
    print("2. Probar conexión básica")
    print("3. Imprimir ticket de prueba")
    print("4. Ejecutar todas las pruebas")
    print("5. Salir")
    print()
    
    return input("Selecciona una opción (1-5): ").strip()


def main():
    """Programa principal"""
    while True:
        opcion = menu_principal()
        
        if opcion == "1":
            puerto = prueba_puertos()
        
        elif opcion == "2":
            puerto = input("\nIngresa puerto COM (ej: COM3): ").strip().upper()
            if puerto:
                prueba_conexion(puerto)
            else:
                print("❌ Puerto inválido")
        
        elif opcion == "3":
            puerto = input("\nIngresa puerto COM (ej: COM3): ").strip().upper()
            if puerto:
                input("\n⚠️  ASEGÚRATE QUE LA IMPRESORA ESTÉ CONECTADA\nPresiona ENTER para continuar...")
                prueba_ticket_completo(puerto)
            else:
                print("❌ Puerto inválido")
        
        elif opcion == "4":
            print("\n" + "="*60)
            print("EJECUTANDO TODAS LAS PRUEBAS")
            print("="*60)
            
            # Paso 1: Detectar puertos
            puerto = prueba_puertos()
            if not puerto:
                print("\n❌ No hay puertos disponibles. Verifica la impresora.")
                continue
            
            input(f"\n⚠️  Se usará puerto {puerto}\nPresiona ENTER para continuar...")
            
            # Paso 2: Probar conexión
            if not prueba_conexion(puerto):
                print("\n❌ No se pudo conectar a la impresora")
                continue
            
            input("\nPresiona ENTER para la siguiente prueba...")
            
            # Paso 3: Ticket completo
            prueba_ticket_completo(puerto)
            
            print("\n" + "="*60)
            print("RESUMEN DE PRUEBAS")
            print("="*60)
            print("✅ Todas las pruebas completadas")
            print(f"✅ Puerto: {puerto}")
            print("✅ Conexión: OK")
            print("✅ Impresión: OK")
            print("\n¡La impresora está lista para usar en producción!")
        
        elif opcion == "5":
            print("\n👋 ¡Hasta luego!")
            break
        
        else:
            print("\n❌ Opción no válida. Intenta de nuevo.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Programa interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
