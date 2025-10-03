# 🔧 Corrección para Despliegue en Render

## Problema Identificado

El despliegue se quedó esperando la conexión a la base de datos PostgreSQL.

**DATABASE_URL de Render**: `postgresql://leyia_postgres_user:9OwLTwxOiZeXyfZCY5yQWtzkKhwaPKtA@dpg-d3c645r7mgec73a8kri0-a/leyia_postgres`

## Cambios Realizados

### 1. Mejora del Script de Espera de Base de Datos

Se actualizó el `Dockerfile` con:

- ✅ Mejor parseo de URLs de PostgreSQL de Render
- ✅ Soporte para hostnames con sufijo `-a` (red interna de Render)
- ✅ Soporte para URLs sin puerto explícito (usa 5432 por defecto)
- ✅ Aumento de reintentos: de 60 a 90
- ✅ Aumento de intervalo: de 2s a 3s
- ✅ Mejor logging de errores

### 2. Variables de Entorno Actualizadas

El script ahora extrae correctamente:
- **Host**: `dpg-d3c645r7mgec73a8kri0-a`
- **Puerto**: `5432` (por defecto)
- **Usuario**: `leyia_postgres_user`
- **Database**: `leyia_postgres`

## 📋 Pasos para Actualizar el Despliegue

### Opción 1: Push de Cambios (Recomendado)

```bash
# 1. Agregar cambios
git add Dockerfile

# 2. Commit
git commit -m "Fix: Mejorar conexión a PostgreSQL de Render"

# 3. Push (esto disparará un nuevo despliegue automático)
git push origin main
```

### Opción 2: Manual Deploy en Render

1. Ve al dashboard de Render
2. Selecciona tu Web Service
3. Haz clic en **"Manual Deploy"** → **"Clear build cache & deploy"**

## 🔐 Verificar Variables de Entorno en Render

Asegúrate de que estas variables estén configuradas:

```bash
# CRÍTICAS
DATABASE_URL=postgresql://leyia_postgres_user:9OwLTwxOiZeXyfZCY5yQWtzkKhwaPKtA@dpg-d3c645r7mgec73a8kri0-a/leyia_postgres
OPENAI_API_KEY=tu-clave
ASSEMBLYAI_API_KEY=tu-clave
TAVILY_API_KEY=tu-clave

# CONFIGURACIÓN
REFLEX_ENV=prod
RUN_MIGRATIONS=1

# TIMEOUTS (INCREMENTADOS)
DB_WAIT_RETRIES=90
DB_WAIT_INTERVAL=3

# PUERTOS (Render los configura automáticamente)
PORT=8000
FRONTEND_PORT=3000
```

## 🔍 Qué Esperar en los Logs

Después del despliegue, deberías ver:

```
🚀 Iniciando aplicación Reflex...
⏳ Esperando a que PostgreSQL esté listo...
🔍 DATABASE_URL detectada
🔍 DB Host: dpg-d3c645r7mgec73a8kri0-a
🔍 DB Port: 5432
🔍 DB User: leyia_postgres_user
🔍 DB Name: leyia_postgres
⏳ Intentando conectar a PostgreSQL (máximo 90 intentos)...
⏳ Intento 1/90: PostgreSQL no está listo. Esperando 3s...
⏳ Intento 2/90: PostgreSQL no está listo. Esperando 3s...
...
✅ PostgreSQL está listo y aceptando conexiones!
🔄 Ejecutando migraciones de Alembic...
```

## 🚨 Solución de Problemas

### Si aún no conecta después de 90 intentos:

**1. Verificar que el servicio PostgreSQL está activo:**
- Ve al dashboard de Render
- Verifica que el servicio PostgreSQL tenga estado "Available"
- Si está "Suspended", actívalo

**2. Verificar la DATABASE_URL:**
- En el Web Service, ve a "Environment"
- Verifica que `DATABASE_URL` esté configurada correctamente
- **IMPORTANTE**: Usa la **Internal Database URL** (con `-a`), no la External

**3. Verificar conectividad de red:**
- Ambos servicios (PostgreSQL y Web Service) deben estar en la **misma región**
- La URL interna (con `-a`) solo funciona entre servicios en la misma región

**4. Aumentar timeouts:**
Si 90 intentos no son suficientes, aumenta:
```bash
DB_WAIT_RETRIES=120
DB_WAIT_INTERVAL=5
```

### Si las migraciones fallan:

**1. Verificar permisos del usuario:**
```sql
-- El usuario debe tener permisos para crear/modificar tablas
GRANT ALL PRIVILEGES ON DATABASE leyia_postgres TO leyia_postgres_user;
```

**2. Ejecutar migraciones manualmente:**
```bash
# En Render Shell (si está disponible)
alembic upgrade head
```

**3. Desactivar migraciones temporalmente:**
```bash
RUN_MIGRATIONS=0
```

### Si el frontend no carga:

**1. Verificar que reflex init se completó:**
Busca en los logs:
```
✅ Reflex inicializado correctamente
```

**2. Verificar puertos:**
```bash
PORT=8000
FRONTEND_PORT=3000
```

**3. Aumentar timeout de healthcheck:**
El healthcheck actual espera 60s. Si necesitas más:
- Contacta a Render para aumentar el tiempo de inicio

## 📊 Monitoreo

### Logs en Tiempo Real:
```bash
# En el dashboard de Render
Logs → View logs → Enable "Auto-scroll"
```

### Verificar Salud de la App:
```bash
# Una vez desplegada
curl https://tu-app.onrender.com/ping
```

## ✅ Checklist Post-Despliegue

- [ ] PostgreSQL está "Available" en Render
- [ ] DATABASE_URL está configurada (con `-a` para URL interna)
- [ ] Todas las API keys están configuradas
- [ ] REFLEX_ENV=prod
- [ ] DB_WAIT_RETRIES=90
- [ ] DB_WAIT_INTERVAL=3
- [ ] Push de cambios realizado
- [ ] Logs muestran "PostgreSQL está listo"
- [ ] Logs muestran "Migraciones completadas"
- [ ] Logs muestran "Reflex inicializado"
- [ ] La aplicación responde en la URL de Render

## 🎯 Próximos Pasos

Una vez que la app esté funcionando:

1. **Verificar funcionalidades:**
   - Login/Registro
   - Chat con asistente
   - Subida de archivos
   - Transcripción de audio

2. **Optimizar:**
   - Agregar Redis para mejor rendimiento
   - Configurar disco persistente para archivos
   - Configurar dominio personalizado

3. **Monitorear:**
   - Revisar logs regularmente
   - Configurar alertas en Render
   - Monitorear uso de tokens de APIs

## 📞 Soporte

Si el problema persiste después de estos cambios:

1. Revisa los logs completos en Render
2. Verifica que PostgreSQL esté en la misma región
3. Intenta usar la External Database URL temporalmente
4. Contacta al soporte de Render

---

**Última actualización**: 2 de octubre de 2025
**Estado**: Cambios listos para desplegar
