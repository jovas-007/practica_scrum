const express = require('express');
const cors = require('cors');
const bcrypt = require('bcrypt');
const fs = require('fs').promises;
const path = require('path');
const { startReminderScheduler, testReminders } = require('./email.service');

const app = express();
const PORT = process.env.PORT || 3000;
const USERS_FILE = path.join(__dirname, 'users.json');
const TASKS_FILE = path.join(__dirname, 'tasks.json');
const SALT_ROUNDS = 10;

app.use(cors());
app.use(express.json());

// Servir archivos estáticos de Angular (producción)
app.use(express.static(path.join(__dirname, 'dist')));

// Inicializar archivo de usuarios si no existe
async function initUsersFile() {
  try {
    await fs.access(USERS_FILE);
  } catch {
    const defaultUsers = [
      { 
        id_usuario: '201912345',
        password: 'admin123',
        nombre_completo: 'Administrador Sistema',
        correo: 'admin@buap.mx',
        telefono: '2221234567',
        sexo: 'Masculino',
        carrera: 'Ingeniería en TI'
      },
      { 
        id_usuario: '201987654',
        password: 'jovany2026',
        nombre_completo: 'Jovany Solis Ortiz',
        correo: 'jovany.solis@alumno.buap.mx',
        telefono: '2227654321',
        sexo: 'Masculino',
        carrera: 'Ingeniería en TI'
      }
    ];
    await fs.writeFile(USERS_FILE, JSON.stringify(defaultUsers, null, 2));
  }
}

// Leer usuarios
async function readUsers() {
  const data = await fs.readFile(USERS_FILE, 'utf8');
  return JSON.parse(data);
}

// Guardar usuarios
async function saveUsers(users) {
  await fs.writeFile(USERS_FILE, JSON.stringify(users, null, 2));
}

// Leer tareas
async function readTasks() {
  const data = await fs.readFile(TASKS_FILE, 'utf8');
  return JSON.parse(data);
}

// Guardar tareas
async function saveTasks(tasks) {
  await fs.writeFile(TASKS_FILE, JSON.stringify(tasks, null, 2));
}

// Inicializar archivo de tareas si no existe
async function initTasksFile() {
  try {
    await fs.access(TASKS_FILE);
  } catch {
    const defaultTasks = [];
    await fs.writeFile(TASKS_FILE, JSON.stringify(defaultTasks, null, 2));
  }
}

// Login
app.post('/api/login', async (req, res) => {
  try {
    console.log('Login request:', req.body);
    const { id_usuario, password } = req.body;
    const users = await readUsers();
    
    // Buscar por matrícula o correo
    const user = users.find(u => 
      u.id_usuario === id_usuario || u.correo.toLowerCase() === id_usuario.toLowerCase()
    );

    if (user) {
      // Comparar contraseña con hash
      const passwordMatch = await bcrypt.compare(password, user.password);
      
      if (passwordMatch) {
        console.log('Login successful for:', user.id_usuario);
        res.json({ 
          success: true, 
          id_usuario: user.id_usuario,
          nombre_completo: user.nombre_completo
        });
      } else {
        console.log('Login failed - incorrect password for:', id_usuario);
        res.json({ success: false, message: 'Matrícula/Correo o contraseña incorrectos' });
      }
    } else {
      console.log('Login failed - user not found:', id_usuario);
      res.json({ success: false, message: 'Matrícula/Correo o contraseña incorrectos' });
    }
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ success: false, message: 'Error en el servidor' });
  }
});

// Registro
app.post('/api/register', async (req, res) => {
  try {
    const { id_usuario, password, nombre_completo, correo, telefono, sexo, carrera } = req.body;
    const users = await readUsers();
    
    // Verificar si la matrícula ya existe
    const existingUser = users.find(u => u.id_usuario === id_usuario);
    if (existingUser) {
      return res.json({ success: false, message: 'La matrícula ya está registrada' });
    }

    // Verificar si el correo ya existe
    const existingEmail = users.find(u => u.correo.toLowerCase() === correo.toLowerCase());
    if (existingEmail) {
      return res.json({ success: false, message: 'El correo electrónico ya está registrado' });
    }

    // Validar formato de correo
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailRegex.test(correo)) {
      return res.json({ success: false, message: 'Formato de correo electrónico inválido' });
    }

    // Validar formato de contraseña
    if (!password || password.length < 8 || password.length > 15) {
      return res.json({ success: false, message: 'La contraseña debe tener entre 8 y 15 caracteres' });
    }

    if (!/[a-zA-Z]/.test(password)) {
      return res.json({ success: false, message: 'La contraseña debe contener al menos una letra' });
    }

    if (!/[0-9]/.test(password)) {
      return res.json({ success: false, message: 'La contraseña debe contener al menos un número' });
    }

    if (!/[^a-zA-Z0-9]/.test(password)) {
      return res.json({ success: false, message: 'La contraseña debe contener al menos un signo especial' });
    }

    // Hashear contraseña antes de guardar
    const hashedPassword = await bcrypt.hash(password, SALT_ROUNDS);

    users.push({ id_usuario, password: hashedPassword, nombre_completo, correo, telefono, sexo, carrera });
    await saveUsers(users);
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ success: false, message: 'Error en el servidor' });
  }
});

// Obtener todos los usuarios (solo para desarrollo)
app.get('/api/users', async (req, res) => {
  try {
    const users = await readUsers();
    res.json(users);
  } catch (error) {
    res.status(500).json({ error: 'Error en el servidor' });
  }
});

// ========== ENDPOINTS DE TAREAS ==========

// Obtener todas las tareas
app.get('/api/tasks', async (req, res) => {
  try {
    const tasks = await readTasks();
    res.json(tasks);
  } catch (error) {
    res.status(500).json({ error: 'Error al obtener tareas' });
  }
});

// Obtener tareas de un usuario específico
app.get('/api/tasks/user/:id', async (req, res) => {
  try {
    const userId = req.params.id;
    const tasks = await readTasks();
    const userTasks = tasks.filter(task => 
      task.usuarios_asignados.includes(userId)
    );
    res.json(userTasks);
  } catch (error) {
    res.status(500).json({ error: 'Error al obtener tareas del usuario' });
  }
});

// Crear nueva tarea
app.post('/api/tasks', async (req, res) => {
  try {
    const { nombre_tarea, materia, fecha_entrega, usuarios_asignados } = req.body;
    const tasks = await readTasks();
    
    const newTask = {
      id_tarea: `TAREA${String(tasks.length + 1).padStart(3, '0')}`,
      nombre_tarea,
      materia,
      fecha_entrega,
      usuarios_asignados
    };
    
    tasks.push(newTask);
    await saveTasks(tasks);
    res.json({ success: true, task: newTask });
  } catch (error) {
    res.status(500).json({ success: false, message: 'Error al crear tarea' });
  }
});

// Actualizar tarea
app.put('/api/tasks/:id', async (req, res) => {
  try {
    const taskId = req.params.id;
    const tasks = await readTasks();
    const taskIndex = tasks.findIndex(t => t.id_tarea === taskId);
    
    if (taskIndex !== -1) {
      tasks[taskIndex] = { ...tasks[taskIndex], ...req.body };
      await saveTasks(tasks);
      res.json({ success: true, task: tasks[taskIndex] });
    } else {
      res.status(404).json({ success: false, message: 'Tarea no encontrada' });
    }
  } catch (error) {
    res.status(500).json({ success: false, message: 'Error al actualizar tarea' });
  }
});

// Eliminar tarea
app.delete('/api/tasks/:id', async (req, res) => {
  try {
    const taskId = req.params.id;
    const tasks = await readTasks();
    const filteredTasks = tasks.filter(t => t.id_tarea !== taskId);
    
    if (filteredTasks.length < tasks.length) {
      await saveTasks(filteredTasks);
      res.json({ success: true, message: 'Tarea eliminada' });
    } else {
      res.status(404).json({ success: false, message: 'Tarea no encontrada' });
    }
  } catch (error) {
    res.status(500).json({ success: false, message: 'Error al eliminar tarea' });
  }
});

// Endpoint para probar el envío de recordatorios manualmente
app.post('/api/test-reminders', async (req, res) => {
  try {
    await testReminders();
    res.json({ success: true, message: 'Recordatorios de prueba enviados' });
  } catch (error) {
    res.status(500).json({ success: false, message: 'Error al enviar recordatorios' });
  }
});

// Endpoint para recuperar contraseña
app.post('/api/forgot-password', async (req, res) => {
  try {
    const { correo } = req.body;
    const users = await readUsers();
    
    const user = users.find(u => u.correo.toLowerCase() === correo.toLowerCase());
    
    if (user) {
      // Generar código de recuperación
      const { generateRecoveryCode, sendRecoveryCodeEmail, recoveryCodes } = require('./email.service');
      const code = generateRecoveryCode();
      
      // Guardar código con expiración de 15 minutos
      const expires = Date.now() + 15 * 60 * 1000;
      recoveryCodes.set(correo.toLowerCase(), { 
        code, 
        expires,
        id_usuario: user.id_usuario 
      });
      
      // Enviar email con el código
      await sendRecoveryCodeEmail(user, code);
      res.json({ success: true, message: 'Código de recuperación enviado al correo' });
    } else {
      res.json({ success: false, message: 'El correo no está registrado en el sistema' });
    }
  } catch (error) {
    console.error('Error en recuperación de contraseña:', error);
    res.status(500).json({ success: false, message: 'Error al recuperar contraseña' });
  }
});

// Verificar código de recuperación
app.post('/api/verify-recovery-code', async (req, res) => {
  try {
    const { correo, code } = req.body;
    const { recoveryCodes } = require('./email.service');
    
    const storedData = recoveryCodes.get(correo.toLowerCase());
    
    if (!storedData) {
      return res.json({ success: false, message: 'No hay código de recuperación activo para este correo' });
    }
    
    if (Date.now() > storedData.expires) {
      recoveryCodes.delete(correo.toLowerCase());
      return res.json({ success: false, message: 'El código ha expirado. Solicita uno nuevo' });
    }
    
    if (storedData.code !== code) {
      return res.json({ success: false, message: 'Código incorrecto' });
    }
    
    res.json({ success: true, message: 'Código verificado correctamente' });
  } catch (error) {
    console.error('Error al verificar código:', error);
    res.status(500).json({ success: false, message: 'Error al verificar código' });
  }
});

// Cambiar contraseña con código verificado
app.post('/api/reset-password', async (req, res) => {
  try {
    const { correo, code, newPassword } = req.body;
    const { recoveryCodes } = require('./email.service');
    
    const storedData = recoveryCodes.get(correo.toLowerCase());
    
    if (!storedData) {
      return res.json({ success: false, message: 'No hay código de recuperación activo' });
    }
    
    if (Date.now() > storedData.expires) {
      recoveryCodes.delete(correo.toLowerCase());
      return res.json({ success: false, message: 'El código ha expirado' });
    }
    
    if (storedData.code !== code) {
      return res.json({ success: false, message: 'Código incorrecto' });
    }
    
    // Validar formato de nueva contraseña
    if (!newPassword || newPassword.length < 8 || newPassword.length > 15) {
      return res.json({ success: false, message: 'La contraseña debe tener entre 8 y 15 caracteres' });
    }

    if (!/[a-zA-Z]/.test(newPassword)) {
      return res.json({ success: false, message: 'La contraseña debe contener al menos una letra' });
    }

    if (!/[0-9]/.test(newPassword)) {
      return res.json({ success: false, message: 'La contraseña debe contener al menos un número' });
    }

    if (!/[^a-zA-Z0-9]/.test(newPassword)) {
      return res.json({ success: false, message: 'La contraseña debe contener al menos un signo especial' });
    }
    
    // Actualizar contraseña
    const users = await readUsers();
    const userIndex = users.findIndex(u => u.correo.toLowerCase() === correo.toLowerCase());
    
    if (userIndex === -1) {
      return res.json({ success: false, message: 'Usuario no encontrado' });
    }
    
    // Hashear nueva contraseña
    const hashedPassword = await bcrypt.hash(newPassword, SALT_ROUNDS);
    users[userIndex].password = hashedPassword;
    await saveUsers(users);
    
    // Eliminar código usado
    recoveryCodes.delete(correo.toLowerCase());
    
    res.json({ success: true, message: 'Contraseña actualizada correctamente' });
  } catch (error) {
    console.error('Error al cambiar contraseña:', error);
    res.status(500).json({ success: false, message: 'Error al cambiar contraseña' });
  }
});

// Ruta catch-all: servir index.html para todas las rutas no API
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'dist', 'index-angular.html'));
});

// Iniciar servidor
initUsersFile()
  .then(() => initTasksFile())
  .then(() => {
    app.listen(PORT, () => {
      console.log(`🚀 Servidor backend corriendo en http://localhost:${PORT}`);
      console.log(`📁 Usuarios guardados en: ${USERS_FILE}`);
      console.log(`📋 Tareas guardadas en: ${TASKS_FILE}`);
      
      // Iniciar el scheduler de recordatorios
      startReminderScheduler();
    });
  });
