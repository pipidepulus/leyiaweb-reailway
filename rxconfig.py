"""Configuración central de Reflex (rxconfig.py).

Este archivo define cómo se ejecuta la aplicación en entornos local (dev) y
producción (prod). Dado que el proyecto usa Postgres (requerido: DATABASE_URL),
configuramos el motor de base de datos de Reflex para que use la variable de
entorno `DATABASE_URL` y forzamos un fallo temprano si no está disponible.

Reflex 0.8.x no crea este archivo automáticamente si se eliminó; aquí
proporcionamos una versión explícita para:
  - Cargar variables desde .env (si existe) para desarrollo.
  - Diferenciar REFLEX_ENV=dev | prod.
  - Ajustar rutas de compilación y puertos por defecto.
  - Exponer una función helper `get_config()` que Reflex detecta.

Uso:
  # Desarrollo
  export REFLEX_ENV=dev  # (opcional, por defecto 'dev' si no es prod)
  export DATABASE_URL=postgresql://user:pass@localhost:5432/mi_db
  reflex run

  # Producción
  export REFLEX_ENV=prod
  export DATABASE_URL=postgresql://user:pass@host:5432/db
  reflex run --env prod

Si necesitas usar SQLite temporalmente (solo para pruebas rápidas), puedes
exportar USE_SQLITE_FOR_DEV=1 y omitir DATABASE_URL en dev (no recomendado para
el flujo real de la app, porque Alembic y scripts asumen Postgres).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import reflex as rx
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe (solo afecta si no están ya en el ambiente)
load_dotenv()

ROOT_DIR = Path(__file__).parent
ENV = os.getenv("REFLEX_ENV", "dev").lower()


def _resolve_db_url() -> str:
	"""Obtiene la URL de base de datos a usar.

	Prioriza:
	  1. DATABASE_URL (Postgres requerida en este proyecto)
	  2. Si USE_SQLITE_FOR_DEV=1 y estamos en dev, genera SQLite local.
	"""
	db_url = os.getenv("DATABASE_URL", "").strip()
	if db_url:
		return db_url

	# Fallback opcional solo para experimentación en dev.
	if ENV != "prod" and os.getenv("USE_SQLITE_FOR_DEV") == "1":
		return f"sqlite:///{ROOT_DIR / 'dev_local.sqlite3'}"

	# Falla claramente si falta en flujo normal.
	raise RuntimeError(
		"DATABASE_URL no definida. Exporta una URL Postgres en la variable de entorno `DATABASE_URL` "
		"(por ej. postgresql://user:pass@localhost:5432/mi_db). Para usar SQLite temporalmente en dev, "
		"exporta USE_SQLITE_FOR_DEV=1." 
	)


def get_config() -> rx.Config:  # Reflex detecta esta función
	"""Construye la configuración de la aplicación.

	Ajustes claves:
	  - db_url: forzamos a Postgres (o fallback explícito en dev si se pidió)
	  - cors: permitir localhost durante desarrollo
	  - api_url: autodetect; en prod a veces detrás de un proxy (dejar default)
	  - frontend_path/backend_path: valores por defecto
	"""

	db_url = _resolve_db_url()

	# ------------------------------------------------------------------
	# Plugins: Sitemap
	# Reflex muestra una advertencia si el SitemapPlugin está "implícito".
	# Damos control explícito:
	#  - Define SITEMAP_SITE_URL para habilitarlo.
	#  - Si no se define, lo deshabilitamos para eliminar la advertencia.
	# ------------------------------------------------------------------
	plugins: list = []
	disable_plugins: list[str] = []
	sitemap_url = os.getenv("SITEMAP_SITE_URL", "").strip()
	if sitemap_url:
		try:
			from reflex.plugins.sitemap import SitemapPlugin  # type: ignore

			# Añadimos el plugin con la URL pública base del sitio.
			plugins.append(SitemapPlugin(site_url=sitemap_url))
		except Exception as e:  # pragma: no cover - solo logging
			print(f"[rxconfig] Aviso: no se pudo inicializar SitemapPlugin: {e}")
			disable_plugins.append("reflex.plugins.sitemap.SitemapPlugin")
	else:
		# Deshabilitar explícitamente para evitar la advertencia.
		disable_plugins.append("reflex.plugins.sitemap.SitemapPlugin")

	# Permitir orígenes locales típicos en desarrollo
	if ENV == "prod":
		cors_allowed_origins: Optional[list[str]] = None  # usar defaults (Reflex validará)
	else:
		cors_allowed_origins = [
			"http://localhost:3000",
			"http://127.0.0.1:3000",
			"http://localhost:8000",
			"http://127.0.0.1:8000",
		]

	# Nota: rx.Config acepta parámetros documentados; mantenemos los esenciales.
	# En Reflex 0.8.x, database_url se pasa como db_url.
	# IMPORTANTE: Reflex espera que plugins sea iterable; no pasar None.
	return rx.Config(
		app_name="asistente_legal_constitucional_con_ia",
		db_url=db_url,
		env=ENV,  # Reflex utiliza 'prod' para activar optimizaciones
		backend_port=int(os.getenv("PORT", "8000")),
		frontend_port=int(os.getenv("FRONTEND_PORT", "3000")),
		cors_allowed_origins=cors_allowed_origins,
		# En muchos entornos de despliegue, el host debe ser 0.0.0.0
		backend_host=os.getenv("BACKEND_HOST", "0.0.0.0"),
		frontend_host=os.getenv("FRONTEND_HOST", "localhost"),
		plugins=plugins,  # siempre lista (vacía o con plugin sitemap)
		disable_plugins=disable_plugins or None,  # puede ser None sin problema
		show_built_with_reflex=False,  # evitar branding en footer
	)


# Exponer instancia (algunas utilidades inspeccionan variable module-level)
config = get_config()

# Log mínimo al importar para ayudar a diagnóstico temprano
print(f"[rxconfig] ENV={ENV} db_url={'sqlite' if 'sqlite' in config.db_url else 'postgres'} backend={config.backend_host}:{config.backend_port}")

