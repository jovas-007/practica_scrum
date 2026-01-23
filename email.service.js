const nodemailer = require('nodemailer');
const cron = require('node-cron');
const fs = require('fs').promises;
const path = require('path');

const TASKS_FILE = path.join(__dirname, 'tasks.json');
const USERS_FILE = path.join(__dirname, 'users.json');

// Configuración del transporte de email
// IMPORTANTE: Usa Gmail con contraseña de aplicación
// Para crear contraseña de aplicación de Gmail:
// 1. Ve a https://myaccount.google.com/security
// 2. Activa verificación en 2 pasos
// 3. Busca "Contraseñas de aplicaciones"
// 4. Genera una para "Correo"
const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: 'secretaria.instituto.aca@gmail.com',  // ← Cambia esto por tu Gmail
    pass: 'ffhd mnft jbnj cglc'     // ← Cambia esto por tu contraseña de aplicación de Gmail (16 caracteres)
  }
});

// Leer tareas
async function readTasks() {
  const data = await fs.readFile(TASKS_FILE, 'utf8');
  return JSON.parse(data);
}

// Leer usuarios
async function readUsers() {
  const data = await fs.readFile(USERS_FILE, 'utf8');
  return JSON.parse(data);
}

// Función para enviar email de recordatorio
async function sendReminderEmail(task, user) {
  const fechaEntrega = new Date(task.fecha_entrega);
  const fechaFormateada = fechaEntrega.toLocaleString('es-MX', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });

  const mailOptions = {
    from: 'secretaria.instituto.aca@gmail.com', // Debe coincidir con el email configurado arriba
    to: user.correo,
    subject: `Recordatorio: Tarea "${task.nombre_tarea}" - Entrega mañana`,
    html: `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #2c3e50;">📚 Recordatorio de Tarea</h2>
        <p>Hola <strong>${user.nombre_completo}</strong>,</p>
        
        <p>Te recordamos que tienes una tarea próxima a vencer:</p>
        
        <div style="background-color: #f8f9fa; padding: 20px; border-left: 4px solid #3498db; margin: 20px 0;">
          <h3 style="margin-top: 0; color: #3498db;">${task.nombre_tarea}</h3>
          <p><strong>📖 Materia:</strong> ${task.materia}</p>
          <p><strong>📅 Fecha de entrega:</strong> ${fechaFormateada}</p>
          <p><strong>⏰ Tiempo restante:</strong> ¡Mañana!</p>
        </div>
        
        <p>No olvides completar tu tarea a tiempo.</p>
        
        <p style="color: #7f8c8d; font-size: 12px; margin-top: 30px;">
          Este es un recordatorio automático del Sistema de Gestión de Tareas Escolares.
        </p>
      </div>
    `
  };

  try {
    await transporter.sendMail(mailOptions);
    console.log(`✅ Email enviado a ${user.correo} para la tarea: ${task.nombre_tarea}`);
    return true;
  } catch (error) {
    console.error(`❌ Error al enviar email a ${user.correo}:`, error.message);
    return false;
  }
}

// Verificar tareas que vencen mañana y enviar recordatorios
async function checkAndSendReminders() {
  try {
    const tasks = await readTasks();
    const users = await readUsers();
    
    const ahora = new Date();
    const mañana = new Date(ahora);
    mañana.setDate(ahora.getDate() + 1);
    mañana.setHours(0, 0, 0, 0);
    
    const pasadoMañana = new Date(mañana);
    pasadoMañana.setDate(mañana.getDate() + 1);

    console.log(`\n🔍 Verificando tareas... (${ahora.toLocaleString('es-MX')})`);

    for (const task of tasks) {
      const fechaEntrega = new Date(task.fecha_entrega);
      
      // Si la tarea vence mañana
      if (fechaEntrega >= mañana && fechaEntrega < pasadoMañana) {
        console.log(`\n📌 Tarea próxima a vencer: ${task.nombre_tarea}`);
        
        // Enviar email a cada usuario asignado
        for (const userId of task.usuarios_asignados) {
          const user = users.find(u => u.id_usuario === userId);
          if (user) {
            await sendReminderEmail(task, user);
          }
        }
      }
    }
  } catch (error) {
    console.error('❌ Error al verificar tareas:', error);
  }
}

// Programar verificación diaria a las 9:00 AM
function startReminderScheduler() {
  // Ejecutar cada día a las 9:00 AM
  cron.schedule('0 9 * * *', () => {
    console.log('\n⏰ Ejecutando verificación programada de tareas...');
    checkAndSendReminders();
  });

  console.log('✅ Scheduler de recordatorios iniciado - Verificará tareas diariamente a las 9:00 AM');
}

// Función para probar el envío inmediato (útil para desarrollo)
async function testReminders() {
  console.log('\n🧪 Ejecutando prueba de recordatorios...');
  await checkAndSendReminders();
}

// Función para enviar contraseña por email
async function sendPasswordEmail(user) {
  const mailOptions = {
    from: 'secretaria.instituto.aca@gmail.com',
    to: user.correo,
    subject: '🔑 Recuperación de Contraseña - Sistema de Gestión de Tareas',
    html: `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #2c3e50;">🔑 Recuperación de Contraseña</h2>
        <p>Hola <strong>${user.nombre_completo}</strong>,</p>
        
        <p>Has solicitado recuperar tu contraseña. Aquí están tus datos de acceso:</p>
        
        <div style="background-color: #f8f9fa; padding: 20px; border-left: 4px solid #3498db; margin: 20px 0;">
          <p><strong>📋 Matrícula:</strong> ${user.id_usuario}</p>
          <p><strong>🔐 Contraseña:</strong> ${user.password}</p>
        </div>
        
        <p style="color: #e74c3c; font-weight: bold;">
          ⚠️ Por seguridad, te recomendamos cambiar tu contraseña después de iniciar sesión.
        </p>
        
        <p>Si no solicitaste esta recuperación, por favor ignora este mensaje.</p>
        
        <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 30px 0;">
        
        <p style="color: #7f8c8d; font-size: 12px;">
          Este es un mensaje automático del Sistema de Gestión de Tareas Escolares - BUAP.
          <br>Por favor, no respondas a este correo.
        </p>
      </div>
    `
  };

  try {
    await transporter.sendMail(mailOptions);
    console.log(`✅ Contraseña enviada a ${user.correo}`);
    return true;
  } catch (error) {
    console.error(`❌ Error al enviar contraseña a ${user.correo}:`, error.message);
    return false;
  }
}

module.exports = {
  startReminderScheduler,
  checkAndSendReminders,
  testReminders,
  sendReminderEmail,
  sendPasswordEmail
};
