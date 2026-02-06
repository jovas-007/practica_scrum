"""
Servicio de Email para el Sistema de Gestión de Tareas
Maneja recuperación de contraseña, notificaciones y recordatorios.

Backend dual:
  - Producción (Railway): Resend HTTP API (SMTP bloqueado por Railway)
  - Desarrollo local: Django SMTP con Gmail App Password

Se selecciona automáticamente según la variable RESEND_API_KEY.
"""
import os
import requests
import logging

logger = logging.getLogger(__name__)

# ── Detección automática del backend ──────────────────────────────
RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
# Remitente para Resend: necesita dominio verificado o usa el de prueba
RESEND_FROM = os.environ.get('RESEND_FROM', 'Sistema de Tareas BUAP <onboarding@resend.dev>')
USE_RESEND = bool(RESEND_API_KEY)


# ── Backend: Resend HTTP API ─────────────────────────────────────
def _send_via_resend(to_email: str, subject: str, html_content: str) -> bool:
    """Envía email usando Resend REST API (funciona en Railway)."""
    try:
        logger.info(f"[RESEND] Enviando a: {to_email} | From: {RESEND_FROM}")
        response = requests.post(
            'https://api.resend.com/emails',
            headers={
                'Authorization': f'Bearer {RESEND_API_KEY}',
                'Content-Type': 'application/json',
            },
            json={
                'from': RESEND_FROM,
                'to': [to_email],
                'subject': subject,
                'html': html_content,
            },
            timeout=30,
        )

        if response.status_code in (200, 201):
            data = response.json()
            logger.info(f"[RESEND] ✅ Email enviado a {to_email} (id: {data.get('id', '?')})")
            print(f"✅ Email enviado exitosamente a {to_email}")
            return True
        else:
            logger.error(
                f"[RESEND] ❌ Error {response.status_code} enviando a {to_email}: "
                f"{response.text}"
            )
            print(f"❌ Resend error {response.status_code}: {response.text}")
            return False

    except requests.exceptions.Timeout:
        logger.error(f"[RESEND] ❌ Timeout conectando a api.resend.com")
        print(f"❌ Timeout conectando a Resend API")
        return False
    except Exception as e:
        logger.error(f"[RESEND] ❌ Error inesperado: {type(e).__name__}: {e}")
        print(f"❌ Error inesperado enviando email: {e}")
        return False


# ── Backend: Django SMTP (desarrollo local) ──────────────────────
def _send_via_smtp(to_email: str, subject: str, html_content: str) -> bool:
    """Envía email usando Django SMTP Backend (Gmail App Password)."""
    try:
        from django.core.mail import EmailMultiAlternatives
        from django.conf import settings
        from django.utils.html import strip_tags

        logger.info(f"[SMTP] Enviando a: {to_email} | From: {settings.EMAIL_HOST_USER}")
        logger.debug(
            f"[SMTP] Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT} | "
            f"TLS: {settings.EMAIL_USE_TLS}"
        )

        plain_text = strip_tags(html_content)
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

        logger.info(f"[SMTP] ✅ Enviado exitosamente a {to_email}")
        print(f"✅ Email enviado exitosamente a {to_email}")
        return True

    except Exception as e:
        logger.error(f"[SMTP] ❌ Falló envío a {to_email}: {type(e).__name__}: {e}")
        print(f"❌ Error al enviar email a {to_email}: {type(e).__name__}: {e}")
        return False


# ── Función principal de envío ────────────────────────────────────
def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """
    Enviar email usando el backend disponible.
    - Si RESEND_API_KEY está configurada → usa Resend HTTP API
    - Si no → usa Django SMTP (Gmail)
    """
    backend = 'Resend HTTP' if USE_RESEND else 'Django SMTP'
    logger.info(f"[EMAIL] Backend: {backend} | Destino: {to_email}")

    if USE_RESEND:
        return _send_via_resend(to_email, subject, html_content)
    else:
        return _send_via_smtp(to_email, subject, html_content)


# ── Diagnóstico ──────────────────────────────────────────────────
def test_email_connection() -> dict:
    """
    Prueba la conexión al servicio de email configurado.
    """
    config = {
        'backend': 'resend' if USE_RESEND else 'smtp',
        'resend_api_key_set': bool(RESEND_API_KEY),
        'resend_from': RESEND_FROM if USE_RESEND else None,
    }

    if USE_RESEND:
        # Probar que la API key es válida consultando los dominios
        try:
            resp = requests.get(
                'https://api.resend.com/domains',
                headers={'Authorization': f'Bearer {RESEND_API_KEY}'},
                timeout=10,
            )
            if resp.status_code == 200:
                logger.info("[TEST] ✅ Resend API key válida")
                return {
                    'success': True,
                    'message': 'Resend API key válida y conectada',
                    'config': config,
                }
            else:
                msg = f'Resend respondió {resp.status_code}: {resp.text}'
                logger.error(f"[TEST] ❌ {msg}")
                return {'success': False, 'message': msg, 'config': config}
        except Exception as e:
            msg = f'Error conectando a Resend API: {type(e).__name__}: {e}'
            logger.error(f"[TEST] ❌ {msg}")
            return {'success': False, 'message': msg, 'config': config}
    else:
        # Probar conexión SMTP
        try:
            from django.core.mail import get_connection
            from django.conf import settings

            config.update({
                'smtp_host': settings.EMAIL_HOST,
                'smtp_port': settings.EMAIL_PORT,
                'smtp_tls': settings.EMAIL_USE_TLS,
                'smtp_user': settings.EMAIL_HOST_USER,
                'smtp_password_set': bool(settings.EMAIL_HOST_PASSWORD),
            })

            connection = get_connection(
                backend=settings.EMAIL_BACKEND,
                host=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                username=settings.EMAIL_HOST_USER,
                password=settings.EMAIL_HOST_PASSWORD,
                use_tls=settings.EMAIL_USE_TLS,
                use_ssl=settings.EMAIL_USE_SSL,
                timeout=settings.EMAIL_TIMEOUT,
            )
            connection.open()
            connection.close()
            logger.info("[TEST] ✅ Conexión SMTP exitosa")
            return {'success': True, 'message': 'Conexión SMTP exitosa', 'config': config}
        except Exception as e:
            msg = f'{type(e).__name__}: {e}'
            logger.error(f"[TEST] ❌ SMTP falló: {msg}")
            return {'success': False, 'message': msg, 'config': config}


def send_recovery_code_email(nombre_completo: str, correo: str, code: str) -> bool:
    """
    Enviar código de recuperación de contraseña
    
    Args:
        nombre_completo: Nombre del usuario
        correo: Email del usuario
        code: Código de 6 dígitos
    
    Returns:
        bool: True si se envió correctamente
    """
    subject = '🔑 Código de Recuperación - Sistema de Gestión de Tareas'
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #2c3e50;">🔑 Código de Recuperación de Contraseña</h2>
        <p>Hola <strong>{nombre_completo}</strong>,</p>
        
        <p>Has solicitado recuperar tu contraseña. Tu código de verificación es:</p>
        
        <div style="background-color: #f8f9fa; padding: 30px; border-left: 4px solid #3498db; margin: 20px 0; text-align: center;">
            <h1 style="color: #3498db; font-size: 48px; margin: 0; letter-spacing: 8px;">{code}</h1>
        </div>
        
        <p style="color: #e74c3c; font-weight: bold;">
            ⚠️ Este código expira en 15 minutos.
        </p>
        
        <p>Ingresa este código en la página de recuperación para continuar.</p>
        
        <p>Si no solicitaste esta recuperación, por favor ignora este mensaje.</p>
        
        <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 30px 0;">
        
        <p style="color: #7f8c8d; font-size: 12px;">
            Este es un mensaje automático del Sistema de Gestión de Tareas Escolares - BUAP.
            <br>Por favor, no respondas a este correo.
        </p>
    </div>
    """
    
    return send_email(correo, subject, html_content)


def send_task_assigned_email(nombre_completo: str, correo: str, 
                              titulo_tarea: str, descripcion: str,
                              fecha_entrega: str, docente_nombre: str) -> bool:
    """
    Enviar notificación de nueva tarea asignada
    
    Args:
        nombre_completo: Nombre del estudiante
        correo: Email del estudiante
        titulo_tarea: Título de la tarea
        descripcion: Descripción de la tarea
        fecha_entrega: Fecha de entrega formateada
        docente_nombre: Nombre del docente que asignó
    
    Returns:
        bool: True si se envió correctamente
    """
    subject = f'📝 Nueva Tarea Asignada: {titulo_tarea}'
    
    # Truncar descripción si es muy larga
    desc_preview = descripcion[:200] + '...' if len(descripcion) > 200 else descripcion
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #2c3e50;">📝 Nueva Tarea Asignada</h2>
        <p>Hola <strong>{nombre_completo}</strong>,</p>
        
        <p>Se te ha asignado una nueva tarea:</p>
        
        <div style="background-color: #f8f9fa; padding: 20px; border-left: 4px solid #27ae60; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #27ae60;">{titulo_tarea}</h3>
            <p><strong>📖 Descripción:</strong> {desc_preview}</p>
            <p><strong>📅 Fecha de entrega:</strong> {fecha_entrega}</p>
            <p><strong>👨‍🏫 Docente:</strong> {docente_nombre}</p>
        </div>
        
        <p>Ingresa al sistema para ver los detalles completos y entregar tu trabajo.</p>
        
        <p style="color: #7f8c8d; font-size: 12px; margin-top: 30px;">
            Sistema de Gestión de Tareas Escolares - BUAP
        </p>
    </div>
    """
    
    return send_email(correo, subject, html_content)


def send_submission_received_email(docente_nombre: str, docente_correo: str,
                                    estudiante_nombre: str, titulo_tarea: str,
                                    es_tardia: bool) -> bool:
    """
    Notificar al docente que un estudiante entregó una tarea
    
    Args:
        docente_nombre: Nombre del docente
        docente_correo: Email del docente
        estudiante_nombre: Nombre del estudiante que entregó
        titulo_tarea: Título de la tarea
        es_tardia: Si la entrega fue tardía
    
    Returns:
        bool: True si se envió correctamente
    """
    tardia_text = " ⏰ (TARDÍA)" if es_tardia else ""
    subject = f'📬 Entrega Recibida: {titulo_tarea}{tardia_text}'
    
    tardia_alert = ""
    if es_tardia:
        tardia_alert = """
        <div style="background-color: #fff3cd; padding: 10px; border-left: 4px solid #f39c12; margin: 15px 0;">
            <p style="margin: 0; color: #856404;">⏰ <strong>Nota:</strong> Esta entrega fue realizada después de la fecha límite.</p>
        </div>
        """
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #2c3e50;">📬 Nueva Entrega Recibida</h2>
        <p>Hola <strong>{docente_nombre}</strong>,</p>
        
        <p>Un estudiante ha entregado una tarea:</p>
        
        <div style="background-color: #f8f9fa; padding: 20px; border-left: 4px solid #3498db; margin: 20px 0;">
            <p><strong>👤 Estudiante:</strong> {estudiante_nombre}</p>
            <p><strong>📝 Tarea:</strong> {titulo_tarea}</p>
        </div>
        
        {tardia_alert}
        
        <p>Ingresa al sistema para revisar y calificar la entrega.</p>
        
        <p style="color: #7f8c8d; font-size: 12px; margin-top: 30px;">
            Sistema de Gestión de Tareas Escolares - BUAP
        </p>
    </div>
    """
    
    return send_email(docente_correo, subject, html_content)


def send_task_graded_email(estudiante_nombre: str, estudiante_correo: str,
                            titulo_tarea: str, calificacion: int,
                            puntos_maximos: int, comentario: str) -> bool:
    """
    Notificar al estudiante que su tarea fue calificada
    
    Args:
        estudiante_nombre: Nombre del estudiante
        estudiante_correo: Email del estudiante
        titulo_tarea: Título de la tarea
        calificacion: Calificación obtenida (1-10)
        puntos_maximos: Puntos máximos posibles
        comentario: Comentario del docente
    
    Returns:
        bool: True si se envió correctamente
    """
    # Color según calificación
    if calificacion >= 8:
        color = '#27ae60'  # Verde
        emoji = '🌟'
    elif calificacion >= 6:
        color = '#f39c12'  # Amarillo
        emoji = '👍'
    else:
        color = '#e74c3c'  # Rojo
        emoji = '📚'
    
    subject = f'{emoji} Tu tarea fue calificada: {calificacion}/{puntos_maximos}'
    
    comentario_html = ""
    if comentario:
        comentario_html = f"""
        <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #7f8c8d; margin: 15px 0;">
            <p style="margin: 0;"><strong>💬 Comentario del docente:</strong></p>
            <p style="margin: 10px 0 0 0; font-style: italic;">"{comentario}"</p>
        </div>
        """
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #2c3e50;">{emoji} Tarea Calificada</h2>
        <p>Hola <strong>{estudiante_nombre}</strong>,</p>
        
        <p>Tu tarea ha sido calificada:</p>
        
        <div style="background-color: #f8f9fa; padding: 20px; border-left: 4px solid {color}; margin: 20px 0; text-align: center;">
            <p style="margin: 0 0 10px 0;"><strong>📝 {titulo_tarea}</strong></p>
            <h1 style="color: {color}; font-size: 48px; margin: 0;">{calificacion}/{puntos_maximos}</h1>
        </div>
        
        {comentario_html}
        
        <p>Ingresa al sistema para ver más detalles.</p>
        
        <p style="color: #7f8c8d; font-size: 12px; margin-top: 30px;">
            Sistema de Gestión de Tareas Escolares - BUAP
        </p>
    </div>
    """
    
    return send_email(estudiante_correo, subject, html_content)


def send_task_reminder_email(nombre_completo: str, correo: str, 
                              titulo_tarea: str, 
                              fecha_entrega: str) -> bool:
    """
    Enviar recordatorio de tarea próxima a vencer (24 horas antes)
    
    Args:
        nombre_completo: Nombre del usuario
        correo: Email del usuario
        titulo_tarea: Título de la tarea
        fecha_entrega: Fecha de entrega formateada
    
    Returns:
        bool: True si se envió correctamente
    """
    subject = f'⏰ Recordatorio: "{titulo_tarea}" vence mañana'
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #e67e22;">⏰ Recordatorio de Tarea</h2>
        <p>Hola <strong>{nombre_completo}</strong>,</p>
        
        <p>Te recordamos que tienes una tarea pendiente que vence <strong>mañana</strong>:</p>
        
        <div style="background-color: #fff3cd; padding: 20px; border-left: 4px solid #f39c12; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #856404;">{titulo_tarea}</h3>
            <p><strong>📅 Fecha de entrega:</strong> {fecha_entrega}</p>
            <p><strong>⏳ Tiempo restante:</strong> Menos de 24 horas</p>
        </div>
        
        <p style="color: #e74c3c; font-weight: bold;">
            ¡No olvides entregar tu tarea a tiempo!
        </p>
        
        <p>Ingresa al sistema para completar tu entrega.</p>
        
        <p style="color: #7f8c8d; font-size: 12px; margin-top: 30px;">
            Sistema de Gestión de Tareas Escolares - BUAP
        </p>
    </div>
    """
    
    return send_email(correo, subject, html_content)
