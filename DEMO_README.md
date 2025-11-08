# 🏋️ HTF Gimnasio POS - Demo

## 📦 Ejecutable Generado

**Archivo:** `dist/HTF_Gimnasio_POS.exe`  
**Tamaño:** ~81 MB  
**Requiere:** Ninguna dependencia (todo incluido)

## 🎯 Datos de Prueba Incluidos

La base de datos local ya contiene datos de demostración:

### 👥 Miembros (10 activos)
- Juan Carlos Pérez García - MIEMBRO001
- María González Martínez - MIEMBRO002
- Roberto Sánchez López - MIEMBRO003
- Ana Laura Ramírez Torres - MIEMBRO004
- Carlos Mendoza Flores - MIEMBRO005
- Laura Jiménez Castro - MIEMBRO006
- Miguel Ortiz Ruiz - MIEMBRO007
- Patricia Hernández Morales - MIEMBRO008
- Fernando Cruz Domínguez - MIEMBRO009
- Carmen Vargas Reyes - MIEMBRO010

### 🥤 Productos (12 items)
**Bebidas:**
- Coca Cola 600ml - BEB001
- Agua Ciel 1L - BEB002
- Gatorade Naranja - BEB003
- Red Bull 250ml - BEB004

**Snacks:**
- Sabritas Originales - SNK001
- Doritos Nacho - SNK002
- Barritas de Granola - SNK003
- Almendras Saladas - SNK004

**Accesorios:**
- Toalla Deportiva - ACC001
- Guantes Gym M - ACC002
- Shaker 700ml - ACC003
- Banda Elástica - ACC004

### 💊 Suplementos (10 items)
- Whey Protein Gold Standard - SUP001
- Creatina Monohidratada - SUP002
- Pre Workout C4 Original - SUP003
- BCAA Powder 5000 - SUP004
- Glutamina Powder - SUP005
- Proteína Vegana - SUP006
- Quemador Hydroxycut - SUP007
- Mass Gainer Serious - SUP008
- Multivitamínico Opti-Men - SUP009
- ZMA Capsulas - SUP010

### 📊 Estadísticas
- **77** registros de acceso (últimos 7 días)
- **16** ventas (últimos 3 días)
- **35** items vendidos
- **26** productos en inventario

## 🔐 Credenciales de Acceso

**Usuario:** admin  
**Contraseña:** admin123

## 🚀 Cómo Ejecutar la Demo

### Opción 1: Ejecutable (Recomendado)
1. Navega a la carpeta `dist/`
2. Doble clic en `HTF_Gimnasio_POS.exe`
3. Inicia sesión con las credenciales

### Opción 2: Código Fuente
```powershell
cd POS_HTF
python main.py
```

## 🎪 Flujo de Demostración Sugerido

### 1️⃣ Login
- Muestra la pantalla de login estilo Windows Phone
- Ingresa credenciales de admin

### 2️⃣ Dashboard
- Visualiza las estadísticas del día
- Muestra totales de ventas e ingresos

### 3️⃣ Registrar Acceso de Miembro
- Ve a la pestaña **Miembros**
- Clic en **Registrar Acceso**
- Ingresa código: **MIEMBRO001** o **1** (ID)
- Verifica que se muestre la foto y datos del miembro
- Confirma el acceso

### 4️⃣ Nueva Venta
- Ve a la pestaña **Ventas**
- Clic en **Nueva Venta**
- Busca productos por código o escaneo
- Ejemplo: **BEB001** (Coca Cola), **SNK001** (Sabritas)
- Completa la venta

### 5️⃣ Agregar Producto
- Ve a la pestaña **Inventario**
- Clic en **Nuevo Producto**
- Selecciona tipo (Producto Varios o Suplemento)
- Llena el formulario con datos de prueba
- Guarda el producto

### 6️⃣ Historial
- **Historial de Acceso:** Ver entradas de miembros
- **Historial de Ventas:** Ver ventas realizadas
- **Movimientos de Inventario:** Ver cambios en stock

## 🎨 Características a Destacar

✨ **Interfaz Windows Phone Style**
- Tiles interactivos
- Colores corporativos
- Animaciones suaves

📱 **Gestión de Miembros**
- Registro de acceso con foto
- Historial de visitas
- Búsqueda por QR o ID

💰 **Sistema de Ventas**
- Búsqueda rápida de productos
- Múltiples métodos de pago
- Ticket de venta

📦 **Control de Inventario**
- Productos varios y suplementos
- Alertas de stock bajo
- Movimientos de entrada/salida

## 📝 Notas Importantes

1. **Base de Datos:** Los datos se almacenan en `database/pos_htf.db`
2. **Modo Offline:** Funciona completamente sin internet
3. **Sincronización:** Preparado para sincronizar con Supabase (opcional)

## 🔧 Regenerar Datos de Prueba

Si necesitas limpiar y volver a crear los datos:

```powershell
# Eliminar base de datos actual
rm database\pos_htf.db

# Regenerar con datos frescos
python insertar_datos_prueba.py
```

## 📞 Soporte

Para cualquier problema durante la demo, verifica:
- Que el archivo `.env` esté presente (si usas Supabase)
- Que la base de datos exista en `database/pos_htf.db`
- Logs en consola si ejecutas desde código fuente

---

**¡La demo está lista para mostrar! 🎉**
