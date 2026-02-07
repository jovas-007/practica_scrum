"""
Modelo de Usuario personalizado para el Sistema de Gestión de Tareas
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class Materia(models.Model):
    """
    Modelo para representar las materias/asignaturas disponibles
    """
    codigo = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Código de materia'
    )
    nombre = models.CharField(
        max_length=200,
        verbose_name='Nombre de la materia'
    )
    nrc = models.CharField(
        max_length=10,
        verbose_name='NRC'
    )
    carreras_permitidas = models.JSONField(
        default=list,
        verbose_name='Carreras que pueden cursar esta materia'
    )
    
    class Meta:
        db_table = 'materias'
        verbose_name = 'Materia'
        verbose_name_plural = 'Materias'
    
    def __str__(self):
        return f"{self.nombre} — NRC: {self.nrc}"
    
    @staticmethod
    def get_materias_por_carrera(carrera_codigo):
        """
        Retorna las materias disponibles para una carrera específica
        Compatible con SQLite y MySQL/PostgreSQL
        """
        from django.db import connection
        
        # Verificar si estamos usando SQLite
        if 'sqlite' in connection.vendor:
            # Para SQLite: filtrar manualmente usando Python
            todas_materias = list(Materia.objects.all())
            return [m for m in todas_materias if carrera_codigo in m.carreras_permitidas]
        else:
            # Para MySQL/PostgreSQL: usar contains
            return Materia.objects.filter(carreras_permitidas__contains=[carrera_codigo])


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
    
    class Carrera(models.TextChoices):
        ICC = 'ICC', 'Ingeniería en Cs. de la Computación'
        LCC = 'LCC', 'Licenciatura en Cs. de la Computación'
        ITI = 'ITI', 'Ingeniería en Tecnologías de la Información'
    
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
        max_length=10,
        choices=Carrera.choices,
        blank=True,
        verbose_name='Carrera'
    )
    rol = models.CharField(
        max_length=15,
        choices=Rol.choices,
        default=Rol.ESTUDIANTE,
        verbose_name='Rol'
    )
    
    # Relaciones con materias según el rol
    materias_estudiante = models.ManyToManyField(
        Materia,
        blank=True,
        related_name='estudiantes',
        verbose_name='Materias del estudiante'
    )
    materias_docente = models.ManyToManyField(
        Materia,
        blank=True,
        related_name='docentes',
        verbose_name='Materias que imparte el docente'
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


class EmailLog(models.Model):
    """
    Modelo para registrar todos los emails enviados por el sistema
    """
    class TipoEmail(models.TextChoices):
        RECOVERY_CODE = 'recovery_code', 'Código de Recuperación'
        TASK_ASSIGNED = 'task_assigned', 'Tarea Asignada'
        SUBMISSION_RECEIVED = 'submission_received', 'Entrega Recibida'
        TASK_GRADED = 'task_graded', 'Tarea Calificada'
        TASK_REMINDER = 'task_reminder', 'Recordatorio de Tarea'
        WELCOME = 'welcome', 'Bienvenida'
    
    class Estado(models.TextChoices):
        ENVIADO = 'enviado', 'Enviado'
        FALLIDO = 'fallido', 'Fallido'
    
    destinatario = models.EmailField(verbose_name='Correo destinatario')
    asunto = models.CharField(max_length=255, verbose_name='Asunto del email')
    tipo = models.CharField(
        max_length=50,
        choices=TipoEmail.choices,
        verbose_name='Tipo de email'
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.ENVIADO,
        verbose_name='Estado del envío'
    )
    mensaje_error = models.TextField(
        blank=True,
        null=True,
        verbose_name='Mensaje de error (si falló)'
    )
    fecha_envio = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha y hora de envío'
    )
    brevo_message_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='ID del mensaje en Brevo'
    )
    
    class Meta:
        db_table = 'email_logs'
        verbose_name = 'Registro de Email'
        verbose_name_plural = 'Registros de Emails'
        ordering = ['-fecha_envio']
        indexes = [
            models.Index(fields=['-fecha_envio']),
            models.Index(fields=['destinatario']),
            models.Index(fields=['tipo']),
            models.Index(fields=['estado']),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_display()} → {self.destinatario} ({self.estado})"
