#!/usr/bin/env python3
"""Script simple para verificar conexión a la base de datos Postgres.

Uso:
  source venv/bin/activate
  python check_db.py

Variables:
  DATABASE_URL debe estar definida y apuntar a postgresql://
"""
from sqlalchemy import text, create_engine
import os
import sys

def main():
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("[ERROR] DATABASE_URL no está definida.")
        sys.exit(1)
    if not url.startswith("postgresql://"):
        print(f"[ADVERTENCIA] La URL no parece Postgres: {url}")
    engine = create_engine(url, echo=False, future=True)
    try:
        with engine.connect() as conn:
            version = conn.execute(text("SELECT version();")).scalar()
            tables = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public';")).fetchall()
            print("[OK] Conexión exitosa a Postgres.")
            print("Versión:", version)
            print("Tablas:", [t[0] for t in tables])
    except Exception as e:
        print("[ERROR] No se pudo conectar:", e)
        sys.exit(2)

if __name__ == "__main__":
    main()
