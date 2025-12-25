# Plan de Refactorización - HTF POS

## FASE 1: Organización del Root (KISS - Keep It Simple)

### Problemas Identificados:

**Archivos Temporales/Logs (Eliminar o mover a carpeta apropiada):**
- `tmpp0rsgw1e.txt` - Temporal, eliminar
- `tmpztx_ky8j.txt` - Temporal, eliminar  
- `pos_htf.log` - Mover a `logs/` o agregar a `.gitignore`
- `test_sync_output.log` - Mover a `logs/` o eliminar si es temporal

**Build Artifacts (Mover a carpeta `build/` o agregar a `.gitignore`):**
- `build_app/` - Build artifacts, agregar a `.gitignore`
- `build_distribucion.py` - Script de build, mover a `scripts/build/`
- `build_exe.py` - Script de build, mover a `scripts/build/`
- `build_onedir.py` - Script de build, mover a `scripts/build/`
- `build_simple.py` - Script de build, mover a `scripts/build/`
- `build.log` - Log de build, agregar a `.gitignore`
- `convert_icon.py` - Script de utilidad, mover a `scripts/utils/`

**Scripts de Una Sola Vez (Mover a `scripts/legacy/` o eliminar):**
- `agregar_id_turno_ventas.py` - Script específico, mover a `scripts/legacy/`
- `test_abrir_turno.py` - Test script, mover a `tests/` o `scripts/test/`

**Documentación (Organizar en `docs/`):**
- `DOCUMENTACION_TECNICA.md` - Mover a `docs/`
- `INTEGRACION_IMPRESORA_ESCPOS.md` - Mover a `docs/`
- `GUIA_USUARIO_IMPRESORA.txt` - Mover a `docs/`
- `RESUMEN_INTEGRACION.txt` - Mover a `docs/`
- `TABLA_COMPARATIVA.txt` - Mover a `docs/`
- `README.md` - Mantener en root (estándar)

**Módulos en Root (Mover a carpetas apropiadas):**
- `escpos_printer.py` - Mover a `services/printers/`
- `windows_printer_manager.py` - Mover a `services/printers/`

**Archivos a Mantener en Root:**
- `main.py` - Punto de entrada principal
- `requirements.txt` - Dependencias (estándar)
- `README.md` - Documentación principal (estándar)
- `.env` - Variables de entorno (agregar a `.gitignore` si no está)
- `setup_postgres_trigger.sql` - Script SQL, puede ir en `database/sql/` o mantener en root

### Estructura Propuesta del Root:

```
POS-HTF/
├── main.py                    # Punto de entrada
├── requirements.txt           # Dependencias
├── README.md                  # Documentación principal
├── .env                       # Variables de entorno (gitignored)
├── .gitignore                 # Archivos ignorados
│
├── database/                  # Gestión de base de datos
│   ├── sql/                   # Scripts SQL
│   │   └── setup_postgres_trigger.sql
│   └── ...
│
├── docs/                      # Documentación
│   ├── DOCUMENTACION_TECNICA.md
│   ├── INTEGRACION_IMPRESORA_ESCPOS.md
│   └── ...
│
├── services/                  # Servicios
│   ├── printers/              # Servicios de impresión
│   │   ├── escpos_printer.py
│   │   └── windows_printer_manager.py
│   └── ...
│
├── scripts/                   # Scripts utilitarios
│   ├── build/                 # Scripts de build
│   ├── utils/                 # Utilidades
│   ├── test/                  # Scripts de test
│   └── legacy/                # Scripts antiguos
│
├── logs/                      # Logs (gitignored)
│
├── build/                     # Build artifacts (gitignored)
│
└── [resto de carpetas existentes]
```

## FASE 2: Refactorización SOLID

### Violaciones Principales:

**1. PostgresManager - Violación de Single Responsibility Principle (SRP)**
- Clase con ~1823 líneas
- Múltiples responsabilidades:
  - Conexión a BD
  - Autenticación
  - Gestión de productos
  - Gestión de ventas
  - Gestión de inventario
  - Gestión de miembros
  - Gestión de turnos
  - Gestión de lockers
  - Notificaciones

**Refactorización Propuesta:**

```
database/
├── managers/
│   ├── base_manager.py        # Clase base con conexión
│   ├── auth_manager.py        # Autenticación
│   ├── product_manager.py     # Productos
│   ├── sale_manager.py        # Ventas
│   ├── inventory_manager.py   # Inventario
│   ├── member_manager.py      # Miembros
│   ├── shift_manager.py       # Turnos
│   └── locker_manager.py      # Lockers
│
└── postgres_manager.py        # Facade/Orchestrator (deprecar gradualmente)
```

**Principios a Aplicar:**
- **SRP**: Cada clase una sola responsabilidad
- **OCP**: Abrir para extensión, cerrar para modificación
- **DIP**: Depender de abstracciones, no de implementaciones concretas
- **KISS**: Mantener simple, no sobre-ingeniería

### Plan de Implementación:

1. Crear estructura de carpetas
2. Crear clase base `BaseManager` con conexión común
3. Extraer cada responsabilidad a su propio manager
4. Mantener `PostgresManager` como facade para compatibilidad
5. Migrar gradualmente el código para usar los nuevos managers
6. Deprecar `PostgresManager` cuando todo esté migrado

## FASE 3: Mejoras de KISS

### Simplificaciones:

1. **Eliminar duplicación**: Consolidar métodos similares
2. **Reducir complejidad**: Simplificar métodos largos
3. **Mejorar nombres**: Nombres más descriptivos y claros
4. **Eliminar código muerto**: Remover código comentado o no usado
5. **Consolidar imports**: Organizar imports mejor

## Orden de Ejecución Recomendado:

1. ✅ **Análisis** (COMPLETADO)
2. ⏭️ **Fase 1**: Organizar root (NO destructivo, fácil de revertir)
3. ⏭️ **Fase 2**: Refactorización SOLID (requiere más cuidado)
4. ⏭️ **Fase 3**: Mejoras KISS (iterativo)

