# Sistema de Gestión de Tareas Escolares

Aplicación Angular + Node/Express para gestión de tareas con login por rol (docente/estudiante), recuperación de contraseña y recordatorios por correo.

## Requisitos

- Node.js 18+
- npm
- Cuenta Gmail con contraseña de aplicación (para recordatorios)

## Instalación

```bash
npm install
```

## Ejecución

- Todo junto (frontend 4200 + backend 3000):
   ```bash
   npm run dev
   ```
- Solo frontend:
   ```bash
   npm start
   ```
- Solo backend:
   ```bash
   npm run server
   ```

## URLs

- Login Angular: http://localhost:4200
- Dashboards servidos por el backend (se redirige tras login):
   - Docente: http://localhost:3000/src/screens/admin-dashboard.html
   - Estudiante: http://localhost:3000/src/screens/student-dashboard.html

## Configurar correo

Edita [email.service.js](email.service.js) y coloca tus credenciales Gmail de app password:

```js
user: 'tu_email@gmail.com',
pass: 'tu_contraseña_de_aplicación'
```

Recordatorios automáticos: cron diario a las 10:00 AM; botón de prueba en el dashboard docente.

## Estructura breve

- [src/screens/login.component.ts](src/screens/login.component.ts): login/registro/recuperación.
- [src/services/auth.service.ts](src/services/auth.service.ts): autenticación y sesión (localStorage + cookie para compartir puertos).
- [src/screens/admin-dashboard.html](src/screens/admin-dashboard.html) y [src/screens/student-dashboard.html](src/screens/student-dashboard.html): vistas según rol.
- [server.js](server.js): API Express + estáticos /src + recordatorios por correo.
- [database/users.json](database/users.json), [database/tasks.json](database/tasks.json): persistencia simple.

## Scripts útiles

- `npm run build`: compila Angular a `dist/`.
- `npm test`: no aplica (sin tests configurados).

## Notas de seguridad

- Contraseñas guardadas con bcrypt en backend.
- Reglas de contraseña: 8-15 caracteres, al menos 1 letra, 1 número y 1 símbolo.
- Sesión se persiste en localStorage y cookie `currentUser` para que los dashboards en `:3000` reconozcan el login hecho en `:4200`.
