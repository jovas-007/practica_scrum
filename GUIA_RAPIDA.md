# 🚀 Guía Rápida - Sistema de Gestión de Tareas BUAP

## ⚡ Inicio Rápido

### 1️⃣ Iniciar el Servidor

**Opción A - PowerShell:**
```powershell
.\iniciar-servidor.ps1
```

**Opción B - CMD:**
```cmd
iniciar-servidor.bat
```

**Opción C - Manual:**
```bash
node server.js
```

### 2️⃣ Acceder al Sistema

Una vez iniciado el servidor, abre tu navegador en:

**🔐 Login Principal:**
```
http://localhost:3000/src/index-angular.html
```

##  Usuarios de Prueba

### Administrador
- **ID:** `201912345`
- **Rol:** Administrador
- **Acceso a:** Panel de administración completo

### Estudiante
- **Matrícula:** `202268439`
- **Rol:** Estudiante  
- **Acceso a:** Ver y gestionar tareas asignadas

> **Nota:** Las contraseñas están hasheadas. Consulta el archivo `database/users.json`

## 📋 Crear Nueva Cuenta

1. En la pantalla de login, haz clic en **"Crear cuenta nueva"**
2. Selecciona el tipo de usuario:
   - ⭕ **Administrador**: Sin matrícula ni carrera
   - ⭕ **Estudiante**: Con matrícula (9 dígitos) y carrera
3. Completa el formulario según el rol seleccionado
4. Haz clic en **"Registrar"**

## 🎯 Diferencias entre Roles

### 👨‍💼 Administrador
**Formulario de Registro:**
- ID de Usuario (alfanumérico)
- Nombre Completo
- Correo Electrónico
- Teléfono
- Sexo
- Contraseña

**Dashboard:**
- Estadísticas del sistema
- Crear tareas (preparado)
- Ver todas las tareas (preparado)
- Gestionar estudiantes (preparado)
- Reportes (preparado)
- Configuración (preparado)

### 👨‍🎓 Estudiante
**Formulario de Registro:**
- Matrícula (9 dígitos numéricos)
- Nombre Completo
- Correo Electrónico
- Teléfono
- Sexo
- **Carrera** ✓
- Contraseña

**Dashboard:**
- Ver tareas asignadas
- Información académica
- Matrícula y carrera
- Recordatorios automáticos

## 🔄 Flujo de Uso

### Para Estudiantes:
```
1. Login → 
2. Dashboard Estudiante → 
3. Mis Tareas → 
4. Ver detalles de cada tarea
```

### Para Administradores:
```
1. Login → 
2. Dashboard Administrador → 
3. Opciones de gestión:
   - Crear tareas
   - Ver estadísticas
   - Gestionar estudiantes
   - Generar reportes
```

## 🗂️ Archivos Importantes

### Base de Datos
- `database/users.json` - Usuarios con roles
- `database/tasks.json` - Tareas del sistema

### Pantallas
- `src/screens/login.component.ts` - Login con selector de roles
- `src/screens/student-dashboard.html` - Dashboard estudiante
- `src/screens/admin-dashboard.html` - Dashboard administrador
- `src/screens/tareas.html` - Vista de tareas

### Servicios
- `src/services/auth.service.ts` - Autenticación con roles
- `server.js` - API backend
- `email.service.js` - Servicio de emails

## 🔧 Solución de Problemas

### El servidor no inicia
```bash
# Verifica que Node.js esté instalado
node --version

# Verifica las dependencias
npm install
```

### Error de autenticación
- Verifica que el archivo `database/users.json` exista
- Comprueba que las credenciales sean correctas
- Revisa la consola del navegador (F12)

### No se puede registrar usuario
- Verifica que todos los campos estén completos
- La matrícula debe ser de 9 dígitos (solo estudiantes)
- La contraseña debe tener 8-15 caracteres con letras, números y símbolos

### Pantalla en blanco
- Verifica que el servidor esté corriendo
- Abre la consola del navegador (F12) para ver errores
- Verifica la ruta: `http://localhost:3000/src/index-angular.html`

## 📞 Información de Contacto

**Institución:** Benemérita Universidad Autónoma de Puebla (BUAP)  
**Año:** 2026

## 📚 Documentación Adicional

- `CAMBIOS_ROLES.md` - Detalles de la implementación de roles
- `ESTRUCTURA.md` - Estructura completa del proyecto
- `README.md` - Documentación general

---

**¡Listo para usar! 🎉**

Para más información, consulta los archivos de documentación o revisa el código fuente.
