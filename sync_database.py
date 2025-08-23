#!/usr/bin/env python3
"""Script para sincronizar BD completamente a ubicación externa."""

import os
import shutil
import sqlite3


def sync_database():
    """Sincroniza la BD a la ubicación externa."""

    old_db = "db/legal_assistant.db"
    new_db = "/tmp/legalassistant_db/legal_assistant.db"

    print("=== SINCRONIZANDO BASE DE DATOS ===\n")

    try:
        # 1. Verificar que existe la BD original
        if os.path.exists(old_db):
            print(f"✅ BD original encontrada: {old_db}")

            # 2. Crear directorio externo
            os.makedirs("/tmp/legalassistant_db", exist_ok=True)
            print("✅ Directorio externo creado/verificado")

            # 3. Copiar BD si no existe o es más antigua
            if not os.path.exists(new_db) or os.path.getmtime(old_db) > os.path.getmtime(new_db):
                shutil.copy2(old_db, new_db)
                print(f"✅ BD copiada a: {new_db}")
            else:
                print("✅ BD externa ya está actualizada")

            # 4. Verificar integridad
            conn = sqlite3.connect(new_db)
            cursor = conn.cursor()

            # Contar notebooks
            cursor.execute("SELECT COUNT(*) FROM notebook")
            notebook_count = cursor.fetchone()[0]

            # Contar transcripciones
            cursor.execute("SELECT COUNT(*) FROM audiotranscription")
            transcription_count = cursor.fetchone()[0]

            conn.close()

            print("✅ Verificación de integridad:")
            print(f"   📓 Notebooks: {notebook_count}")
            print(f"   🎙️ Transcripciones: {transcription_count}")

        else:
            print(f"❌ BD original no encontrada: {old_db}")
            return False

        print("\n✅ SINCRONIZACIÓN COMPLETADA")
        print("\n🚀 AHORA PUEDES:")
        print("1. Reiniciar Reflex: reflex run")
        print("2. Editar notebooks sin recompilación")
        print("3. Crear transcripciones sin recompilación")

        return True

    except Exception as e:
        print(f"❌ Error durante sincronización: {e}")
        return False


if __name__ == "__main__":
    sync_database()
