@echo off
echo ========================================
echo  Sistema de Tareas - Backend Django
echo ========================================
echo.

cd /d "%~dp0"

echo Activando entorno virtual...
call venv\Scripts\activate.bat

echo.
echo Iniciando servidor en http://127.0.0.1:3000/
echo Presiona Ctrl+C para detener
echo.

python manage.py runserver 3000
