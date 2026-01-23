# Sistema de Gestión de Tareas Escolares - Práctica SCRUM

Sistema completo de gestión de tareas con autenticación, recordatorios automáticos por email y recuperación de contraseña desarrollado con Angular y Node.js/Express.

## 📋 Requisitos Previos

- [Node.js](https://nodejs.org/) (versión 18 o superior)
- [npm](https://www.npmjs.com/) (se instala automáticamente con Node.js)
- Cuenta de Gmail con contraseña de aplicación (para recordatorios por email)

## 🚀 Instalación

1. **Clona o descarga el proyecto**

2. **Instala las dependencias**

   ```bash
   npm install
   ```

   Esto instalará:
   - Angular 20
   - Express 4.18.2
   - bcrypt (para hash de contraseñas)
   - nodemailer (para envío de emails)
   - node-cron (para tareas programadas)
   - cors, body-parser, etc.

## ⚙️ Configuración de Email

**IMPORTANTE**: Para que funcionen los recordatorios por email:

1. Edita `email.service.js` (líneas 18-19)
2. Configura tu Gmail:
   ```javascript
   user: 'tu_email@gmail.com',
   pass: 'tu_contraseña_de_aplicación'
   ```

3. Para obtener contraseña de aplicación de Gmail:
   - Ve a https://myaccount.google.com/security
   - Activa verificación en 2 pasos
   - Busca "Contraseñas de aplicaciones"
   - Genera una para "Correo"

## ▶️ Cómo Ejecutar el Proyecto

Tienes tres opciones para ejecutar el proyecto:

### Opción 1: Ejecutar Frontend y Backend simultáneamente (Recomendado)

```bash
npm run dev
```

Este comando ejecuta tanto el servidor backend como el frontend de Angular al mismo tiempo.

- **Backend**: Se ejecutará en `http://localhost:3000`
- **Frontend**: Se ejecutará en `http://localhost:4200`

### Opción 2: Ejecutar solo el Frontend

```bash
npm start
```

El frontend estará disponible en `http://localhost:4200`

### Opción 3: Ejecutar solo el Backend

```bash
npm run server
```

El servidor backend estará disponible en `http://localhost:3000`

## 📁 Estructura del Proyecto

```
practica_scrum/
├── src/                      # Código fuente de Angular
│   ├── app.component.ts      # Componente principal
│   ├── auth.service.ts       # Servicio de autenticación
│   ├── login.component.ts    # Componente de login
│   ├── main.ts              # Punto de entrada de Angular
│   └── ...
├── server.js                # Servidor backend Express
├── users.json              # Base de datos de usuarios (JSON)
├── package.json            # Dependencias del proyecto
├── angular.json            # Configuración de Angular
└── tsconfig.json           # Configuración de TypeScript
```

## 🔐 Requisitos de Contraseña

Al registrarse o cambiar contraseña:
- Entre 8 y 15 caracteres
- Al menos una letra (mayúscula o minúscula)
- Al menos un número
- Al menos un símbolo especial (cualquiera: @#$%^&*()!_.-+, etc.)

## 🛠️ Scripts Disponibles

- `npm start` - Inicia el servidor de desarrollo de Angular
- `npm run server` - Inicia el servidor backend
- `npm run dev` - Inicia frontend y backend simultáneamente
- `npm run build` - Compila el proyecto Angular para producción

## 📝 Endpoints del API

### Autenticación
- `POST /api/login` - Autenticación de usuarios (verifica hash con bcrypt)
- `POST /api/register` - Registro de nuevos usuarios (hashea contraseña)
- `POST /api/forgot-password` - Solicitar código de recuperación por email
- `POST /api/verify-recovery-code` - Verificar código de 6 dígitos
- `POST /api/reset-password` - Cambiar contraseña con código válido

### Usuarios
- `GET /api/users` - Obtener lista de usuarios

### Tareas
- `GET /api/tasks` - Obtener todas las tareas
- `GET /api/tasks/user/:id` - Obtener tareas de un usuario específico
- `POST /api/tasks` - Crear nueva tarea
- `PUT /api/tasks/:id` - Actualizar tarea existente
- `DELETE /api/tasks/:id` - Eliminar tarea

### Recordatorios
- `POST /api/test-reminders` - Probar envío manual de recordatorios

## 🔔 Sistema de Recordatorios

- **Automático**: Verificación diaria a las 10:00 AM
- **Envío**: Emails 24 horas antes de cada fecha de entrega
- **Manual**: Botón "Probar Recordatorios" en pantalla de tareas
- **Configuración**: Requiere Gmail configurado en `email.service.js`

## 🔒 Seguridad Implementada

1. **Hash de Contraseñas**: bcrypt con 10 salt rounds
2. **Validación de Contraseñas**: Requisitos estrictos (letra, número, símbolo)
3. **Recuperación Segura**: Código de 6 dígitos con expiración de 15 minutos
4. **Sesión**: localStorage para mantener sesión activa

## 🖥️ Pantallas de la Aplicación

1. **Login**: Inicio de sesión con matrícula o correo
2. **Registro**: Creación de cuenta con validaciones
3. **Recuperar Contraseña**: 
   - Solicitar código por email
   - Verificar código de 6 dígitos
   - Establecer nueva contraseña
4. **Pantalla de Inicio**: Menú principal con información del usuario
5. **Mis Tareas**: Gestión completa de tareas asignadas

## ⚙️ Configuración Adicional

**Email Service** (`email.service.js`):
- Configurar credenciales de Gmail (líneas 18-19)
- Horario de verificación automática (línea 133): `'0 10 * * *'` = 10:00 AM
- Códigos de recuperación expiran en 15 minutos

**Tareas** (`tasks.json`):
- Formato de fecha: ISO 8601 (YYYY-MM-DDTHH:mm:ss)
- Usuarios asignados: array de matrículas

## 🐛 Solución de Problemas

### Error: Puerto en uso

- **Frontend (4200)**: Cierra otras instancias o cambia en `angular.json`
- **Backend (3000)**: Cierra aplicaciones o modifica `PORT` en `server.js`

### Error: Módulos no encontrados

```bash
npm install
```

### Emails no se envían

1. Verifica credenciales de Gmail en `email.service.js`
2. Asegúrate de usar contraseña de aplicación (no tu contraseña normal)
3. Revisa que la verificación en 2 pasos esté activa
4. Consulta la consola del servidor para errores específicos

### Error al iniciar sesión después de actualizar

Las contraseñas ahora están hasheadas. Si actualizaste desde versión anterior, las contraseñas en texto plano no funcionarán. Opciones:
1. Crear nuevo usuario con el sistema de registro
2. Usar usuarios predeterminados (contraseñas ya hasheadas)

## 🎨 Características Adicionales

- ✅ Interfaz responsive con gradientes azules institucionales
- ✅ Botones reactivos con efectos hover y active
- ✅ Validación de formularios en frontend y backend
- ✅ Mensajes de error/éxito amigables
- ✅ Información académica personalizada por usuario
- ✅ Cierre de sesión seguro

## 📞 Soporte

Si encuentras algún problema, verifica:

1. Que Node.js esté correctamente instalado: `node --version`
2. Que npm esté instalado: `npm --version`
3. Que todas las dependencias estén instaladas: `npm install`
4. Que los puertos 3000 y 4200 estén disponibles

## 📄 Licencia

Este proyecto es parte de una práctica académica.
