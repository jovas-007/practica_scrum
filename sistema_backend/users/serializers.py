"""
Serializadores para la API de usuarios
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
import re
from .models import User, Materia


class MateriaSerializer(serializers.ModelSerializer):
    """Serializador para materias"""
    
    class Meta:
        model = Materia
        fields = ['id', 'codigo', 'nombre', 'nrc', 'carreras_permitidas']
        read_only_fields = ['id', 'codigo', 'nombre', 'nrc', 'carreras_permitidas']


class UserSerializer(serializers.ModelSerializer):
    """Serializador para mostrar datos de usuario"""
    materias = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id_usuario', 'nombre_completo', 'correo', 'telefono', 'sexo', 'carrera', 'rol', 'materias']
        read_only_fields = ['id_usuario']
    
    def get_materias(self, obj):
        """Obtener materias según el rol del usuario"""
        if obj.rol == 'estudiante':
            materias = obj.materias_estudiante.all()
        elif obj.rol == 'docente':
            materias = obj.materias_docente.all()
        else:
            materias = []
        return MateriaSerializer(materias, many=True).data


class RegisterSerializer(serializers.ModelSerializer):
    """Serializador para registro de usuarios"""
    
    password = serializers.CharField(write_only=True, min_length=8, max_length=20)
    nombre_completo = serializers.CharField(max_length=50, min_length=3)
    correo = serializers.EmailField(max_length=50)
    materias = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Materia.objects.all(),
        required=False
    )
    
    class Meta:
        model = User
        fields = ['id_usuario', 'password', 'nombre_completo', 'correo', 'telefono', 'sexo', 'carrera', 'rol', 'materias']
    
    def validate_password(self, value):
        """Validar que la contraseña tenga letra, número y símbolo"""
        if len(value) < 8 or len(value) > 20:
            raise serializers.ValidationError('La contraseña debe tener entre 8 y 20 caracteres')
        
        if not re.search(r'[a-zA-Z]', value):
            raise serializers.ValidationError('La contraseña debe contener al menos una letra')
        
        if not re.search(r'\d', value):
            raise serializers.ValidationError('La contraseña debe contener al menos un número')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/~`]', value):
            raise serializers.ValidationError('La contraseña debe contener al menos un símbolo especial')
        
        return value
    
    def validate_correo(self, value):
        """Validar formato de correo"""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, value):
            raise serializers.ValidationError('Formato de correo electrónico inválido')
        return value.lower()
    
    def validate_rol(self, value):
        """Validar que el rol sea válido"""
        if value not in ['docente', 'estudiante']:
            raise serializers.ValidationError('El rol debe ser "docente" o "estudiante"')
        return value
    
    def validate(self, data):
        """Validaciones adicionales a nivel de objeto"""
        rol = data.get('rol')
        carrera = data.get('carrera', '').strip()
        materias = data.get('materias', [])
        
        # Validar que la carrera sea requerida para estudiantes y docentes
        if not carrera:
            raise serializers.ValidationError({'carrera': 'La carrera es requerida'})
        
        # Validar que las materias correspondan a la carrera
        if materias:
            materias_permitidas = Materia.get_materias_por_carrera(carrera)
            # Convertir a lista si es queryset
            if hasattr(materias_permitidas, 'values_list'):
                materias_ids_permitidas = set(materias_permitidas.values_list('id', flat=True))
            else:
                # Es una lista de objetos
                materias_ids_permitidas = set(m.id for m in materias_permitidas)
            
            materias_ids_seleccionadas = set(m.id for m in materias)
            
            # Verificar que todas las materias seleccionadas sean válidas para la carrera
            if not materias_ids_seleccionadas.issubset(materias_ids_permitidas):
                raise serializers.ValidationError({
                    'materias': f'Las materias seleccionadas no corresponden a la carrera {carrera}'
                })
            
            # Validar que ITI solo pueda seleccionar 1 materia
            if carrera == 'ITI' and len(materias) > 1:
                raise serializers.ValidationError({
                    'materias': 'Para la carrera ITI solo puede seleccionar una materia'
                })
        
        return data
    
    def create(self, validated_data):
        """Crear usuario con contraseña hasheada"""
        materias = validated_data.pop('materias', [])
        
        user = User.objects.create_user(
            id_usuario=validated_data['id_usuario'],
            correo=validated_data['correo'],
            password=validated_data['password'],
            nombre_completo=validated_data['nombre_completo'],
            telefono=validated_data.get('telefono', ''),
            sexo=validated_data.get('sexo', 'Otro'),
            carrera=validated_data.get('carrera', ''),
            rol=validated_data.get('rol', 'estudiante'),
        )
        
        # Asignar materias según el rol
        if materias:
            if user.rol == 'estudiante':
                user.materias_estudiante.set(materias)
            elif user.rol == 'docente':
                user.materias_docente.set(materias)
        
        return user


class LoginSerializer(serializers.Serializer):
    """Serializador para login de usuarios"""
    
    id_usuario = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        import bcrypt
        
        id_usuario = data.get('id_usuario')
        password = data.get('password')
        
        # Buscar por matrícula o correo
        try:
            user = User.objects.get(id_usuario=id_usuario)
        except User.DoesNotExist:
            try:
                user = User.objects.get(correo__iexact=id_usuario)
            except User.DoesNotExist:
                raise serializers.ValidationError('Matrícula/Correo o contraseña incorrectos')
        
        # Verificar contraseña - soportar tanto bcrypt de Node.js como Django
        password_valid = False
        stored_password = user.password
        
        # Si es hash bcrypt de Node.js ($2b$, $2a$, $2y$)
        if stored_password.startswith('$2'):
            try:
                password_valid = bcrypt.checkpw(
                    password.encode('utf-8'),
                    stored_password.encode('utf-8')
                )
            except (ValueError, TypeError):
                password_valid = False
        else:
            # Hash de Django (PBKDF2, etc.)
            password_valid = user.check_password(password)
        
        if not password_valid:
            raise serializers.ValidationError('Matrícula/Correo o contraseña incorrectos')
        
        if not user.is_active:
            raise serializers.ValidationError('Esta cuenta está desactivada')
        
        data['user'] = user
        return data


class ForgotPasswordSerializer(serializers.Serializer):
    """Serializador para solicitar recuperación de contraseña"""
    
    correo = serializers.EmailField()
    
    def validate_correo(self, value):
        try:
            User.objects.get(correo__iexact=value)
        except User.DoesNotExist:
            raise serializers.ValidationError('No existe una cuenta con este correo electrónico')
        return value.lower()


class VerifyCodeSerializer(serializers.Serializer):
    """Serializador para verificar código de recuperación"""
    
    correo = serializers.EmailField()
    code = serializers.CharField(max_length=6, min_length=6)


class ResetPasswordSerializer(serializers.Serializer):
    """Serializador para restablecer contraseña"""
    
    correo = serializers.EmailField()
    code = serializers.CharField(max_length=6, min_length=6)
    new_password = serializers.CharField(min_length=8, max_length=20)
    
    def validate_new_password(self, value):
        """Validar que la nueva contraseña tenga letra, número y símbolo"""
        if not re.search(r'[a-zA-Z]', value):
            raise serializers.ValidationError('La contraseña debe contener al menos una letra')
        
        if not re.search(r'\d', value):
            raise serializers.ValidationError('La contraseña debe contener al menos un número')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/~`]', value):
            raise serializers.ValidationError('La contraseña debe contener al menos un símbolo especial')
        
        return value


class UpdateMateriasSerializer(serializers.Serializer):
    """Serializador para actualizar las materias de un usuario"""
    
    id_usuario = serializers.CharField()
    materias = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Materia.objects.all()
    )
    
    def validate(self, data):
        """Validar que las materias correspondan a la carrera del usuario"""
        id_usuario = data.get('id_usuario')
        materias = data.get('materias', [])
        
        # Obtener el usuario
        try:
            user = User.objects.get(id_usuario=id_usuario)
        except User.DoesNotExist:
            raise serializers.ValidationError({'id_usuario': 'Usuario no encontrado'})
        
        # Validar que tenga carrera
        if not user.carrera:
            raise serializers.ValidationError({'carrera': 'El usuario debe tener una carrera asignada'})
        
        # Validar que las materias correspondan a la carrera
        if materias:
            materias_permitidas = Materia.get_materias_por_carrera(user.carrera)
            # Convertir a lista si es queryset
            if hasattr(materias_permitidas, 'values_list'):
                materias_ids_permitidas = set(materias_permitidas.values_list('id', flat=True))
            else:
                # Es una lista de objetos
                materias_ids_permitidas = set(m.id for m in materias_permitidas)
            
            materias_ids_seleccionadas = set(m.id for m in materias)
            
            if not materias_ids_seleccionadas.issubset(materias_ids_permitidas):
                raise serializers.ValidationError({
                    'materias': f'Las materias seleccionadas no corresponden a la carrera {user.carrera}'
                })
            
            # Validar que ITI solo pueda seleccionar 1 materia
            if user.carrera == 'ITI' and len(materias) > 1:
                raise serializers.ValidationError({
                    'materias': 'Para la carrera ITI solo puede seleccionar una materia'
                })
        
        data['user'] = user
        return data
