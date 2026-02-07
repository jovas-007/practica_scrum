import threading
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Avg
from .models import Task, Submission, SubmissionFile
from .serializers import (
    TaskListSerializer, TaskCreateSerializer, TaskDetailSerializer,
    SubmissionListSerializer, SubmissionStudentSerializer,
    GradeSubmissionSerializer, SubmitFileSerializer, StudentBasicSerializer
)
from users.models import User
from users.email_service import (
    send_task_assigned_email,
    send_submission_received_email,
    send_task_graded_email,
)


# ==================== ENDPOINTS DOCENTE ====================

@api_view(['GET', 'POST'])
def task_list_create(request):
    """
    GET: Lista todas las tareas del docente
    POST: Crear nueva tarea (borrador)
    """
    # Obtener docente desde el header o query param
    docente_id = request.headers.get('X-User-Id') or request.query_params.get('docente_id')
    
    if not docente_id:
        return Response({
            'success': False,
            'message': 'Se requiere ID del docente'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        docente = User.objects.get(id_usuario=docente_id, rol='docente')
    except User.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Docente no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        # Filtrar por estado si se especifica
        estado = request.query_params.get('estado')
        tareas = Task.objects.filter(docente=docente)
        
        if estado:
            tareas = tareas.filter(estado=estado)
        
        serializer = TaskListSerializer(tareas, many=True)
        return Response({
            'success': True,
            'tareas': serializer.data
        })
    
    elif request.method == 'POST':
        serializer = TaskCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            tarea = serializer.save(docente=docente)
            return Response({
                'success': True,
                'message': 'Tarea creada como borrador',
                'tarea': TaskListSerializer(tarea).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Error de validación',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def task_detail(request, task_id):
    """
    GET: Detalle de tarea con submissions
    PUT: Editar tarea
    DELETE: Eliminar tarea (solo borradores)
    """
    docente_id = request.headers.get('X-User-Id') or request.query_params.get('docente_id')
    
    try:
        tarea = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Tarea no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Verificar que el docente sea el dueño
    if docente_id and tarea.docente.id_usuario != docente_id:
        return Response({
            'success': False,
            'message': 'No tienes permiso para acceder a esta tarea'
        }, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        serializer = TaskDetailSerializer(tarea)
        return Response({
            'success': True,
            'tarea': serializer.data
        })
    
    elif request.method == 'PUT':
        # Solo se pueden editar borradores o tareas activas (ciertos campos)
        if tarea.estado == 'cerrada':
            return Response({
                'success': False,
                'message': 'No se puede editar una tarea cerrada'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = TaskCreateSerializer(tarea, data=request.data, partial=True)
        
        if serializer.is_valid():
            # Si la tarea está activa, solo permitir editar ciertos campos
            if tarea.estado == 'activa':
                allowed_fields = ['descripcion', 'url_recurso', 'fecha_entrega', 'permite_tardias']
                for field in request.data.keys():
                    if field not in allowed_fields and field != 'archivo_adjunto':
                        return Response({
                            'success': False,
                            'message': f'No se puede editar "{field}" en una tarea activa'
                        }, status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save()
            return Response({
                'success': True,
                'message': 'Tarea actualizada',
                'tarea': TaskListSerializer(tarea).data
            })
        
        return Response({
            'success': False,
            'message': 'Error de validación',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if tarea.estado != 'borrador':
            return Response({
                'success': False,
                'message': 'Solo se pueden eliminar tareas en borrador'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        tarea.delete()
        return Response({
            'success': True,
            'message': 'Tarea eliminada'
        })


@api_view(['POST'])
def task_activate(request, task_id):
    """
    POST: Activar tarea (crea submissions para todos los estudiantes)
    """
    docente_id = request.headers.get('X-User-Id') or request.query_params.get('docente_id')
    
    try:
        tarea = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Tarea no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if docente_id and tarea.docente.id_usuario != docente_id:
        return Response({
            'success': False,
            'message': 'No tienes permiso'
        }, status=status.HTTP_403_FORBIDDEN)
    
    if tarea.estado != 'borrador':
        return Response({
            'success': False,
            'message': 'Solo se pueden activar tareas en borrador'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Cambiar estado a activa (la señal creará los submissions)
    tarea.estado = 'activa'
    tarea.save()
    
    # Contar estudiantes asignados
    total_estudiantes = tarea.submissions.count()

    # Notificar por email a todos los estudiantes asignados (en background)
    def _notify_students():
        fecha = tarea.fecha_entrega.strftime('%d/%m/%Y %H:%M') if tarea.fecha_entrega else 'Sin fecha'
        for sub in tarea.submissions.select_related('student').all():
            try:
                send_task_assigned_email(
                    nombre_completo=sub.student.nombre_completo,
                    correo=sub.student.correo,
                    titulo_tarea=tarea.titulo,
                    descripcion=tarea.descripcion or '',
                    fecha_entrega=fecha,
                    docente_nombre=tarea.docente.nombre_completo,
                )
            except Exception as e:
                print(f'[EMAIL] Error notificando a {sub.student.correo}: {e}')

    threading.Thread(target=_notify_students, daemon=True).start()

    return Response({
        'success': True,
        'message': f'Tarea activada y asignada a {total_estudiantes} estudiantes',
        'tarea': TaskListSerializer(tarea).data
    })


@api_view(['POST'])
def task_close(request, task_id):
    """
    POST: Cerrar tarea (no permite más entregas)
    """
    docente_id = request.headers.get('X-User-Id') or request.query_params.get('docente_id')
    
    try:
        tarea = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Tarea no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if docente_id and tarea.docente.id_usuario != docente_id:
        return Response({
            'success': False,
            'message': 'No tienes permiso'
        }, status=status.HTTP_403_FORBIDDEN)
    
    if tarea.estado != 'activa':
        return Response({
            'success': False,
            'message': 'Solo se pueden cerrar tareas activas'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    tarea.estado = 'cerrada'
    tarea.save()
    
    return Response({
        'success': True,
        'message': 'Tarea cerrada',
        'tarea': TaskListSerializer(tarea).data
    })


@api_view(['GET'])
def task_submissions(request, task_id):
    """
    GET: Lista de entregas de una tarea
    """
    try:
        tarea = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Tarea no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)
    
    submissions = tarea.submissions.all().select_related('student').prefetch_related('archivos')
    serializer = SubmissionListSerializer(submissions, many=True)
    
    return Response({
        'success': True,
        'tarea': tarea.titulo,
        'submissions': serializer.data
    })


@api_view(['POST'])
def grade_submission(request, submission_id):
    """
    POST: Calificar una entrega
    """
    try:
        submission = Submission.objects.get(id=submission_id)
    except Submission.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Entrega no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if submission.estado == 'pendiente':
        return Response({
            'success': False,
            'message': 'No se puede calificar una entrega sin archivos'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = GradeSubmissionSerializer(data=request.data)
    
    if serializer.is_valid():
        submission.calificacion = serializer.validated_data['calificacion']
        submission.comentario_docente = serializer.validated_data.get('comentario_docente', '')
        submission.fecha_calificacion = timezone.now()
        submission.estado = 'calificado'
        submission.save()

        # Notificar al estudiante por email (en background)
        def _notify_graded():
            try:
                send_task_graded_email(
                    estudiante_nombre=submission.student.nombre_completo,
                    estudiante_correo=submission.student.correo,
                    titulo_tarea=submission.task.titulo,
                    calificacion=submission.calificacion,
                    puntos_maximos=10,
                    comentario=submission.comentario_docente or '',
                )
            except Exception as e:
                print(f'[EMAIL] Error notificando calificación a {submission.student.correo}: {e}')

        threading.Thread(target=_notify_graded, daemon=True).start()

        return Response({
            'success': True,
            'message': f'Entrega calificada con {submission.calificacion}/10',
            'submission': SubmissionListSerializer(submission).data
        })
    
    return Response({
        'success': False,
        'message': 'Error de validación',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def grades_report(request):
    """
    GET: Reporte de calificaciones (tabla estudiantes × tareas)
    """
    docente_id = request.headers.get('X-User-Id') or request.query_params.get('docente_id')
    
    if not docente_id:
        return Response({
            'success': False,
            'message': 'Se requiere ID del docente'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Obtener tareas del docente que estén activas o cerradas
    tareas = Task.objects.filter(
        docente__id_usuario=docente_id,
        estado__in=['activa', 'cerrada']
    ).order_by('fecha_creacion')
    
    # Obtener todos los estudiantes
    estudiantes = User.objects.filter(rol='estudiante', is_active=True)
    
    # Construir reporte
    reporte = []
    for estudiante in estudiantes:
        fila = {
            'estudiante': StudentBasicSerializer(estudiante).data,
            'tareas': [],
            'promedio': None
        }
        
        calificaciones = []
        for tarea in tareas:
            try:
                submission = Submission.objects.get(task=tarea, student=estudiante)
                tarea_data = {
                    'id': tarea.id,
                    'titulo': tarea.titulo,
                    'estado_entrega': submission.estado,
                    'calificacion': submission.calificacion,
                    'es_tardia': submission.archivos.filter(es_entrega_tardia=True).exists() if submission.tiene_entregas else False
                }
                if submission.calificacion:
                    calificaciones.append(submission.calificacion)
            except Submission.DoesNotExist:
                tarea_data = {
                    'id': tarea.id,
                    'titulo': tarea.titulo,
                    'estado_entrega': 'no_asignado',
                    'calificacion': None,
                    'es_tardia': False
                }
            
            fila['tareas'].append(tarea_data)
        
        if calificaciones:
            fila['promedio'] = round(sum(calificaciones) / len(calificaciones), 2)
        
        reporte.append(fila)
    
    return Response({
        'success': True,
        'tareas_headers': [{'id': t.id, 'titulo': t.titulo} for t in tareas],
        'reporte': reporte
    })


# ==================== ENDPOINTS ESTUDIANTE ====================

@api_view(['GET'])
def my_tasks(request):
    """
    GET: Lista de tareas asignadas al estudiante
    """
    student_id = request.headers.get('X-User-Id') or request.query_params.get('student_id')
    
    if not student_id:
        return Response({
            'success': False,
            'message': 'Se requiere ID del estudiante'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        estudiante = User.objects.get(id_usuario=student_id, rol='estudiante')
    except User.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Estudiante no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Obtener submissions del estudiante (tareas activas y cerradas)
    submissions = Submission.objects.filter(
        student=estudiante,
        task__estado__in=['activa', 'cerrada']
    ).select_related('task').prefetch_related('archivos').order_by('-task__fecha_entrega')
    
    # Agrupar por estado
    pendientes = []
    entregadas = []
    calificadas = []
    
    for sub in submissions:
        data = {
            'submission_id': sub.id,
            'task_id': sub.task.id,
            'titulo': sub.task.titulo,
            'descripcion': sub.task.descripcion[:100] + '...' if len(sub.task.descripcion) > 100 else sub.task.descripcion,
            'fecha_entrega': sub.task.fecha_entrega,
            'estado': sub.estado,
            'calificacion': sub.calificacion,
            'puntos_maximos': sub.task.puntos_maximos,
            'esta_vencida': sub.task.esta_vencida,
            'puede_entregar': sub.task.puede_recibir_entregas,
            'tiene_archivos': sub.tiene_entregas
        }
        
        if sub.estado == 'pendiente':
            pendientes.append(data)
        elif sub.estado == 'entregado':
            entregadas.append(data)
        else:
            calificadas.append(data)
    
    return Response({
        'success': True,
        'pendientes': pendientes,
        'entregadas': entregadas,
        'calificadas': calificadas,
        'total': len(submissions)
    })


@api_view(['GET'])
def my_task_detail(request, task_id):
    """
    GET: Detalle de una tarea para el estudiante
    """
    student_id = request.headers.get('X-User-Id') or request.query_params.get('student_id')
    
    if not student_id:
        return Response({
            'success': False,
            'message': 'Se requiere ID del estudiante'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        submission = Submission.objects.get(
            task_id=task_id,
            student__id_usuario=student_id
        )
    except Submission.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Tarea no encontrada o no asignada'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = SubmissionStudentSerializer(submission, context={'request': request})
    
    return Response({
        'success': True,
        'submission': serializer.data
    })


@api_view(['POST'])
def submit_task(request, task_id):
    """
    POST: Subir archivos para una tarea
    """
    student_id = request.headers.get('X-User-Id') or request.query_params.get('student_id')
    
    if not student_id:
        return Response({
            'success': False,
            'message': 'Se requiere ID del estudiante'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        submission = Submission.objects.get(
            task_id=task_id,
            student__id_usuario=student_id
        )
    except Submission.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Tarea no encontrada o no asignada'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Verificar si puede entregar
    if not submission.task.puede_recibir_entregas:
        if submission.task.estado == 'cerrada':
            return Response({
                'success': False,
                'message': 'Esta tarea está cerrada y no acepta más entregas'
            }, status=status.HTTP_400_BAD_REQUEST)
        elif submission.task.esta_vencida and not submission.task.permite_tardias:
            return Response({
                'success': False,
                'message': 'La fecha límite ha pasado y no se permiten entregas tardías'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    # Obtener archivos del request
    archivos = request.FILES.getlist('archivos')
    
    if not archivos:
        return Response({
            'success': False,
            'message': 'No se recibieron archivos'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validar archivos
    allowed_extensions = [
        'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
        'jpg', 'jpeg', 'png', 'gif', 'zip', 'rar', 'txt',
        'py', 'js', 'html', 'css', 'java', 'cpp', 'c'
    ]
    max_size = 20 * 1024 * 1024  # 20MB
    
    for archivo in archivos:
        if archivo.size > max_size:
            return Response({
                'success': False,
                'message': f'El archivo {archivo.name} excede los 20MB permitidos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        ext = archivo.name.split('.')[-1].lower() if '.' in archivo.name else ''
        if ext not in allowed_extensions:
            return Response({
                'success': False,
                'message': f'Extensión no permitida: .{ext}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    # Guardar archivos
    archivos_guardados = []
    es_tardia = submission.task.esta_vencida
    
    for archivo in archivos:
        submission_file = SubmissionFile.objects.create(
            submission=submission,
            archivo=archivo,
            nombre_original=archivo.name,
            es_entrega_tardia=es_tardia
        )
        archivos_guardados.append({
            'id': submission_file.id,
            'nombre': submission_file.nombre_original,
            'es_tardia': submission_file.es_entrega_tardia
        })
    
    # Actualizar estado de submission
    if submission.estado == 'pendiente':
        submission.estado = 'entregado'
        submission.save()

    # # Notificar al docente por email (en background) - DESACTIVADO
    # def _notify_teacher():
    #     try:
    #         send_submission_received_email(
    #             docente_nombre=submission.task.docente.nombre_completo,
    #             docente_correo=submission.task.docente.correo,
    #             estudiante_nombre=submission.student.nombre_completo,
    #             titulo_tarea=submission.task.titulo,
    #             es_tardia=es_tardia,
    #         )
    #     except Exception as e:
    #         print(f'[EMAIL] Error notificando entrega a docente: {e}')
    # 
    # threading.Thread(target=_notify_teacher, daemon=True).start()

    mensaje = f'{len(archivos_guardados)} archivo(s) subido(s) correctamente'
    if es_tardia:
        mensaje += ' (ENTREGA TARDÍA)'
    
    return Response({
        'success': True,
        'message': mensaje,
        'archivos': archivos_guardados,
        'estado': submission.estado
    })


@api_view(['GET'])
def my_submissions(request):
    """
    GET: Historial de todas las entregas del estudiante
    """
    student_id = request.headers.get('X-User-Id') or request.query_params.get('student_id')
    
    if not student_id:
        return Response({
            'success': False,
            'message': 'Se requiere ID del estudiante'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        estudiante = User.objects.get(id_usuario=student_id, rol='estudiante')
    except User.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Estudiante no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    
    submissions = Submission.objects.filter(
        student=estudiante,
        estado='calificado'
    ).select_related('task').order_by('-fecha_calificacion')
    
    # Calcular promedio
    calificaciones = [s.calificacion for s in submissions if s.calificacion]
    promedio = round(sum(calificaciones) / len(calificaciones), 2) if calificaciones else None
    
    data = []
    for sub in submissions:
        data.append({
            'tarea': sub.task.titulo,
            'calificacion': sub.calificacion,
            'puntos_maximos': sub.task.puntos_maximos,
            'comentario': sub.comentario_docente,
            'fecha_calificacion': sub.fecha_calificacion,
            'es_tardia': sub.archivos.filter(es_entrega_tardia=True).exists()
        })
    
    return Response({
        'success': True,
        'calificaciones': data,
        'promedio': promedio,
        'total_calificadas': len(calificaciones)
    })


# ==================== ENDPOINTS PÚBLICOS ====================

@api_view(['GET'])
def students_list(request):
    """
    GET: Lista de estudiantes registrados
    """
    estudiantes = User.objects.filter(rol='estudiante', is_active=True)
    serializer = StudentBasicSerializer(estudiantes, many=True)
    
    return Response({
        'success': True,
        'estudiantes': serializer.data,
        'total': estudiantes.count()
    })
