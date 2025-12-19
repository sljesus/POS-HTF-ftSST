"""
Script rápido para detectar puerto COM de impresora USB instalada
Funciona con impresoras instaladas como "Generic/Text Only" en Windows
"""

import serial
import os
import sys
from config_impresora import ConfiguradorImpresora
import time

def detectar_puerto_usb():
    """Detectar puerto COM de impresora USB"""
    print("\n" + "="*60)
    print("DETECCIÓN DE PUERTO COM - IMPRESORA USB")
    print("="*60)
    
    # Obtener puertos disponibles
    puertos = ConfiguradorImpresora.obtener_puertos_disponibles()
    
    print("\nPuertos disponibles en el sistema:\n")
    puertos_disponibles = []
    
    for i, puerto in enumerate(puertos, 1):
        estado = "✅ DISPONIBLE" if puerto['disponible'] else "❌ EN USO"
        print(f"{i}. {puerto['puerto']:6} - {estado}")
        if puerto['disponible']:
            puertos_disponibles.append(puerto['puerto'])
    
    if not puertos_disponibles:
        print("\n❌ No hay puertos COM disponibles")
        return None
    
    print(f"\n{'='*60}")
    print("Selecciona el puerto COM de la impresora")
    print(f"{'='*60}\n")
    
    while True:
        entrada = input("Ingresa el número o el puerto (ej: 1 o COM3): ").strip()
        
        # Si es número
        if entrada.isdigit():
            idx = int(entrada) - 1
            if 0 <= idx < len(puertos_disponibles):
                puerto = puertos_disponibles[idx]
                break
            else:
                print("❌ Número inválido. Intenta de nuevo.")
        # Si es puerto
        elif entrada.upper().startswith("COM"):
            if entrada.upper() in puertos_disponibles:
                puerto = entrada.upper()
                break
            else:
                print(f"❌ {entrada} no está disponible")
        else:
            print("❌ Entrada inválida. Usa formato: COM3 o número")
    
    return puerto


def probar_puerto(puerto):
    """Probar conexión con el puerto"""
    print(f"\n{'='*60}")
    print(f"PROBANDO PUERTO: {puerto}")
    print(f"{'='*60}\n")
    
    # Velocidades comunes para impresoras
    velocidades = [9600, 19200, 38400, 57600, 115200]
    
    for baudrate in velocidades:
        try:
            print(f"Intentando {puerto} a {baudrate} baud...", end=" ")
            
            ser = serial.Serial(
                port=puerto,
                baudrate=baudrate,
                timeout=1.0,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
            
            # Enviar test (ESC/POS reset)
            ser.write(b'\x1b\x40')  # ESC @
            time.sleep(0.5)
            
            ser.close()
            print("✅ CONECTADO")
            return baudrate
            
        except Exception as e:
            print(f"❌ ({str(e)[:20]}...)")
    
    return None


def enviar_test(puerto, baudrate):
    """Enviar texto de prueba"""
    print(f"\n{'='*60}")
    print("ENVIANDO TEXTO DE PRUEBA")
    print(f"{'='*60}\n")
    
    try:
        ser = serial.Serial(
            port=puerto,
            baudrate=baudrate,
            timeout=2.0,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
        
        print("Enviando comando de inicialización...")
        ser.write(b'\x1b\x40')  # Reset
        time.sleep(0.3)
        
        print("Enviando texto...\n")
        
        # Texto de prueba
        texto = "TEST IMPRESORA\n"
        texto += "="*40 + "\n"
        texto += "Puerto: " + puerto + "\n"
        texto += "Baudrate: " + str(baudrate) + "\n"
        texto += "="*40 + "\n"
        texto += "\nSi ves esto, la conexion es correcta!\n\n"
        
        ser.write(texto.encode('utf-8'))
        
        print("✅ Texto enviado a la impresora")
        print("\n¿Ves el texto impreso en la impresora térmica?\n")
        
        ser.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def guardar_puerto(puerto, baudrate):
    """Guardar puerto en configuración"""
    print(f"\n{'='*60}")
    print("GUARDAR CONFIGURACIÓN")
    print(f"{'='*60}\n")
    
    config = ConfiguradorImpresora()
    config.establecer("puerto_impresora", puerto)
    config.establecer("baudrate", baudrate)
    
    print(f"✅ Configuración guardada:")
    print(f"   Puerto: {puerto}")
    print(f"   Baudrate: {baudrate}")
    print(f"   Archivo: config_impresora.json")


def main():
    """Programa principal"""
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*15 + "CONFIGURADOR DE PUERTO USB" + " "*17 + "║")
    print("║" + " "*10 + "Impresora: Generic/Text Only" + " "*20 + "║")
    print("╚" + "="*58 + "╝")
    
    # Detectar puerto
    puerto = detectar_puerto_usb()
    if not puerto:
        return
    
    # Probar velocidad
    baudrate = probar_puerto(puerto)
    if not baudrate:
        print("\n❌ No se pudo conectar con ninguna velocidad")
        print("Verifica que:")
        print("- La impresora esté conectada")
        print("- Los drivers estén instalados")
        return
    
    print(f"\n✅ Conexión establecida a {baudrate} baud")
    
    # Enviar prueba
    if not enviar_test(puerto, baudrate):
        print("❌ Error al enviar texto")
        return
    
    # Guardar
    respuesta = input("\n¿Guardar esta configuración? (s/n): ").lower()
    if respuesta == 's':
        guardar_puerto(puerto, baudrate)
        print("\n✅ ¡Listo! La impresora está configurada.")
        print(f"\nPuede ahora usar la impresora en el sistema POS.")
        print(f"Puerto: {puerto}")
        print(f"Baudrate: {baudrate}")
    else:
        print("\nConfiguración no guardada.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Programa interrumpido")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
