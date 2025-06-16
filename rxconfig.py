import reflex as rx

config = rx.Config(
    app_name="asistente_legal_constitucional_con_ia",
    plugins=[rx.plugins.TailwindV3Plugin()],
    db_url="sqlite:///reflex.db",  # Usa SQLite por defecto
)