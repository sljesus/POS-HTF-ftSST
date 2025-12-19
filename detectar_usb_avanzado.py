"""
Detectar impresora USB en Windows usando WMI
Más confiable que detectar puertos COM directamente
"""

import os
import sys
import subprocess
import re
from config_impresora import ConfiguradorImpresora

def obtener_puertos_de_registro():
    """Obtener puertos COM del registro de Windows"""
    print("\n" + "="*60)
    print("BUSCANDO PUERTOS USB EN EL REGISTRO DE WINDOWS")
    print("="*60 + "\n")
    
    try:
        # Comando para obtener información de puertos
        cmd = 'reg query "HKEY_LOCAL_MACHINE\\HARDWARE\\DEVICEMAP\\SERIALCOMM"'
        resultado = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        
        puertos = []
        
        # Parsear la salida
        for linea in resultado.stdout.split('\n'):
            if 'COM' in linea:
                # Extraer el número de puerto
                match = re.search(r'COM(\d+)', linea)
                if match:
                    puerto = f"COM{match.group(1)}"
                    puertos.append(puerto)
                    print(f"✅ Encontrado: {puerto}")
        
        return puertos
    except Exception as e:
        print(f"❌ Error al acceder al registro: {e}")
        return []


def obtener_dispositivos_usb():
    """Obtener dispositivos USB conectados"""
    print("\n" + "="*60)
    print("DISPOSITIVOS USB CONECTADOS")
    print("="*60 + "\n")
    
    try:
        # Comando para listar dispositivos USB
        cmd = 'Get-PnpDevice -Class Ports -PresentOnly | Select-Object Name, FriendlyName | ConvertTo-Csv -NoTypeInformation'
        resultado = subprocess.run(
            ['powershell', '-Command', cmd],
            capture_output=True,
            text=True
        )
        
        print("Dispositivos encontrados:\n")
        print(resultado.stdout)
        
        return resultado.stdout
    except Exception as e:
        print(f"Error: {e}")
        return ""


def obtener_impresoras_windows():
    """Obtener impresoras instaladas en Windows"""
    print("\n" + "="*60)
    print("IMPRESORAS INSTALADAS EN WINDOWS")
    print("="*60 + "\n")
    
    try:
        # Obtener impresoras
        cmd = 'Get-Printer -Name "*" | Select-Object Name, PortName | ConvertTo-Csv -NoTypeInformation'
        resultado = subprocess.run(
            ['powershell', '-Command', cmd],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        impresoras = []
        
        for linea in resultado.stdout.split('\n'):
            if 'Generic' in linea or 'Thermal' in linea or 'Text' in linea:
                print(f"✅ {linea}")
                impresoras.append(linea)
                
                # Extraer puerto si está disponible
                if 'COM' in linea:
                    match = re.search(r'(COM\d+)', linea)
                    if match:
                        return match.group(1)
        
        return impresoras
    except Exception as e:
        print(f"Error: {e}")
        return []


def probar_puertos_directos():
    """Probar conexión directa con todos los puertos"""
    print("\n" + "="*60)
    print("PROBANDO CONEXIÓN DIRECTA CON PUERTOS COM")
    print("="*60 + "\n")
    
    import serial
    import time
    
    velocidades = [9600, 19200, 38400, 57600, 115200]
    encontrados = []
    
    # Intentar con puertos comunes
    for puerto_num in range(1, 10):
        puerto = f"COM{puerto_num}"
        
        for baudrate in velocidades:
            try:
                print(f"Probando {puerto} @ {baudrate} baud...", end=" ", flush=True)
                
                ser = serial.Serial(
                    port=puerto,
                    baudrate=baudrate,
                    timeout=0.5,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS
                )
                
                # Enviar comando de test
                ser.write(b'\x1b\x40')
                time.sleep(0.2)
                
                ser.close()
                print(f"✅ CONECTADO")
                encontrados.append({
                    'puerto': puerto,
                    'baudrate': baudrate
                })
                break  # Si funciona, pasar al siguiente puerto
                
            except serial.SerialException:
                print("❌", end=" ", flush=True)
            except Exception as e:
                print(f"Error: {str(e)[:10]}", end=" ", flush=True)
        
        if encontrados and encontrados[-1]['puerto'] == puerto:
            print()
    
    return encontrados


def main():
    """Programa principal"""
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*10 + "LOCALIZADOR DE PUERTO USB - IMPRESORA" + " "*12 + "║")
    print("║" + " "*20 + "Windows Generic/Text Only" + " "*13 + "║")
    print("╚" + "="*58 + "╝")
    
    print("\nEste script buscará el puerto COM de tu impresora USB...")
    print("Proceso: Registro → Dispositivos → Conexión directa\n")
    
    # Paso 1: Registro de Windows
    puertos_registro = obtener_puertos_de_registro()
    
    # Paso 2: Dispositivos USB
    dispositivos_usb = obtener_dispositivos_usb()
    
    # Paso 3: Impresoras instaladas
    impresoras = obtener_impresoras_windows()
    
    # Paso 4: Probar conexión directa
    print("\nFase 4: Intentando conexión directa...\n")
    encontrados = probar_puertos_directos()
    
    # Resultado
    print("\n" + "="*60)
    print("RESULTADO")
    print("="*60 + "\n")
    
    if encontrados:
        print("✅ IMPRESORA(S) ENCONTRADA(S):\n")
        for info in encontrados:
            print(f"   Puerto: {info['puerto']}")
            print(f"   Baudrate: {info['baudrate']}")
            print()
        
        # Guardar
        puerto = encontrados[0]['puerto']
        baudrate = encontrados[0]['baudrate']
        
        respuesta = input("¿Guardar esta configuración? (s/n): ").lower()
        if respuesta == 's':
            config = ConfiguradorImpresora()
            config.establecer("puerto_impresora", puerto)
            config.establecer("baudrate", baudrate)
            print(f"\n✅ Guardado: {puerto} @ {baudrate} baud")
    else:
        print("❌ No se encontró impresora conectada")
        print("\nVerifica que:")
        print("- La impresora esté conectada por USB")
        print("- Esté encendida")
        print("- Los drivers estén instalados")
        print("- Intenta en un puerto USB diferente")


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
