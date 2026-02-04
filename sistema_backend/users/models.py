"""
Modelo de Usuario personalizado para el Sistema de Gestión de Tareas
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """Manager personalizado para el modelo User"""
    
    def create_user(self, id_usuario, correo, password=None, **extra_fields):
        """Crear y guardar un usuario regular"""
        if not id_usuario:
            raise ValueError('El usuario debe tener un ID/Matrícula')
        if not correo:
            raise ValueError('El usuario debe tener un correo electrónico')
        
        correo = self.normalize_email(correo)
        user = self.model(id_usuario=id_usuario, correo=correo, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, id_usuario, correo, password=None, **extra_fields):
        """Crear y guardar un superusuario"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('rol', 'docente')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')
        
        return self.create_user(id_usuario, correo, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de Usuario personalizado que usa id_usuario (matrícula) como identificador único
    """
    
    class Rol(models.TextChoices):
        DOCENTE = 'docente', 'Docente'
        ESTUDIANTE = 'estudiante', 'Estudiante'
    
    class Sexo(models.TextChoices):
        MASCULINO = 'Masculino', 'Masculino'
        FEMENINO = 'Femenino', 'Femenino'
        OTRO = 'Otro', 'Otro'
    
    id_usuario = models.CharField(
        max_length=50,
        unique=True,
        primary_key=True,
        verbose_name='Matrícula/ID'
    )
    correo = models.EmailField(
        unique=True,
        verbose_name='Correo electrónico'
    )
    nombre_completo = models.CharField(
        max_length=150,
        verbose_name='Nombre completo'
    )
    telefono = models.CharField(
        max_length=15,
        blank=True,
        verbose_name='Teléfono'
    )
    sexo = models.CharField(
        max_length=10,
        choices=Sexo.choices,
        default=Sexo.OTRO,
        verbose_name='Sexo'
    )
    carrera = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Carrera'
    )
    rol = models.CharField(
        max_length=15,
        choices=Rol.choices,
        default=Rol.ESTUDIANTE,
        verbose_name='Rol'
    )
    
    # Campos requeridos por Django
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'id_usuario'
    REQUIRED_FIELDS = ['correo', 'nombre_completo']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.id_usuario} - {self.nombre_completo}"
    
    def get_full_name(self):
        return self.nombre_completo
    
    def get_short_name(self):
        return self.nombre_completo.split()[0] if self.nombre_completo else self.id_usuario


class RecoveryCode(models.Model):
    """
    Modelo para almacenar códigos de recuperación de contraseña
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recovery_codes'
    )
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'recovery_codes'
        verbose_name = 'Código de recuperación'
        verbose_name_plural = 'Códigos de recuperación'
    
    def __str__(self):
        return f"Código para {self.user.correo}"
