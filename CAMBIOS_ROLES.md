# Sistema de Gestión de Tareas Escolares - BUAP

## 📋 Cambios Implementados

### ✅ Sistema de Roles
Se ha implementado un sistema completo de roles con dos tipos de usuario:

1. **Administrador** 👨‍💼
   - Sin campo de matrícula
   - Sin campo de carrera
   - Acceso a panel de administración
   - Puede gestionar tareas y estudiantes

2. **Estudiante** 👨‍🎓
   - Con campo de matrícula (9 dígitos)
   - Con campo de carrera
   - Acceso a panel de estudiante
   - Puede ver sus tareas asignadas

### 🗂️ Nueva Estructura de Carpetas

```
practica_scrum/
├── database/                    # Base de datos JSON
│   ├── users.json              # Usuarios con roles
│   └── tasks.json              # Tareas del sistema
│
├── src/
│   ├── screens/                # Pantallas de la aplicación
│   │   ├── login.component.ts         # Login con selector de roles
│   │   ├── student-dashboard.html     # Dashboard estudiante
│   │   ├── admin-dashboard.html       # Dashboard administrador
│   │   └── tareas.html                # Vista de tareas
│   │
│   ├── services/               # Servicios Angular
│   │   └── auth.service.ts     # Servicio de autenticación con roles
│   │
│   ├── assets/                 # Recursos estáticos
│   │   └── diseños.css         # Estilos del sistema
│   │
│   ├── app.component.ts        # Componente principal
│   ├── main.ts                 # Punto de entrada Angular
│   └── index-angular.html      # HTML principal
│
├── server.js                   # Servidor con rutas actualizadas
├── email.service.js            # Servicio de emails
└── package.json                # Dependencias
```

### 🎨 Selector de Tipo de Usuario

Al hacer clic en "Crear cuenta nueva" aparece un selector visual con dos opciones:
- ⭕ Administrador
- ⭕ Estudiante

El formulario se adapta dinámicamente según la selección:

**Para Estudiante:**
- Matrícula (9 dígitos numéricos)
- Nombre Completo
- Correo Electrónico
- Teléfono
- Sexo
- **Carrera** ✓
- Contraseña

**Para Administrador:**
- ID de Usuario (alfanumérico)
- Nombre Completo
- Correo Electrónico
- Teléfono
- Sexo
- ~~Carrera~~ (No requerido)
- Contraseña

### 🔄 Redirección según Rol

El sistema redirige automáticamente después del login:

- **Estudiante** → `student-dashboard.html`
  - Ver tareas asignadas
  - Información académica
  - Matrícula y carrera

- **Administrador** → `admin-dashboard.html`
  - Estadísticas del sistema
  - Crear nuevas tareas (preparado)
  - Gestionar estudiantes (preparado)
  - Ver todas las tareas (preparado)
  - Reportes y análisis (preparado)
  - Configuración (preparado)

### 🔐 Base de Datos Actualizada

El archivo `database/users.json` ahora incluye el campo `rol`:

```json
{
  "id_usuario": "202268439",
  "password": "...",
  "nombre_completo": "Jovany Solis Ortiz",
  "correo": "jovany.solis@alumno.buap.mx",
  "telefono": "2227654321",
  "sexo": "Masculino",
  "carrera": "Ingeniería en TI",
  "rol": "estudiante"
}
```

### 🛠️ Funcionalidades del Servicio de Autenticación

El servicio `auth.service.ts` ahora incluye:

- `isAdmin()`: Verifica si el usuario es administrador
- `isStudent()`: Verifica si el usuario es estudiante
- `getCurrentUser()`: Retorna datos del usuario incluyendo rol
- Gestión de sesión con localStorage
- Validación de roles en login y registro

### 📱 Pantallas Preparadas

#### Dashboard Estudiante
- ✅ Vista de información personal
- ✅ Acceso a tareas asignadas
- ✅ Información académica (carrera, matrícula)
- ✅ Recordatorios automáticos

#### Dashboard Administrador
- ✅ Estadísticas del sistema
- ✅ Panel de opciones administrativas
- 📝 Crear tareas (estructura preparada)
-  Gestionar estudiantes (estructura preparada)
- 📊 Reportes (estructura preparada)
- ⚙️ Configuración (estructura preparada)

### 🚀 Cómo Ejecutar

1. **Iniciar el servidor:**
   ```bash
   node server.js
   ```

2. **Acceder al sistema:**
   - Login: `http://localhost:3000/src/index-angular.html`
   - Dashboard Estudiante: `http://localhost:3000/src/screens/student-dashboard.html`
   - Dashboard Admin: `http://localhost:3000/src/screens/admin-dashboard.html`

###  Usuarios de Prueba

**Administrador:**
- ID: `201912345`
- Email: `admin@buap.mx`
- Contraseña: (la que hayas configurado)
- Rol: administrador

**Estudiante:**
- Matrícula: `202268439`
- Email: `jovany.solis@alumno.buap.mx`
- Contraseña: (la que hayas configurado)
- Rol: estudiante

### 📝 Próximos Pasos (Preparados pero No Implementados)

Para el administrador, las siguientes funcionalidades están preparadas en la interfaz:

1. **Crear Tareas**: Formulario para asignar tareas a estudiantes
2. **Ver Todas las Tareas**: Lista completa de tareas del sistema
3. **Gestionar Estudiantes**: CRUD de estudiantes
4. **Reportes**: Generación de reportes y estadísticas
5. **Configuración**: Ajustes del sistema
6. **Notificaciones**: Envío de mensajes a estudiantes

### 🎯 Validaciones Implementadas

- ✓ Rol obligatorio en registro
- ✓ Matrícula de 9 dígitos solo para estudiantes
- ✓ Campo carrera obligatorio solo para estudiantes
- ✓ Redirección automática según rol
- ✓ Verificación de rol en cada pantalla
- ✓ Protección de rutas según tipo de usuario

---

**Desarrollado para:** Benemérita Universidad Autónoma de Puebla (BUAP)
**Año:** 2026
