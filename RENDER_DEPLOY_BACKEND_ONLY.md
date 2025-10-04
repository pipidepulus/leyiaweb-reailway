# Despliegue en Render: Backend (Reflex) + Static Site separado

Este enfoque separa el backend (WebSockets + API Reflex) del frontend estático exportado.

## Arquitectura

Servicio 1: Web Service (Python)
- Build Command:
```
pip install --upgrade pip && pip install -r requirements.txt && reflex export --frontend-only
```
- Start Command (evita doble bind de puerto en 0.8.7 usando un runner explícito):
```
python run_backend_render.py
```
- Variables:
  - REFLEX_ENV=prod
  - DATABASE_URL=postgresql+psycopg2://... (Render Postgres)
  - SECRET_KEY=<token seguro>
  - API_BASE=https://<dominio-backend>.onrender.com  (opcional si Render no expone RENDER_EXTERNAL_HOSTNAME en runtime)
  - FRONTEND_ORIGIN=https://<dominio-frontend>.onrender.com
  - (Opcionales) OPENAI_API_KEY, ASSEMBLYAI_API_KEY, TAVILY_API_KEY

Servicio 2: Static Site
- Build Command:
```
pip install --upgrade pip && pip install -r requirements.txt && reflex export --frontend-only
```
- Publish Directory: `.web/_static`
- Sin Start Command (Render sirve estáticos)

## Flujo de CORS / API
- El JS del static site carga `api_url` (inyectado desde config) y se comunica con el backend.
- Asegura que `FRONTEND_ORIGIN` se establezca para permitir CORS en websockets.

## Ajustes en `rxconfig.py`
Se añadió lógica IS_RENDER para:
- Leer `API_BASE` y `FRONTEND_ORIGIN`.
- Configurar `cors_allowed_origins` adecuadamente.

## Pasos Iniciales
1. Crear Postgres en Render.
2. Crear Web Service (backend) con las variables de entorno.
3. Crear Static Site apuntando al mismo repo.
4. Después de primer deploy, obtener la URL pública del backend y asignarla a `API_BASE` si no se autoinfiere.
5. Redeploy backend si agregaste `API_BASE` después.

## Troubleshooting
| Problema | Causa | Solución |
|----------|-------|----------|
| Pantalla blanca | Falta de export o ruta publish errónea | Verifica build y `.web/_static` |
| WebSocket error | FRONTEND_ORIGIN no listado en CORS | Añade variable y redeploy |
| 404 en API | `api_url` vacío | Define API_BASE |
| Version reflex antigua | Cache build | Forzar redeploy / "Clear build cache" |
| Errores puerto en uso  | Reflex 0.8.7 intentando reloader | Actualiza a 0.8.13 y/o usa run_backend_render.py |

## Migraciones
Si necesitas migraciones Alembic: ejecutar manualmente en Build Command antes del export:
```
alembic upgrade head || echo "(warning) migrations no aplicadas"
```

## Health Check
El backend expone `/api/health` (GET) para monitoreo sencillo.

## Producción Completa
Para revertir a single service en el futuro: usar Nginx reverse proxy o esperar soporte estable single-port.

---
