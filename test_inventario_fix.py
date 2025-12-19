#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_inventario_fix.py

Script para prueba del nuevo método obtener_inventario_completo()
Verifica que se obtienen todos los campos correctamente desde la BD
"""

import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Agregar ruta del proyecto
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'utils'))

from database.postgres_manager import PostgresManager
from utils.config import Config


def test_obtener_inventario_completo():
    """Test del nuevo método obtener_inventario_completo()"""
    
    print("=" * 70)
    print("TEST: obtener_inventario_completo()")
    print("=" * 70)
    
    try:
        # Conectar
        config = Config()
        db_config = config.get_postgres_config()
        pg_manager = PostgresManager(db_config)
        
        print("\n1️⃣  Obteniendo inventario completo...")
        inventario = pg_manager.obtener_inventario_completo()
        
        if not inventario:
            print("❌ No se obtuvo inventario")
            return False
        
        print(f"✅ Inventario obtenido: {len(inventario)} productos\n")
        
        # Verificar estructura
        print("2️⃣  Verificando estructura de datos...")
        campos_requeridos = [
            'id_inventario',
            'codigo_interno',
            'nombre',           # ← Crítico
            'precio',           # ← Crítico
            'categoria',        # ← Crítico
            'codigo_barras',
            'seccion',
            'tipo_producto',
            'stock_actual',
            'stock_minimo',
            'ubicacion',
            'activo'
        ]
        
        primer_producto = inventario[0]
        campos_faltantes = []
        
        for campo in campos_requeridos:
            if campo not in primer_producto:
                campos_faltantes.append(campo)
                print(f"  ❌ Falta campo: {campo}")
            else:
                print(f"  ✅ Campo presente: {campo}")
        
        if campos_faltantes:
            print(f"\n❌ Faltan campos: {campos_faltantes}")
            return False
        
        print("\n✅ Todos los campos requeridos están presentes\n")
        
        # Mostrar datos de ejemplo
        print("3️⃣  Datos de ejemplo (primeros 3 productos):")
        print("-" * 70)
        for i, producto in enumerate(inventario[:3], 1):
            print(f"\nProducto {i}:")
            print(f"  Código: {producto['codigo_interno']}")
            print(f"  Nombre: {producto['nombre']}")
            print(f"  Precio: ${producto['precio']:.2f}")
            print(f"  Categoría: {producto['categoria']}")
            print(f"  Tipo: {producto['tipo_producto']}")
            print(f"  Stock: {producto['stock_actual']} (mín: {producto['stock_minimo']})")
            print(f"  Ubicación: {producto['ubicacion']}")
            print(f"  Barras: {producto.get('codigo_barras', 'N/A')}")
        
        # Validar tipos de datos
        print("\n4️⃣  Validando tipos de datos...")
        validaciones = [
            ('id_inventario', int),
            ('codigo_interno', str),
            ('nombre', str),
            ('precio', (int, float)),
            ('categoria', str),
            ('tipo_producto', str),
            ('stock_actual', int),
            ('stock_minimo', int),
            ('activo', bool),
        ]
        
        errores_tipo = []
        for campo, tipo_esperado in validaciones:
            valor = primer_producto[campo]
            if not isinstance(valor, tipo_esperado):
                errores_tipo.append(f"{campo}: esperaba {tipo_esperado}, obtuvo {type(valor)}")
                print(f"  ❌ {campo}: tipo incorrecto")
            else:
                print(f"  ✅ {campo}: tipo correcto")
        
        if errores_tipo:
            print(f"\n❌ Errores de tipo: {errores_tipo}")
            return False
        
        print("\n✅ Todos los tipos de datos son correctos\n")
        
        # Resumen
        print("5️⃣  Resumen estadístico:")
        print("-" * 70)
        
        tipos = set(p['tipo_producto'] for p in inventario)
        print(f"  Total de productos: {len(inventario)}")
        print(f"  Tipos de producto: {tipos}")
        
        for tipo in tipos:
            cantidad = len([p for p in inventario if p['tipo_producto'] == tipo])
            print(f"    - {tipo}: {cantidad}")
        
        categorias = set(p['categoria'] for p in inventario)
        print(f"  Categorías: {len(categorias)}")
        
        ubicaciones = set(p['ubicacion'] for p in inventario)
        print(f"  Ubicaciones: {len(ubicaciones)}")
        
        stock_bajo = len([p for p in inventario if p['stock_actual'] <= p['stock_minimo']])
        print(f"  Productos con stock bajo: {stock_bajo}")
        
        print("\n" + "=" * 70)
        print("✅ TEST PASADO - obtener_inventario_completo() funciona correctamente")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        pg_manager.close()


if __name__ == '__main__':
    exito = test_obtener_inventario_completo()
    sys.exit(0 if exito else 1)
