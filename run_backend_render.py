import os
import subprocess
import reflex as rx
from asistente_legal_constitucional_con_ia.asistente_legal_constitucional_con_ia import app
from fastapi import APIRouter, FastAPI

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


def _extract_fastapi_app() -> FastAPI:
    """Compila la app Reflex y devuelve instancia FastAPI.

    En algunas versiones la propiedad .api no se materializa hasta después de compile().
    Hacemos introspección segura para encontrar el objeto FastAPI.
    """
    # Intentar compile (idempotente en prod; genera artefactos si faltan)
    try:
        app.compile()
    except Exception as e:  # pragma: no cover
        print(f"[run_backend_render] Aviso: fallo en app.compile(): {e}")

    # 1) Acceso directo si existe atributo api
    candidate = getattr(app, 'api', None)
    if candidate is not None:
        if isinstance(candidate, FastAPI):
            return candidate  # type: ignore

    # 2) Buscar en atributos internos
    for name, value in vars(app).items():
        if isinstance(value, FastAPI):
            print(f"[run_backend_render] FastAPI localizado en atributo '{name}'")
            return value

    raise RuntimeError("No se pudo localizar instancia FastAPI en la app Reflex tras compile().")


def main():
    fastapi_app = _extract_fastapi_app()
    fastapi_app.include_router(router)

    run_migrations()

    import uvicorn  # import tardío
    host = '0.0.0.0'
    port = int(os.environ.get('PORT', '8000'))
    # Log de versión de Reflex para confirmar que no estamos en una versión vieja con bug.
    try:
        import reflex
        print(f"[run_backend_render] Reflex version: {reflex.__version__}")
    except Exception:
        print("[run_backend_render] No se pudo obtener la versión de Reflex")
    print(f"[run_backend_render] Iniciando backend en {host}:{port}")
    uvicorn.run(fastapi_app, host=host, port=port, reload=False, workers=1)


if __name__ == '__main__':
    main()
