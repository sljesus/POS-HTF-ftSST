"""
Configuración de Impresora ESC/POS
Archivo para gestionar los puertos COM disponibles
"""

import os
import json
from typing import List, Dict
import serial
import logging

logger = logging.getLogger(__name__)

CONFIG_FILE = "config_impresora.json"


class ConfiguradorImpresora:
    """Gestor de configuración de impresora"""
    
    DEFAULT_CONFIG = {
        "puerto_impresora": "COM3",
        "baudrate": 115200,
        "abrir_caja_automaticamente": True,
        "cortar_papel_automaticamente": True,
        "timeout_conexion": 2.0,
        "nombre_tienda": "HTF GIMNASIO",
        "subtitulo_tienda": "PUNTO DE VENTA"
    }
    
    def __init__(self, archivo_config: str = CONFIG_FILE):
        self.archivo_config = archivo_config
        self.config = self.cargar_config()
    
    def cargar_config(self) -> Dict:
        """Cargar configuración desde archivo"""
        if os.path.exists(self.archivo_config):
            try:
                with open(self.archivo_config, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    logger.info("✅ Configuración cargada desde archivo")
                    return config
            except Exception as e:
                logger.warning(f"Error al cargar config: {e}. Usando defaults.")
        
        return self.DEFAULT_CONFIG.copy()
    
    def guardar_config(self) -> bool:
        """Guardar configuración a archivo"""
        try:
            with open(self.archivo_config, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
                logger.info(f"✅ Configuración guardada en {self.archivo_config}")
                return True
        except Exception as e:
            logger.error(f"Error al guardar config: {e}")
            return False
    
    def obtener(self, clave: str, default=None):
        """Obtener valor de configuración"""
        return self.config.get(clave, default or self.DEFAULT_CONFIG.get(clave))
    
    def establecer(self, clave: str, valor):
        """Establecer valor de configuración"""
        self.config[clave] = valor
        self.guardar_config()
    
    @staticmethod
    def obtener_puertos_disponibles() -> List[Dict]:
        """
        Obtener lista de puertos COM disponibles
        
        Returns:
            Lista de dicts con {puerto, descripcion, disponible}
        """
        puertos = []
        
        # Puertos comunes en Windows
        puertos_comunes = [f"COM{i}" for i in range(1, 10)]
        
        for puerto in puertos_comunes:
            try:
                ser = serial.Serial(puerto, timeout=0.1)
                ser.close()
                puertos.append({
                    'puerto': puerto,
                    'descripcion': f"{puerto} - Disponible",
                    'disponible': True
                })
                logger.info(f"✅ Puerto {puerto} disponible")
            except serial.SerialException:
                puertos.append({
                    'puerto': puerto,
                    'descripcion': f"{puerto} - No disponible",
                    'disponible': False
                })
        
        return puertos
    
    @staticmethod
    def probar_conexion(puerto: str, baudrate: int = 115200, timeout: float = 1.0) -> bool:
        """
        Probar conexión con puerto
        
        Args:
            puerto: Puerto COM a probar
            baudrate: Velocidad de comunicación
            timeout: Timeout de conexión
            
        Returns:
            bool: Éxito de conexión
        """
        try:
            ser = serial.Serial(
                port=puerto,
                baudrate=baudrate,
                timeout=timeout,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
            
            # Intentar inicializar impresora
            ser.write(b'\x1b\x40')  # Comando de reset
            time.sleep(0.5)
            
            ser.close()
            logger.info(f"✅ Conexión exitosa con {puerto}")
            return True
            
        except Exception as e:
            logger.warning(f"❌ No se pudo conectar a {puerto}: {e}")
            return False


# ===== EJEMPLOS =====

if __name__ == "__main__":
    import time
    
    # Crear configurador
    config = ConfiguradorImpresora()
    
    # Mostrar puertos disponibles
    print("\n=== PUERTOS DISPONIBLES ===")
    puertos = config.obtener_puertos_disponibles()
    for puerto in puertos:
        estado = "✅" if puerto['disponible'] else "❌"
        print(f"{estado} {puerto['descripcion']}")
    
    # Obtener configuración actual
    print("\n=== CONFIGURACIÓN ACTUAL ===")
    print(f"Puerto: {config.obtener('puerto_impresora')}")
    print(f"Baudrate: {config.obtener('baudrate')}")
    print(f"Abrir caja: {config.obtener('abrir_caja_automaticamente')}")
    print(f"Cortar papel: {config.obtener('cortar_papel_automaticamente')}")
    
    # Probar conexión
    puerto = config.obtener('puerto_impresora')
    print(f"\n=== PROBANDO CONEXIÓN ===")
    if config.probar_conexion(puerto):
        print(f"✅ Conexión exitosa con {puerto}")
    else:
        print(f"❌ No se pudo conectar a {puerto}")
