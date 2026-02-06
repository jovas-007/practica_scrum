"""
Views para la API de usuarios
"""
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
import random
import string

from .models import User, RecoveryCode
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    LoginSerializer,
    ForgotPasswordSerializer,
    VerifyCodeSerializer,
    ResetPasswordSerializer,
)


@api_view(['POST'])
def register(request):
    """
    POST /api/register
    Registrar un nuevo usuario
    """
    print(f"[DEBUG] Datos recibidos: {request.data}")
    serializer = RegisterSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'success': True,
            'message': 'Usuario registrado exitosamente',
            'id_usuario': user.id_usuario,
            'nombre_completo': user.nombre_completo,
            'correo': user.correo,
            'rol': user.rol,
        }, status=status.HTTP_201_CREATED)
    
    # Formatear errores para mantener compatibilidad con frontend
    errors = serializer.errors
    print(f"[DEBUG] Errores de validación: {errors}")
    error_message = ''
    
    if 'id_usuario' in errors:
        if 'unique' in str(errors['id_usuario']).lower():
            error_message = 'El ID de usuario ya está registrado'
        else:
            error_message = str(errors['id_usuario'][0])
    elif 'correo' in errors:
        if 'unique' in str(errors['correo']).lower():
            error_message = 'El correo electrónico ya está registrado'
        else:
            error_message = str(errors['correo'][0])
    elif 'password' in errors:
        error_message = str(errors['password'][0])
    else:
        error_message = str(list(errors.values())[0][0])
    
    print(f"[DEBUG] Mensaje de error: {error_message}")
    return Response({
        'success': False,
        'message': error_message
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    """
    POST /api/login
    Autenticar un usuario
    """
    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        return Response({
            'success': True,
            'user': {
                'id_usuario': user.id_usuario,
                'nombre_completo': user.nombre_completo,
                'correo': user.correo,
                'rol': user.rol,
                'carrera': user.carrera,
            }
        })
    
    return Response({
        'success': False,
        'message': 'Matrícula/Correo o contraseña incorrectos'
    }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def get_users(request):
    """
    GET /api/users
    Obtener todos los usuarios (desarrollo)
    """
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def forgot_password(request):
    """
    POST /api/forgot-password
    Solicitar código de recuperación de contraseña
    """
    from .email_service import send_recovery_code_email
    
    serializer = ForgotPasswordSerializer(data=request.data)
    
    if serializer.is_valid():
        correo = serializer.validated_data['correo']
        user = User.objects.get(correo__iexact=correo)
        
        # Generar código de 6 dígitos
        code = ''.join(random.choices(string.digits, k=6))
        
        # Guardar código con expiración de 15 minutos
        RecoveryCode.objects.create(
            user=user,
            code=code,
            expires_at=timezone.now() + timedelta(minutes=15)
        )
        
        # Enviar correo con el código
        email_sent = send_recovery_code_email(
            nombre_completo=user.nombre_completo,
            correo=user.correo,
            code=code
        )
        
        if email_sent:
            return Response({
                'success': True,
                'message': 'Se ha enviado un código de verificación a tu correo'
            })
        else:
            # Si falla el email, igual devolvemos éxito pero logueamos el código
            print(f"[DEBUG] Email falló. Código de recuperación para {correo}: {code}")
            return Response({
                'success': True,
                'message': 'Se ha enviado un código de verificación a tu correo'
            })
    
    return Response({
        'success': False,
        'message': serializer.errors.get('correo', ['Error al procesar solicitud'])[0]
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def verify_code(request):
    """
    POST /api/verify-code
    Verificar código de recuperación
    """
    serializer = VerifyCodeSerializer(data=request.data)
    
    if serializer.is_valid():
        correo = serializer.validated_data['correo']
        code = serializer.validated_data['code']
        
        try:
            user = User.objects.get(correo__iexact=correo)
            recovery = RecoveryCode.objects.filter(
                user=user,
                code=code,
                used=False,
                expires_at__gt=timezone.now()
            ).latest('created_at')
            
            return Response({
                'success': True,
                'message': 'Código verificado correctamente'
            })
        except (User.DoesNotExist, RecoveryCode.DoesNotExist):
            pass
    
    return Response({
        'success': False,
        'message': 'Código inválido o expirado'
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def reset_password(request):
    """
    POST /api/reset-password
    Restablecer contraseña con código verificado
    """
    serializer = ResetPasswordSerializer(data=request.data)
    
    if serializer.is_valid():
        correo = serializer.validated_data['correo']
        code = serializer.validated_data['code']
        new_password = serializer.validated_data['newPassword']
        
        try:
            user = User.objects.get(correo__iexact=correo)
            recovery = RecoveryCode.objects.filter(
                user=user,
                code=code,
                used=False,
                expires_at__gt=timezone.now()
            ).latest('created_at')
            
            # Cambiar contraseña
            user.set_password(new_password)
            user.save()
            
            # Marcar código como usado
            recovery.used = True
            recovery.save()
            
            return Response({
                'success': True,
                'message': 'Contraseña actualizada exitosamente'
            })
        except (User.DoesNotExist, RecoveryCode.DoesNotExist):
            pass
    
    return Response({
        'success': False,
        'message': 'No se pudo restablecer la contraseña. Código inválido o expirado.'
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def test_reminders(request):
    """
    POST /api/test-reminders
    Probar conexión al servicio de email y enviar email de prueba.
    Body opcional: { "correo": "destino@ejemplo.com" }
    """
    from .email_service import test_email_connection, send_recovery_code_email

    # Paso 1: Probar conexión al servicio de email
    conn_result = test_email_connection()
    if not conn_result['success']:
        return Response({
            'success': False,
            'message': f'Error de conexión: {conn_result["message"]}',
            'config': conn_result.get('config', {}),
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Paso 2: Enviar email de prueba
    try:
        to_email = request.data.get('correo')
        if not to_email:
            docente = User.objects.filter(rol='docente').first()
            if docente:
                to_email = docente.correo
            else:
                return Response({
                    'success': False,
                    'message': 'No hay docentes registrados y no se proporcionó correo destino',
                    'connection': 'OK',
                }, status=status.HTTP_404_NOT_FOUND)

        success = send_recovery_code_email(
            nombre_completo='Prueba de Sistema',
            correo=to_email,
            code='123456'
        )

        if success:
            return Response({
                'success': True,
                'message': f'Email de prueba enviado a {to_email}',
                'backend': conn_result['config']['backend'],
            })
        else:
            return Response({
                'success': False,
                'message': f'Conexión OK pero falló el envío a {to_email}. Revisa los logs.',
                'backend': conn_result['config']['backend'],
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def test_smtp(request):
    """
    GET /api/test-smtp
    Prueba la conexión al servicio de email sin enviar nada.
    Útil para verificar las variables de entorno en Railway.
    """
    from .email_service import test_email_connection

    result = test_email_connection()
    http_status = status.HTTP_200_OK if result['success'] else status.HTTP_500_INTERNAL_SERVER_ERROR
    return Response(result, status=http_status)
