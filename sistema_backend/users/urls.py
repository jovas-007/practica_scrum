"""
URLs para la API de usuarios
"""
from django.urls import path
from . import views

urlpatterns = [
    # Autenticación
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    
    # Recuperación de contraseña (nombres que usa el frontend)
    path('forgot-password', views.forgot_password, name='forgot-password'),
    path('verify-recovery-code', views.verify_code, name='verify-recovery-code'),
    path('reset-password', views.reset_password, name='reset-password'),
    
    # Usuarios
    path('users', views.get_users, name='get-users'),
    path('users/materias', views.update_materias, name='update-materias'),
    
    # Materias
    path('materias', views.get_materias_disponibles, name='get-materias'),
    
    # Email / Recordatorios
    path('test-reminders', views.test_reminders, name='test-reminders'),
    path('test-reminders/', views.test_reminders),
    path('test-smtp', views.test_smtp, name='test-smtp'),
    path('test-smtp/', views.test_smtp),
]
