"""Script de compilación de frontend para despliegue en Render.

En Reflex 0.8.x no existe el atributo `rx.export.export` en la instalación
estándar; la forma soportada programáticamente es llamar `app.compile()`.
Esto genera el build de frontend y prepara assets sin iniciar el servidor.

Se usa en la fase de *build* y luego se arranca sólo el backend con:
  reflex run --env prod --backend-only --backend-host 0.0.0.0 --backend-port $PORT
"""

from asistente_legal_constitucional_con_ia.asistente_legal_constitucional_con_ia import app

if __name__ == "__main__":
    print("[build_frontend] Compilando aplicación Reflex (app.compile)...")
    try:
        # `compile()` es idempotente: si ya compiló, rehace sólo lo necesario.
        app.compile()
        print("[build_frontend] ✅ Compilación completada.")
    except Exception as e:
        print(f"[build_frontend] ❌ Error compilando la app: {e}")
        raise SystemExit(1)
