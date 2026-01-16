const express = require('express');
const cors = require('cors');
const fs = require('fs').promises;
const path = require('path');

const app = express();
const PORT = 3000;
const USERS_FILE = path.join(__dirname, 'users.json');

app.use(cors());
app.use(express.json());

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

// Login
app.post('/api/login', async (req, res) => {
  try {
    console.log('Login request:', req.body);
    const { id_usuario, password } = req.body;
    const users = await readUsers();
    console.log('Users in DB:', users);
    
    const user = users.find(u => 
      u.id_usuario === id_usuario && 
      u.password === password
    );

    if (user) {
      console.log('Login successful for:', user.id_usuario);
      res.json({ 
        success: true, 
        id_usuario: user.id_usuario,
        nombre_completo: user.nombre_completo
      });
    } else {
      console.log('Login failed for:', id_usuario);
      res.json({ success: false, message: 'Matrícula o contraseña incorrectos' });
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
    
    const existingUser = users.find(u => u.id_usuario === id_usuario);

    if (existingUser) {
      res.json({ success: false, message: 'La matrícula ya está registrada' });
    } else {
      users.push({ id_usuario, password, nombre_completo, correo, telefono, sexo, carrera });
      await saveUsers(users);
      res.json({ success: true });
    }
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

// Iniciar servidor
initUsersFile().then(() => {
  app.listen(PORT, () => {
    console.log(`🚀 Servidor backend corriendo en http://localhost:${PORT}`);
    console.log(`📁 Usuarios guardados en: ${USERS_FILE}`);
  });
});
