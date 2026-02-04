# Sistema de Gestión de Tareas Escolares

Aplicación Angular 20 + Django REST Framework con MySQL para gestión de tareas con login por rol (docente/estudiante), recuperación de contraseña por correo y recordatorios automáticos.

## Arquitectura

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Angular 20    │────▶│  Django + DRF   │────▶│  MySQL (XAMPP)  │
│   Puerto 4200   │     │   Puerto 3000   │     │   Puerto 3307   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Requisitos

- **Python 3.10+**
- **Node.js 18+** y npm
- **XAMPP** con MySQL corriendo en puerto **3307**
- Cuenta Gmail con contraseña de aplicación (para correos)

## Instalación

### 1. Base de datos MySQL

1. Inicia XAMPP y activa MySQL (puerto 3307)
2. Crea la base de datos:
   ```sql
   CREATE DATABASE sistema_tareas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

### 2. Backend Django

```bash
cd sistema_backend
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows PowerShell
pip install -r requirements.txt
python manage.py migrate
```

### 3. Frontend Angular

```bash
npm install
```

## Ejecución

### Backend Django (puerto 3000)

```bash
cd sistema_backend
.\venv\Scripts\Activate.ps1
python manage.py runserver 3000
```

### Frontend Angular (puerto 4200)

```bash
npm start
```

### Todo junto (2 terminales)

**Terminal 1 - Backend:**
```bash
cd sistema_backend && .\venv\Scripts\Activate.ps1 && python manage.py runserver 3000
```

**Terminal 2 - Frontend:**
```bash
npm start
```

## URLs

| Servicio | URL |
|----------|-----|
| Login Angular | http://localhost:4200 |
| Dashboard Docente | http://localhost:3000/src/screens/admin-dashboard.html |
| Dashboard Estudiante | http://localhost:3000/src/screens/student-dashboard.html |
| API REST | http://localhost:3000/api/ |

## API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/login` | Iniciar sesión |
| POST | `/api/register` | Registrar usuario |
| POST | `/api/forgot-password` | Solicitar código de recuperación |
| POST | `/api/verify-recovery-code` | Verificar código |
| POST | `/api/reset-password` | Restablecer contraseña |

## Configuración de correo

El servicio de correo está configurado en [sistema_backend/users/email_service.py](sistema_backend/users/email_service.py):

```python
GMAIL_USER = 'tu_email@gmail.com'
GMAIL_APP_PASSWORD = 'tu_contraseña_de_aplicación'
```

Para obtener una contraseña de aplicación:
1. Ve a [myaccount.google.com](https://myaccount.google.com)
2. Seguridad → Verificación en 2 pasos → Contraseñas de aplicación
3. Genera una contraseña para "Correo"

## Estructura del proyecto

```
practica_scrum/
├── sistema_backend/          # Backend Django
│   ├── config/               # Configuración Django
│   │   ├── settings.py       # MySQL, CORS, etc.
│   │   └── urls.py           # Rutas principales
│   ├── users/                # App de usuarios
│   │   ├── models.py         # User, RecoveryCode
│   │   ├── views.py          # Endpoints API
│   │   ├── serializers.py    # Validación DRF
│   │   ├── email_service.py  # Servicio de correo
│   │   └── urls.py           # Rutas /api/
│   ├── manage.py
│   └── requirements.txt
├── src/                      # Frontend Angular
│   ├── screens/              # Componentes de pantalla
│   │   ├── login.component.ts
│   │   ├── admin-dashboard.html
│   │   └── student-dashboard.html
│   ├── services/
│   │   └── auth.service.ts   # Servicio de autenticación
│   └── assets/
├── package.json
└── angular.json
```

## Modelos de base de datos

### User
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id_usuario | VARCHAR(20) | Clave primaria |
| password | VARCHAR(128) | Hash bcrypt |
| nombre_completo | VARCHAR(100) | Nombre del usuario |
| correo | VARCHAR(100) | Email único |
| telefono | VARCHAR(20) | Teléfono |
| sexo | VARCHAR(10) | Género |
| carrera | VARCHAR(100) | Carrera/área |
| rol | VARCHAR(20) | docente/estudiante |

### RecoveryCode
| Campo | Tipo | Descripción |
|-------|------|-------------|
| user | FK → User | Usuario asociado |
| code | VARCHAR(6) | Código de 6 dígitos |
| expires_at | DATETIME | Expira en 15 minutos |
| used | BOOLEAN | Si ya fue usado |

## Scripts útiles

```bash
# Compilar Angular a dist/
npm run build

# Ver usuarios registrados
cd sistema_backend
python manage.py shell -c "from users.models import User; print([u.correo for u in User.objects.all()])"

# Crear superusuario Django
python manage.py createsuperuser
```

## Notas de seguridad

- ✅ Contraseñas hasheadas con **bcrypt**
- ✅ Validación de contraseña: 8-15 caracteres, letra + número + símbolo
- ✅ Códigos de recuperación expiran en **15 minutos**
- ✅ Códigos de un solo uso
- ✅ CORS configurado solo para `localhost:4200`
- ✅ Sesión persistida en localStorage + cookie para compartir entre puertos

## Tecnologías

| Componente | Tecnología | Versión |
|------------|------------|---------|
| Frontend | Angular | 20 |
| Backend | Django | 4.2 |
| API | Django REST Framework | 3.16 |
| Base de datos | MySQL (XAMPP) | 8.0 |
| Conector DB | PyMySQL | 1.1 |
| Hash passwords | bcrypt | 4.2 |
| Correo | Gmail SMTP | - |
