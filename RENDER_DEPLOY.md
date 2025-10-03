# Guía de Despliegue en Render.com

Esta guía te ayudará a desplegar tu aplicación Reflex de Asistente Legal Constitucional con IA en Render.com.

## 📋 Requisitos Previos

1. Cuenta en [Render.com](https://render.com)
2. Repositorio Git con el código (GitHub, GitLab, o Bitbucket)
3. Claves de API necesarias:
   - OpenAI API Key
   - AssemblyAI API Key
   - Tavily API Key

## 🗄️ Paso 1: Crear Base de Datos PostgreSQL

1. En el dashboard de Render, haz clic en **"New +"** → **"PostgreSQL"**
2. Configura la base de datos:
   - **Name**: `leyia-db` (o el nombre que prefieras)
   - **Database**: `leyia`
   - **User**: `leyia` (se crea automáticamente)
   - **Region**: Elige la región más cercana
   - **Plan**: Free (para pruebas) o Starter (para producción)
3. Haz clic en **"Create Database"**
4. **Importante**: Guarda la **Internal Database URL** (se usará más adelante)

## 🚀 Paso 2: Crear Web Service

1. En el dashboard de Render, haz clic en **"New +"** → **"Web Service"**
2. Conecta tu repositorio:
   - Autoriza Render a acceder a tu cuenta de Git
   - Selecciona el repositorio `leyiaweb`
3. Configura el servicio:
   - **Name**: `leyia-app` (o el nombre que prefieras)
   - **Region**: La misma que la base de datos
   - **Branch**: `main`
   - **Runtime**: **Docker**
   - **Plan**: Free (para pruebas) o Starter (para producción)

### Configuración de Build y Deploy:

**Build Command**: (Dejar vacío, Docker lo maneja)

**Start Command**: (Dejar vacío, usa el CMD del Dockerfile)

**Dockerfile Path**: `./Dockerfile`

## 🔐 Paso 3: Configurar Variables de Entorno

En la sección **"Environment"** del Web Service, agrega las siguientes variables:

### Variables Requeridas:

```bash
# Base de datos (copiar de PostgreSQL creado en Paso 1)
DATABASE_URL=postgresql://usuario:password@host:puerto/database

# APIs de IA
OPENAI_API_KEY=sk-tu-clave-de-openai
ASSEMBLYAI_API_KEY=tu-clave-de-assemblyai
TAVILY_API_KEY=tu-clave-de-tavily

# Configuración de Reflex
REFLEX_ENV=prod
RUN_MIGRATIONS=1
DB_WAIT_RETRIES=60
DB_WAIT_INTERVAL=2

# Puerto (Render lo configura automáticamente, pero puedes especificarlo)
PORT=8000
FRONTEND_PORT=3000

# PostgreSQL (si no usas DATABASE_URL completa)
POSTGRES_USER=leyia
POSTGRES_PASSWORD=tu-password
POSTGRES_DB=leyia
```

### Variables Opcionales (para mejor rendimiento):

```bash
# Redis (si agregas servicio Redis)
REDIS_URL=redis://tu-redis-host:puerto

# Frontend URL (se configura automáticamente)
FRONTEND_URL=https://tu-app.onrender.com

# Control de exportación de frontend
EXPORT_FRONTEND=0
```

## 💾 Paso 4: Configurar Disco Persistente (Opcional)

Para persistir archivos subidos:

1. En la configuración del Web Service, ve a **"Disks"**
2. Haz clic en **"Add Disk"**
3. Configura:
   - **Name**: `uploaded-files`
   - **Mount Path**: `/app/uploaded_files`
   - **Size**: 1GB o más según necesites
4. Guarda los cambios

## 🎯 Paso 5: Desplegar

1. Haz clic en **"Create Web Service"**
2. Render comenzará a:
   - Clonar el repositorio
   - Construir la imagen Docker
   - Ejecutar migraciones
   - Inicializar Reflex
   - Iniciar la aplicación

3. Monitorea los logs para verificar el progreso:
   ```
   🚀 Iniciando aplicación Reflex...
   ⏳ Esperando a que PostgreSQL esté listo...
   ✅ PostgreSQL está listo!
   🔄 Ejecutando migraciones de Alembic...
   ✅ Migraciones completadas
   🔧 Inicializando aplicación Reflex...
   ✅ Reflex inicializado correctamente
   🎯 Iniciando servidor Reflex...
   ```

## 🔍 Paso 6: Verificar el Despliegue

1. Una vez completado, Render te proporcionará una URL: `https://tu-app.onrender.com`
2. Visita la URL en tu navegador
3. Deberías ver la página de inicio del Asistente Legal

## 🔧 Solución de Problemas

### Error: Base de datos no disponible
- Verifica que `DATABASE_URL` esté correctamente configurada
- Asegúrate de usar la **Internal Database URL** de Render
- Revisa que la base de datos esté en estado "Available"

### Error: Migraciones fallan
- Revisa los logs para ver el error específico
- Puedes desactivar migraciones temporalmente: `RUN_MIGRATIONS=0`
- Conéctate a la base de datos y ejecuta migraciones manualmente

### Error: Frontend no carga
- Verifica que Node.js se instaló correctamente (revisa logs de build)
- Asegúrate de que el puerto 3000 esté abierto
- Revisa que `reflex init` se completó sin errores

### Error: Timeout durante el build
- El plan Free de Render tiene límites de tiempo de build
- Considera actualizar a un plan Starter
- Optimiza el Dockerfile si es necesario

### Error: APIs de IA no funcionan
- Verifica que las API keys sean correctas
- Revisa los logs para mensajes de error específicos
- Asegúrate de tener créditos en las cuentas de OpenAI/AssemblyAI/Tavily

## 📊 Monitoreo

### Logs en Tiempo Real:
```bash
# En el dashboard de Render, haz clic en "Logs"
# O usa el CLI de Render:
render logs -f tu-servicio
```

### Health Checks:
Render automáticamente verifica la salud de tu aplicación en:
- `http://tu-app.onrender.com/ping`

Si la app no responde, Render intentará reiniciarla automáticamente.

## 🔄 Actualizaciones

Para desplegar cambios:

1. Haz commit y push a tu rama `main`:
   ```bash
   git add .
   git commit -m "Actualización de la aplicación"
   git push origin main
   ```

2. Render detectará el cambio automáticamente y desplegará la nueva versión

### Despliegue Manual:
En el dashboard de Render, puedes hacer clic en **"Manual Deploy"** → **"Deploy latest commit"**

## 🛡️ Seguridad

### Recomendaciones:
- ✅ Usa HTTPS (Render lo proporciona automáticamente)
- ✅ No commitees archivos `.env` al repositorio
- ✅ Rota las API keys regularmente
- ✅ Usa secretos de Render para información sensible
- ✅ Habilita autenticación en tu aplicación
- ✅ Configura CORS apropiadamente

## 💰 Costos Estimados

### Plan Free:
- Web Service: $0/mes
- PostgreSQL: $0/mes
- Limitaciones: 
  - 750 horas/mes de cómputo
  - La app duerme después de 15 min de inactividad
  - 100GB ancho de banda
  - Build time limitado

### Plan Starter (Recomendado para producción):
- Web Service: ~$7/mes
- PostgreSQL: ~$7/mes
- Total: ~$14/mes
- Beneficios:
  - Sin sleep
  - Más recursos
  - Build time extendido
  - 100GB ancho de banda

## 📚 Recursos Adicionales

- [Documentación de Render](https://render.com/docs)
- [Documentación de Reflex](https://reflex.dev/docs)
- [Troubleshooting en Render](https://render.com/docs/troubleshooting)

## 🆘 Soporte

Si encuentras problemas:
1. Revisa los logs en el dashboard de Render
2. Consulta esta guía
3. Revisa la documentación de Render
4. Contacta al soporte de Render si el problema persiste

---

¡Feliz despliegue! 🚀
