# 📦 Distribución del Ejecutable POS HTF

## ✅ Estado actual
El archivo ejecutable ha sido generado exitosamente:
- **Ubicación**: `dist/HTF_Gimnasio_POS/`
- **Archivo principal**: `HTF_Gimnasio_POS.exe`
- **Tamaño**: ~13.4 MB
- **Dependencias**: Todas incluidas en la carpeta

## 📋 Requisitos para ejecutar

### Opción 1: En Windows con Python (RECOMENDADO PARA DESARROLLO)
```bash
# Ejecutar directamente desde el proyecto
python main.py
```

### Opción 2: Ejecutable independiente (SIN Python necesario)
```bash
# Ir a la carpeta
cd dist/HTF_Gimnasio_POS/

# Ejecutar el .exe
HTF_Gimnasio_POS.exe
```

## 🔑 Archivo de configuración (.env)

El ejecutable requiere un archivo `.env` en el mismo directorio con las credenciales:

```env
# En dist/HTF_Gimnasio_POS/.env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-anon-key
DATABASE_URL=postgresql://usuario:contraseña@host:5432/basedatos
```

**IMPORTANTE**: 
- Si `.env` no existe, la aplicación intentará funcionar en modo offline
- Las credenciales son OBLIGATORIAS para acceder a la base de datos

## 📂 Estructura de distribución

```
HTF_Gimnasio_POS/
├── HTF_Gimnasio_POS.exe    (Aplicación principal)
├── .env                     (Configuración - CREAR ANTES DE USAR)
├── pos_htf.log             (Se genera automáticamente)
└── _internal/              (Bibliotecas y dependencias)
```

## 🚀 Cómo usar

### Para los usuarios finales:
1. Copiar la carpeta completa `dist/HTF_Gimnasio_POS/` a donde se desee
2. Crear archivo `.env` en esa carpeta con las credenciales
3. Hacer doble clic en `HTF_Gimnasio_POS.exe`

### Para distribución:
```bash
# La carpeta dist/HTF_Gimnasio_POS/ es auto-contenida
# Se puede distribuir como:
# - Carpeta comprimida (.zip)
# - Instalador (requiere NSIS o similar)
# - Copiar directamente a máquinas
```

## ⚠️ Posibles problemas y soluciones

### ❌ La aplicación se cierra inmediatamente
- Verificar que `.env` existe y tiene valores válidos
- Revisar el archivo `pos_htf.log` para errores
- Asegurar conexión a Supabase/Base de datos

### ❌ Error "Cannot find module..."
- Los módulos están incluidos en `_internal/`
- NO borrar esta carpeta

### ❌ Error de conexión a BD
- Verificar credenciales en `.env`
- Verificar conectividad de red
- Aplicación continúa en modo offline con funciones limitadas

### ❌ Puerto 5432 en uso
- Si PostgreSQL local está en otro puerto, actualizar `DATABASE_URL`
- Verificar con: `netstat -ano | findstr :5432`

## 📝 Logs y depuración

Todos los eventos se registran en `pos_htf.log`:
```bash
# Ver últimas líneas del log en PowerShell
Get-Content pos_htf.log -Tail 20

# O en CMD
type pos_htf.log
```

## 🔄 Actualizar el ejecutable

Si hay cambios en el código:
```bash
# En el directorio del proyecto
python build_onedir.py

# O
pyinstaller --onedir --windowed --name HTF_Gimnasio_POS main.py
```

## 📊 Información técnica

- **Framework**: PySide6 (Qt para Python)
- **BD Primaria**: Supabase (PostgreSQL en cloud)
- **BD Local**: SQLite (para modo offline)
- **Python**: 3.12.8
- **Modo**: GUI Windows, sin consola

## ✨ Características

- ✅ Ejecutable independiente (no requiere Python instalado)
- ✅ Interfaz gráfica moderna con PySide6
- ✅ Sincronización Supabase/Offline
- ✅ Código QR para productos
- ✅ Gestión completa de inventario
- ✅ Ventas y reportes
- ✅ Gestión de usuarios

## 🎯 Próximos pasos

1. ✅ Generar archivo `.env` con credenciales
2. ✅ Probar ejecutable en máquina limpia
3. ✅ Crear instalador (opcional, con NSIS)
4. ✅ Distribuir a usuarios finales
5. ✅ Establecer proceso de actualizaciones
