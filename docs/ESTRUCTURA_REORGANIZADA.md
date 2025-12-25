# Estructura del Proyecto Reorganizada

## Cambios Realizados

### ✅ Documentación → `docs/`
- `DOCUMENTACION_TECNICA.md`
- `INTEGRACION_IMPRESORA_ESCPOS.md`
- `GUIA_USUARIO_IMPRESORA.txt`
- `RESUMEN_INTEGRACION.txt`
- `TABLA_COMPARATIVA.txt`

### ✅ Scripts de Build → `scripts/build/`
- `build_distribucion.py`
- `build_exe.py`
- `build_onedir.py`
- `build_simple.py`

### ✅ Scripts Utilitarios → `scripts/utils/`
- `convert_icon.py`

### ✅ Scripts Legacy → `scripts/legacy/`
- `agregar_id_turno_ventas.py`

### ✅ Scripts de Test → `scripts/test/`
- `test_abrir_turno.py`

### ✅ Servicios de Impresión → `services/printers/`
- `escpos_printer.py`
- `windows_printer_manager.py`

### ✅ Scripts SQL → `database/sql/`
- `setup_postgres_trigger.sql`

## Archivos en Root (Mantenidos)

### Archivos Principales
- `main.py` - Punto de entrada
- `requirements.txt` - Dependencias
- `README.md` - Documentación principal
- `.gitignore` - Configuración Git (actualizado para ser más permisivo)

### Archivos de Configuración
- `INICIAR_DEMO.bat` - Script de inicio rápido

### Archivos Temporales/Logs (Permanecen en root para backup en git)
- `pos_htf.log` - Log de la aplicación
- `test_sync_output.log` - Log de sincronización
- `build.log` - Log de builds
- `tmpp0rsgw1e.txt` - Archivo temporal
- `tmpztx_ky8j.txt` - Archivo temporal

### Build Artifacts (Permanecen para backup en git)
- `build_app/` - Artifacts de build
- `dist_app/` - Distribuciones
- `spec_app/` - Especificaciones PyInstaller

## Estructura Final

```
POS-HTF/
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
├── REFACTORIZACION_PLAN.md
│
├── docs/                      # 📚 Documentación
│   ├── DOCUMENTACION_TECNICA.md
│   ├── INTEGRACION_IMPRESORA_ESCPOS.md
│   └── ...
│
├── database/                  # 💾 Base de datos
│   └── sql/
│       └── setup_postgres_trigger.sql
│
├── services/                  # 🔧 Servicios
│   └── printers/
│       ├── escpos_printer.py
│       └── windows_printer_manager.py
│
├── scripts/                   # 📜 Scripts
│   ├── build/
│   ├── utils/
│   ├── legacy/
│   └── test/
│
├── ui/                        # 🖥️ Interfaz de usuario
├── utils/                     # 🛠️ Utilidades
└── [otros archivos]
```

## Imports Actualizados

- ✅ `ui/ventas/nueva_venta.py` - Actualizado para usar `services.printers.*`
- ✅ `docs/DOCUMENTACION_TECNICA.md` - Actualizado referencia de import

## Configuración .gitignore

El `.gitignore` ahora es más permisivo (estilo junior) para no perder nada:
- ❌ Solo ignora: `.env`, `__pycache__/`, archivos del sistema
- ✅ Permite subir: logs, builds, temporales, ejecutables, etc.

Esto asegura que todo esté respaldado en git en caso de resetear la computadora.

