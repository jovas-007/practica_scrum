"""
Configuración del admin de Django para usuarios
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, RecoveryCode


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin personalizado para el modelo User"""
    
    list_display = ['id_usuario', 'nombre_completo', 'correo', 'rol', 'is_active']
    list_filter = ['rol', 'is_active', 'sexo', 'carrera']
    search_fields = ['id_usuario', 'nombre_completo', 'correo']
    ordering = ['id_usuario']
    
    fieldsets = (
        (None, {'fields': ('id_usuario', 'password')}),
        ('Información Personal', {'fields': ('nombre_completo', 'correo', 'telefono', 'sexo', 'carrera')}),
        ('Rol y Permisos', {'fields': ('rol', 'is_active', 'is_staff', 'is_superuser')}),
        ('Fechas', {'fields': ('date_joined', 'last_login')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('id_usuario', 'correo', 'nombre_completo', 'password1', 'password2', 'rol'),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']


@admin.register(RecoveryCode)
class RecoveryCodeAdmin(admin.ModelAdmin):
    """Admin para códigos de recuperación"""
    
    list_display = ['user', 'code', 'created_at', 'expires_at', 'used']
    list_filter = ['used', 'created_at']
    search_fields = ['user__correo', 'code']
