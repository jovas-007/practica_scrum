"""
Configuración del admin de Django para usuarios
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, RecoveryCode, EmailLog


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


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    """Admin para bitácora de emails"""
    
    list_display = ['fecha_envio', 'destinatario', 'tipo', 'asunto_corto', 'estado', 'brevo_message_id']
    list_filter = ['tipo', 'estado', 'fecha_envio']
    search_fields = ['destinatario', 'asunto', 'brevo_message_id']
    readonly_fields = ['fecha_envio', 'destinatario', 'asunto', 'tipo', 'estado', 'mensaje_error', 'brevo_message_id']
    date_hierarchy = 'fecha_envio'
    
    def asunto_corto(self, obj):
        """Mostrar asunto truncado"""
        return obj.asunto[:50] + '...' if len(obj.asunto) > 50 else obj.asunto
    asunto_corto.short_description = 'Asunto'
    
    def has_add_permission(self, request):
        """No permitir agregar registros manualmente"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """No permitir editar registros"""
        return False
