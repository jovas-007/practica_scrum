"""
URL configuration for Sistema de Gestión de Tareas
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve
from django.http import FileResponse
import os

# Ruta base del proyecto practica_scrum (padre de sistema_backend)
BASE_PROJECT_DIR = os.path.dirname(settings.BASE_DIR)

def serve_src_file(request, path):
    """Servir archivos estáticos desde la carpeta src del proyecto principal"""
    file_path = os.path.join(BASE_PROJECT_DIR, 'src', path)
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'))
    from django.http import Http404
    raise Http404(f"Archivo no encontrado: {path}")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    
    # Servir archivos estáticos desde /src (compatibilidad con frontend)
    re_path(r'^src/(?P<path>.*)$', serve_src_file),
]
