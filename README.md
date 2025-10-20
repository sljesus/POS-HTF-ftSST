# HTF Gimnasio - Sistema POS

Sistema de Punto de Venta para HTF Gimnasio con capacidades offline y sincronización con Supabase.

## Características

- ✅ Sistema de login seguro
- ✅ Base de datos SQLite local para funcionamiento offline
- ✅ Sincronización con Supabase (opcional)
- ✅ Gestión de inventario
- ✅ Procesamiento de ventas
- ✅ Interfaz gráfica con Tkinter

## Estructura del Proyecto

```
POS_HTF/
├── main.py              # Aplicación principal
├── requirements.txt     # Dependencias
├── .env.example        # Ejemplo de variables de entorno
├── database/
│   ├── __init__.py
│   ├── db_manager.py   # Gestor de base de datos SQLite
│   └── pos_htf.db      # Base de datos (se crea automáticamente)
├── ui/
│   ├── __init__.py
│   └── login_window.py # Ventana de login
├── services/
│   ├── __init__.py
│   └── supabase_service.py # Servicio de sincronización
├── utils/
│   ├── __init__.py
│   └── config.py       # Configuración de la aplicación
└── assets/             # Recursos (iconos, imágenes)
```

## Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Configurar variables de entorno (opcional):
```bash
copy .env.example .env
# Editar .env con tus credenciales de Supabase
```

3. Ejecutar la aplicación:
```bash
python main.py
```

## Usuario por Defecto

- **Usuario:** admin
- **Contraseña:** admin123

## Funcionalidades Implementadas

### ✅ Sistema de Login
- Autenticación local con SQLite
- Hash seguro de contraseñas
- Manejo de sesiones
- Indicador de estado de conexión

### ✅ Base de Datos Local
- Tablas: users, products, sales, sale_items, sync_log
- Usuario administrador por defecto
- Gestión de inventario offline

### ✅ Sincronización (En desarrollo)
- Conexión a Supabase
- Sincronización bidireccional de datos
- Modo offline completo

## Próximos Pasos

1. Implementar ventana principal del POS
2. Módulo de ventas
3. Gestión de inventario
4. Reportes
5. Configuración avanzada
6. Empaquetado como ejecutable