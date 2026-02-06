"""
Servicio de Email para el Sistema de Gestión de Tareas
Maneja recuperación de contraseña, notificaciones y recordatorios.

Usa smtplib directo con Gmail App Password forzando IPv4.
Railway resuelve smtp.gmail.com a IPv6 pero su red no tiene IPv6 activo,
causando "Network is unreachable". Forzar IPv4 soluciona el problema.

Equivalente Python del nodemailer que usaban antes en Node.js.
Límite: 500 emails/día (límite de Gmail, no de un tercero).
"""
import os
import smtplib
import socket
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

# ── Configuración Gmail ──────────────────────────────────────────
EMAIL_USER = 'secretaria.instituto.aca@gmail.com'
EMAIL_PASSWORD = 'ffhdmnftjbnjcglc'  # App Password sin espacios
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587


# ── Parche IPv4: forzar resolución DNS a IPv4 ────────────────────
_original_getaddrinfo = socket.getaddrinfo


def _ipv4_getaddrinfo(*args, **kwargs):
    """
    Wrapper que filtra resultados DNS para devolver solo IPv4 (AF_INET).
    Esto evita el error 'Network is unreachable' en Railway donde IPv6
    está resuelto por DNS pero no es ruteable.
    """
    responses = _original_getaddrinfo(*args, **kwargs)
    ipv4_only = [r for r in responses if r[0] == socket.AF_INET]
    return ipv4_only if ipv4_only else responses


def _create_smtp_connection():
    """
    Crea conexión SMTP a Gmail forzando IPv4.
    Aplica el parche de DNS solo durante la conexión.
    """
    # Aplicar parche IPv4 temporalmente
    socket.getaddrinfo = _ipv4_getaddrinfo
    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=30)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        return server
    finally:
        # Restaurar getaddrinfo original
        socket.getaddrinfo = _original_getaddrinfo


# ── Función principal de envío ────────────────────────────────────
def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """
    Enviar email vía Gmail SMTP con IPv4 forzado.
    Equivalente a nodemailer.createTransport({ service: 'gmail', ... })

    Args:
        to_email: Correo del destinatario
        subject: Asunto del email
        html_content: Contenido HTML del email

    Returns:
        bool: True si se envió correctamente
    """
    try:
        logger.info(f"[EMAIL] Enviando a: {to_email} | From: {EMAIL_USER} | "
                     f"Host: {EMAIL_HOST}:{EMAIL_PORT} (IPv4 forzado)")

        # Construir mensaje MIME (equivalente a mailOptions en nodemailer)
        msg = MIMEMultipart('alternative')
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject

        # Versión texto plano (fallback)
        import re
        plain_text = re.sub(r'<[^>]+>', '', html_content)
        plain_text = re.sub(r'\s+', ' ', plain_text).strip()

        msg.attach(MIMEText(plain_text, 'plain', 'utf-8'))
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))

        # Conectar y enviar
        server = _create_smtp_connection()
        try:
            server.sendmail(EMAIL_USER, to_email, msg.as_string())
        finally:
            server.quit()

        logger.info(f"[EMAIL] ✅ Enviado exitosamente a {to_email}")
        print(f"✅ Email enviado exitosamente a {to_email}")
        return True

    except smtplib.SMTPAuthenticationError as e:
        logger.error(
            f"[EMAIL] ❌ AUTENTICACIÓN FALLIDA: Gmail rechazó las credenciales. "
            f"Verifica EMAIL_USER y EMAIL_PASSWORD en Railway. Detalle: {e}"
        )
        print(f"❌ Error de autenticación Gmail: {e}")
        return False

    except (socket.timeout, smtplib.SMTPConnectError, OSError) as e:
        logger.error(
            f"[EMAIL] ❌ CONEXIÓN FALLIDA a {EMAIL_HOST}:{EMAIL_PORT}: "
            f"{type(e).__name__}: {e}"
        )
        print(f"❌ Error de conexión SMTP: {type(e).__name__}: {e}")
        return False

    except Exception as e:
        logger.error(f"[EMAIL] ❌ Error inesperado enviando a {to_email}: "
                     f"{type(e).__name__}: {e}")
        print(f"❌ Error al enviar email a {to_email}: {type(e).__name__}: {e}")
        return False


# ── Diagnóstico ──────────────────────────────────────────────────
def test_email_connection() -> dict:
    """
    Prueba la conexión SMTP a Gmail con IPv4 forzado.
    No envía ningún email, solo verifica autenticación.
    """
    config = {
        'backend': 'gmail_smtp_ipv4',
        'host': EMAIL_HOST,
        'port': EMAIL_PORT,
        'user': EMAIL_USER,
        'password_set': bool(EMAIL_PASSWORD),
        'password_length': len(EMAIL_PASSWORD),
    }
    logger.info(f"[TEST] Probando conexión SMTP IPv4: {config}")

    try:
        server = _create_smtp_connection()
        server.quit()
        logger.info("[TEST] ✅ Conexión SMTP Gmail IPv4 exitosa")
        return {
            'success': True,
            'message': 'Conexión SMTP Gmail exitosa (IPv4 forzado)',
            'config': config,
        }
    except smtplib.SMTPAuthenticationError as e:
        msg = (f"Autenticación fallida: {e}. Verifica EMAIL_USER y EMAIL_PASSWORD "
               f"en las variables de entorno de Railway.")
        logger.error(f"[TEST] ❌ {msg}")
        return {'success': False, 'message': msg, 'config': config}
    except Exception as e:
        msg = f"{type(e).__name__}: {e}"
        logger.error(f"[TEST] ❌ {msg}")
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
