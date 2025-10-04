import os
import subprocess
import reflex as rx
from asistente_legal_constitucional_con_ia.asistente_legal_constitucional_con_ia import app
from fastapi import APIRouter

"""Runner para Render.

Evita usar `reflex run` en producción (que puede intentar habilitar reloader / doble proceso
si detecta watchfiles) provocando errores 'Address already in use'.

Pasos:
 1. Ejecuta migraciones Alembic (si existen) -> ignora fallo si no aplica.
 2. Expone un endpoint /api/health.
 3. Levanta uvicorn sin reload con 1 worker.
"""

router = APIRouter()


@router.get('/api/health')
async def health():  # pragma: no cover - trivial
    return {'status': 'ok'}


def run_migrations():
    """Ejecuta alembic upgrade head si hay directorio alembic."""
    if not os.path.isdir('alembic'):
        return
    try:
        print('[run_backend_render] Ejecutando migraciones Alembic...')
        subprocess.run(['alembic', 'upgrade', 'head'], check=False)
    except Exception as e:  # pragma: no cover - log only
        print(f"[run_backend_render] Aviso: fallo al correr migraciones: {e}")


def main():
    # Hook FastAPI app (rx.App expone .api tras compilación)
    fastapi_app = app.api
    fastapi_app.include_router(router)

    run_migrations()

    import uvicorn  # import tardío para evitar coste si falla migración antes
    host = '0.0.0.0'
    port = int(os.environ.get('PORT', '8000'))
    print(f"[run_backend_render] Iniciando backend en {host}:{port}")
    uvicorn.run(fastapi_app, host=host, port=port, reload=False, workers=1)


if __name__ == '__main__':
    main()
