# Guía Completa - Deploy en Render.com

## 🚀 Paso a Paso para Deploy

### 1. Preparar tu Repositorio en GitHub

Primero, sube tu proyecto a GitHub:

```bash
# Inicializar Git (si no lo has hecho)
git init

# Agregar todos los archivos
git add .

# Hacer commit
git commit -m "Configuración para deploy en Render"

# Crear repositorio en GitHub y conectarlo
git remote add origin https://github.com/TU_USUARIO/practica-scrum.git
git branch -M main
git push -u origin main
```

### 2. Crear Cuenta en Render.com

1. Ve a [https://render.com](https://render.com)
2. Haz clic en **"Get Started"**
3. Regístrate con tu cuenta de GitHub (recomendado)

### 3. Crear un Nuevo Web Service

1. En el dashboard de Render, haz clic en **"New +"**
2. Selecciona **"Web Service"**
3. Conecta tu repositorio de GitHub:
   - Autoriza a Render a acceder a tus repositorios
   - Selecciona el repositorio `practica-scrum`

### 4. Configurar el Web Service

Render detectará automáticamente que es un proyecto Node.js. Configura así:

**Configuración Básica:**
- **Name:** `practica-scrum` (o el nombre que prefieras)
- **Region:** Selecciona la más cercana a ti (ej: Oregon USA)
- **Branch:** `main`
- **Root Directory:** (dejar vacío)
- **Runtime:** `Node`

**Build & Deploy:**
- **Build Command:** `npm install`
- **Start Command:** `npm start`

**Plan:**
- Selecciona **"Free"** (gratis)

### 5. Variables de Entorno (Opcional)

Si necesitas configurar variables:
1. En la sección **"Environment"**
2. Agrega variables si las necesitas:
   - `NODE_ENV` → `production` (ya está en render.yaml)
   - `PORT` → Render lo asigna automáticamente

### 6. Deploy

1. Haz clic en **"Create Web Service"**
2. Render comenzará a:
   - Clonar tu repositorio
   - Instalar dependencias (`npm install`)
   - Compilar Angular automáticamente (postinstall)
   - Iniciar el servidor

### 7. Esperar el Deploy

- El primer deploy toma 5-10 minutos
- Verás logs en tiempo real
- Cuando veas "🚀 Servidor backend corriendo..." está listo

### 8. Acceder a tu Aplicación

Tu app estará disponible en:
```
https://practica-scrum.onrender.com
```
(o el nombre que hayas elegido)

## 📝 Actualizaciones Automáticas

Cada vez que hagas `git push` a GitHub:
1. Render detecta el cambio automáticamente
2. Hace un nuevo deploy
3. Tu app se actualiza sola

```bash
# Para actualizar tu app:
git add .
git commit -m "Descripción de cambios"
git push
```

## ⚠️ Importante - Plan Gratuito

**Limitaciones del plan gratuito:**
- El servicio "duerme" después de 15 minutos de inactividad
- Primer acceso después de dormir toma ~30 segundos
- 750 horas/mes gratis (suficiente para la mayoría)

**Cómo evitar que duerma:**
- Upgrade al plan de $7/mes
- Usa un servicio de "ping" para mantenerlo activo

## 🔍 Monitorear tu Aplicación

En el dashboard de Render puedes:
- Ver **Logs** en tiempo real
- Ver **Metrics** de uso
- Ver **Events** de deploy
- Configurar **Alertas**

## 🐛 Solución de Problemas

### Error: "Build failed"
```bash
# Verifica que compile localmente
npm install
npm run build
npm start
```

### Error: "Cannot find module"
- Asegúrate de que todas las dependencias estén en `package.json`
- Verifica que no uses dependencias de `devDependencies` en producción

### Error: "Application failed to respond"
- Verifica que el puerto sea `process.env.PORT` ✅ (ya está configurado)
- Revisa los logs en Render para ver el error exacto

### Archivos no encontrados
- Verifica que `dist/` se genere correctamente con `npm run build`
- Asegúrate de que `.gitignore` no excluya archivos necesarios

## 📊 Comandos Útiles

```bash
# Ver el estado de tu proyecto localmente
npm start

# Limpiar y reinstalar
rm -rf node_modules package-lock.json
npm install

# Forzar rebuild en Render
git commit --allow-empty -m "Trigger rebuild"
git push
```

## 🔗 Enlaces Importantes

- **Dashboard:** https://dashboard.render.com
- **Documentación:** https://render.com/docs
- **Status:** https://status.render.com

## 💡 Consejos

1. **Dominio personalizado:** Puedes conectar tu propio dominio gratis
2. **SSL:** Incluido automáticamente (HTTPS)
3. **Logs persistentes:** Se guardan por 7 días en plan gratuito
4. **Base de datos:** Puedes agregar PostgreSQL gratuito si lo necesitas

## ✅ Checklist Final

- [ ] Proyecto subido a GitHub
- [ ] Cuenta creada en Render.com
- [ ] Web Service creado y configurado
- [ ] Deploy completado exitosamente
- [ ] Aplicación accesible desde la URL
- [ ] Funcionalidad probada (login, tareas, etc.)

¡Tu aplicación ya está en producción! 🎉
