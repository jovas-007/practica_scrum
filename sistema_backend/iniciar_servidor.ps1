# Script para iniciar el servidor Django con entorno virtual
# Ejecutar: .\iniciar_servidor.ps1

Write-Host "========================================"
Write-Host "  Sistema de Tareas - Backend Django"
Write-Host "========================================"
Write-Host ""

# Navegar al directorio del script
Set-Location $PSScriptRoot

# Activar entorno virtual
Write-Host "Activando entorno virtual..."
& ".\venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "Iniciando servidor en http://127.0.0.1:3000/"
Write-Host "Presiona Ctrl+C para detener"
Write-Host ""

# Iniciar servidor
python manage.py runserver 3000
