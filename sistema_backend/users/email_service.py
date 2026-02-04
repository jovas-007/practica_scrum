"""
Servicio de Email para el Sistema de Gestión de Tareas
Maneja recuperación de contraseña y recordatorios
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings


# Configuración de Gmail - CAMBIAR POR TUS CREDENCIALES
EMAIL_CONFIG = {
    'host': 'smtp.gmail.com',
    'port': 587,
    'user': 'secretaria.instituto.aca@gmail.com',  # ← Cambia esto por tu Gmail
    'password': 'ffhd mnft jbnj cglc',  # ← Cambia esto por tu contraseña de aplicación
}


def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """
    Enviar email usando SMTP de Gmail
    
    Args:
        to_email: Correo del destinatario
        subject: Asunto del email
        html_content: Contenido HTML del email
    
    Returns:
        bool: True si se envió correctamente, False en caso de error
    """
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = EMAIL_CONFIG['user']
        msg['To'] = to_email
        
        # Adjuntar contenido HTML
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Conectar y enviar
        with smtplib.SMTP(EMAIL_CONFIG['host'], EMAIL_CONFIG['port']) as server:
            server.starttls()
            server.login(EMAIL_CONFIG['user'], EMAIL_CONFIG['password'])
            server.sendmail(EMAIL_CONFIG['user'], to_email, msg.as_string())
        
        print(f"✅ Email enviado a {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Error al enviar email a {to_email}: {str(e)}")
        return False


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


def send_task_reminder_email(nombre_completo: str, correo: str, 
                              nombre_tarea: str, materia: str, 
                              fecha_entrega: str) -> bool:
    """
    Enviar recordatorio de tarea próxima a vencer
    
    Args:
        nombre_completo: Nombre del usuario
        correo: Email del usuario
        nombre_tarea: Nombre de la tarea
        materia: Materia de la tarea
        fecha_entrega: Fecha de entrega formateada
    
    Returns:
        bool: True si se envió correctamente
    """
    subject = f'📚 Recordatorio: Tarea "{nombre_tarea}" - Entrega mañana'
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #2c3e50;">📚 Recordatorio de Tarea</h2>
        <p>Hola <strong>{nombre_completo}</strong>,</p>
        
        <p>Te recordamos que tienes una tarea próxima a vencer:</p>
        
        <div style="background-color: #f8f9fa; padding: 20px; border-left: 4px solid #3498db; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #3498db;">{nombre_tarea}</h3>
            <p><strong>📖 Materia:</strong> {materia}</p>
            <p><strong>📅 Fecha de entrega:</strong> {fecha_entrega}</p>
            <p><strong>⏰ Tiempo restante:</strong> ¡Mañana!</p>
        </div>
        
        <p>No olvides completar tu tarea a tiempo.</p>
        
        <p style="color: #7f8c8d; font-size: 12px; margin-top: 30px;">
            Este es un recordatorio automático del Sistema de Gestión de Tareas Escolares.
        </p>
    </div>
    """
    
    return send_email(correo, subject, html_content)
