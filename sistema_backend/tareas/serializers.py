from rest_framework import serializers
from django.utils import timezone
from .models import Task, Submission, SubmissionFile
from users.models import User


class SubmissionFileSerializer(serializers.ModelSerializer):
    """Serializer para archivos de entrega"""
    
    class Meta:
        model = SubmissionFile
        fields = ['id', 'archivo', 'nombre_original', 'fecha_subida', 'es_entrega_tardia']
        read_only_fields = ['id', 'nombre_original', 'fecha_subida', 'es_entrega_tardia']


class StudentBasicSerializer(serializers.ModelSerializer):
    """Serializer básico de estudiante para listados"""
    
    class Meta:
        model = User
        fields = ['id_usuario', 'nombre_completo', 'correo', 'carrera']


class SubmissionListSerializer(serializers.ModelSerializer):
    """Serializer para listar entregas (vista docente)"""
    
    student = StudentBasicSerializer(read_only=True)
    archivos = SubmissionFileSerializer(many=True, read_only=True)
    tiene_entregas = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Submission
        fields = [
            'id', 'student', 'estado', 'fecha_creacion',
            'calificacion', 'comentario_docente', 'fecha_calificacion',
            'archivos', 'tiene_entregas'
        ]


class SubmissionStudentSerializer(serializers.ModelSerializer):
    """Serializer para entregas (vista estudiante)"""
    
    archivos = SubmissionFileSerializer(many=True, read_only=True)
    task_id = serializers.IntegerField(source='task.id', read_only=True)
    tarea_titulo = serializers.CharField(source='task.titulo', read_only=True)
    tarea_descripcion = serializers.CharField(source='task.descripcion', read_only=True)
    tarea_fecha_entrega = serializers.DateTimeField(source='task.fecha_entrega', read_only=True)
    tarea_puntos_maximos = serializers.IntegerField(source='task.puntos_maximos', read_only=True)
    tarea_archivo_adjunto = serializers.FileField(source='task.archivo_adjunto', read_only=True)
    tarea_url_recurso = serializers.URLField(source='task.url_recurso', read_only=True)
    tarea_esta_vencida = serializers.BooleanField(source='task.esta_vencida', read_only=True)
    puede_entregar = serializers.SerializerMethodField()
    
    class Meta:
        model = Submission
        fields = [
            'id', 'task_id', 'estado', 'fecha_creacion',
            'calificacion', 'comentario_docente', 'fecha_calificacion',
            'archivos', 'tarea_titulo', 'tarea_descripcion', 'tarea_fecha_entrega',
            'tarea_puntos_maximos', 'tarea_archivo_adjunto', 'tarea_url_recurso',
            'tarea_esta_vencida', 'puede_entregar'
        ]
    
    def get_puede_entregar(self, obj):
        return obj.task.puede_recibir_entregas


class TaskListSerializer(serializers.ModelSerializer):
    """Serializer para listar tareas (vista docente)"""
    
    docente_nombre = serializers.CharField(source='docente.nombre_completo', read_only=True)
    total_estudiantes = serializers.SerializerMethodField()
    total_entregados = serializers.SerializerMethodField()
    total_calificados = serializers.SerializerMethodField()
    esta_vencida = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'titulo', 'descripcion', 'archivo_adjunto', 'url_recurso',
            'fecha_creacion', 'fecha_modificacion', 'fecha_entrega',
            'docente_nombre', 'estado', 'puntos_maximos', 'permite_tardias',
            'esta_vencida', 'total_estudiantes', 'total_entregados', 'total_calificados'
        ]
    
    def get_total_estudiantes(self, obj):
        return obj.submissions.count()
    
    def get_total_entregados(self, obj):
        return obj.submissions.filter(estado__in=['entregado', 'calificado']).count()
    
    def get_total_calificados(self, obj):
        return obj.submissions.filter(estado='calificado').count()


class TaskCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear/editar tareas"""
    
    class Meta:
        model = Task
        fields = [
            'titulo', 'descripcion', 'archivo_adjunto', 'url_recurso',
            'fecha_entrega', 'puntos_maximos', 'permite_tardias'
        ]
    
    def validate_fecha_entrega(self, value):
        """La fecha de entrega debe ser futura"""
        if value <= timezone.now():
            raise serializers.ValidationError('La fecha de entrega debe ser futura')
        return value
    
    def validate_titulo(self, value):
        """El título no puede estar vacío"""
        if not value.strip():
            raise serializers.ValidationError('El título es requerido')
        return value.strip()


class TaskDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado de tarea con submissions"""
    
    docente_nombre = serializers.CharField(source='docente.nombre_completo', read_only=True)
    submissions = SubmissionListSerializer(many=True, read_only=True)
    esta_vencida = serializers.BooleanField(read_only=True)
    puede_recibir_entregas = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'titulo', 'descripcion', 'archivo_adjunto', 'url_recurso',
            'fecha_creacion', 'fecha_modificacion', 'fecha_entrega',
            'docente_nombre', 'estado', 'puntos_maximos', 'permite_tardias',
            'esta_vencida', 'puede_recibir_entregas', 'submissions'
        ]


class GradeSubmissionSerializer(serializers.Serializer):
    """Serializer para calificar una entrega"""
    
    calificacion = serializers.IntegerField(min_value=1, max_value=10)
    comentario_docente = serializers.CharField(required=False, allow_blank=True, default='')
    
    def validate_calificacion(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError('La calificación debe estar entre 1 y 10')
        return value


class SubmitFileSerializer(serializers.Serializer):
    """Serializer para subir archivos de entrega"""
    
    archivos = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=False,
        max_length=10  # Máximo 10 archivos por entrega
    )
    
    def validate_archivos(self, value):
        """Validar tamaño y extensión de archivos"""
        allowed_extensions = [
            'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
            'jpg', 'jpeg', 'png', 'gif', 'zip', 'rar', 'txt',
            'py', 'js', 'html', 'css', 'java', 'cpp', 'c'
        ]
        max_size = 20 * 1024 * 1024  # 20MB
        
        for archivo in value:
            # Verificar tamaño
            if archivo.size > max_size:
                raise serializers.ValidationError(
                    f'El archivo {archivo.name} excede el límite de 20MB'
                )
            
            # Verificar extensión
            ext = archivo.name.split('.')[-1].lower() if '.' in archivo.name else ''
            if ext not in allowed_extensions:
                raise serializers.ValidationError(
                    f'Extensión no permitida: {ext}. Permitidas: {", ".join(allowed_extensions)}'
                )
        
        return value


class GradesReportSerializer(serializers.Serializer):
    """Serializer para reporte de calificaciones"""
    
    estudiante = StudentBasicSerializer()
    tareas = serializers.ListField()
    promedio = serializers.FloatField()
