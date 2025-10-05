"""Script de compilación de frontend para despliegue en Render.

Ejecuta la exportación del frontend (build estático) sin iniciar el backend.
Usar en Render en la fase de *build* antes de arrancar el backend con
`reflex run --env prod --backend-only`.
"""
from asistente_legal_constitucional_con_ia.asistente_legal_constitucional_con_ia import app  # noqa: F401
import reflex as rx

if __name__ == "__main__":
    print("[build_frontend] Compilando frontend de Reflex (producción)...")
    try:
        rx.export.export(frontend=True, backend=False, zip=False)
        print("[build_frontend] ✅ Frontend compilado correctamente.")
    except Exception as e:
        print(f"[build_frontend] ⚠️ Error compilando frontend: {e}")
        raise SystemExit(1)
