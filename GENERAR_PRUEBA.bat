@echo off
REM Script para generar datos de prueba rápidamente
REM Uso: generador_prueba.bat [cantidad_visitas] [cantidad_codigos]

echo.
echo ===============================================
echo  GENERADOR DE DATOS DE PRUEBA - FLUJO POS HTF
echo ===============================================
echo.

REM Valores por defecto
set VISITAS=5
set CODIGOS=3

REM Permitir argumentos
if not "%~1"=="" set VISITAS=%~1
if not "%~2"=="" set CODIGOS=%~2

echo Parametros:
echo - Visitas a generar: %VISITAS%
echo - Codigos de pago: %CODIGOS%
echo.

REM Ejecutar el script Python
cd /d "%~dp0"
python test_generar_prueba_flujo.py

echo.
pause
