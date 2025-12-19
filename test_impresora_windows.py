"""
Script de Prueba Rápida - Impresora Generic/Text Only en Windows
Verificar si la impresora está funcionando
"""

import sys
from windows_printer_manager import WindowsPrinterManager, TicketPrinterWindows
from datetime import datetime

def main():
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*12 + "PRUEBA DE IMPRESORA WINDOWS" + " "*20 + "║")
    print("║" + " "*15 + "Generic / Text Only" + " "*25 + "║")
    print("╚" + "="*58 + "╝\n")
    
    # Paso 1: Obtener impresoras
    print("PASO 1: Buscando impresoras...")
    print("="*60)
    
    impresoras = WindowsPrinterManager.obtener_impresoras_instaladas()
    
    if not impresoras:
        print("❌ No se encontraron impresoras")
        return False
    
    print(f"✅ Se encontraron {len(impresoras)} impresoras:\n")
    for i, imp in enumerate(impresoras, 1):
        print(f"   {i}. {imp}")
    
    # Paso 2: Buscar impresora Generic
    print("\nPASO 2: Buscando impresora Generic/Text Only...")
    print("="*60)
    
    nombre_impresora = WindowsPrinterManager.obtener_impresora_por_tipo("Generic")
    
    if not nombre_impresora:
        print("❌ No se encontró impresora Generic")
        print("\nIntentando con otras palabras clave...")
        
        for palabra in ["Thermal", "Text", "USB", "POS"]:
            nombre = WindowsPrinterManager.obtener_impresora_por_tipo(palabra)
            if nombre:
                print(f"✅ Encontrada con '{palabra}': {nombre}")
                nombre_impresora = nombre
                break
    else:
        print(f"✅ Impresora encontrada: {nombre_impresora}")
    
    if not nombre_impresora:
        print("\n❌ No se pudo encontrar una impresora compatible")
        return False
    
    # Paso 3: Conectar
    print("\nPASO 3: Conectando a la impresora...")
    print("="*60)
    
    printer = TicketPrinterWindows(nombre_impresora)
    
    if not printer.conectar():
        print(f"❌ No se pudo conectar a {nombre_impresora}")
        return False
    
    print(f"✅ Conectado a: {nombre_impresora}")
    
    # Paso 4: Enviar prueba simple
    print("\nPASO 4: Enviando prueba de texto simple...")
    print("="*60)
    
    texto_simple = "TEST DE IMPRESORA\n" + "="*40 + "\nSi ves esto, funciona!\n" + "="*40 + "\n"
    
    if printer.enviar_texto(texto_simple):
        print("✅ Texto de prueba enviado")
    else:
        print("❌ Error al enviar texto")
        printer.desconectar()
        return False
    
    input("\nPresiona ENTER cuando hayas visto el texto impreso...")
    
    # Paso 5: Imprimir ticket de prueba
    print("\nPASO 5: Imprimiendo ticket de prueba...")
    print("="*60)
    
    datos_ticket = {
        'tienda': 'HTF GIMNASIO',
        'subtitulo': 'PUNTO DE VENTA - TEST',
        'numero_ticket': 9999,
        'fecha_hora': datetime.now().strftime("%d/%m/%Y %H:%M"),
        'cajero': 'TEST',
        'productos': [
            {
                'nombre': 'Bebida Energética 250ml',
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
        'metodo_pago': 'EFECTIVO'
    }
    
    if printer.imprimir_ticket(datos_ticket):
        print("✅ Ticket impreso correctamente")
    else:
        print("❌ Error al imprimir ticket")
        printer.desconectar()
        return False
    
    printer.desconectar()
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN - TODAS LAS PRUEBAS COMPLETADAS")
    print("="*60)
    print(f"✅ Impresora: {nombre_impresora}")
    print("✅ Conexión: OK")
    print("✅ Envío de texto: OK")
    print("✅ Impresión de ticket: OK")
    print("\n✨ La impresora está LISTA para usar en producción\n")
    
    return True


if __name__ == "__main__":
    try:
        if main():
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Programa interrumpido")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
