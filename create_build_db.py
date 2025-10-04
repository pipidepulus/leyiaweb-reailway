# create_build_db.py
import reflex as rx
from sqlmodel import SQLModel

# Importa el módulo principal de tu aplicación para que Reflex descubra
# todos los modelos (como LocalUser) que necesita crear.
# Asegúrate de que esta línea es correcta para tu estructura de proyecto.
import asistente_legal_constitucional_con_ia.asistente_legal_constitucional_con_ia

def create_db_tables():
    """
    Se conecta a la base de datos configurada en rxconfig
    (que será nuestra DB "dummy" durante el build) y crea todas las tablas.
    """
    print("🔧 Creando tablas en la base de datos temporal de compilación...")
    
    # Importar el módulo de la base de datos de la manera correcta
    from reflex.model import get_engine
    
    engine = get_engine()
    SQLModel.metadata.create_all(engine)
    print("✅ Tablas creadas con éxito.")

if __name__ == "__main__":
    create_db_tables()