#!/usr/bin/env python3
"""Script para arreglar la base de datos de transcripciones."""

import json
import sqlite3
from datetime import datetime


def fix_transcription_database():
    """Arregla las asociaciones incorrectas en la base de datos."""

    conn = sqlite3.connect("/tmp/legalassistant_db/legal_assistant.db")
    cursor = conn.cursor()

    print("=== ARREGLANDO BASE DE DATOS DE TRANSCRIPCIONES ===\n")

    try:
        # 1. Crear notebook faltante para "derecho_a_la_carta_invitado_espan_ol.mp3"
        print("1. Creando notebook faltante para transcripción ID 2...")

        # Contenido del notebook
        notebook_content = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "source": [
                        "# Transcripción - derecho_a_la_carta_invitado_espan_ol\n\n",
                        "**Archivo:** derecho_a_la_carta_invitado_espan_ol.mp3\n\n",
                        f"**Generado:** {datetime.now().strftime('%d/%m/%Y a las %H:%M')}\n\n",
                        "---\n\n",
                    ],
                },
                {"cell_type": "markdown", "source": ["## 📝 Transcripción Completa\n\n", "*Transcripción no disponible - archivo procesado anteriormente*\n\n"]},
            ],
            "metadata": {"kernelspec": {"display_name": "Audio Transcription", "language": "markdown", "name": "audio_transcription"}},
        }

        # Insertar notebook
        cursor.execute(
            """
            INSERT INTO notebook (title, content, workspace_id, notebook_type, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            ("Transcripción - derecho_a_la_carta_invitado_espan_ol", json.dumps(notebook_content), "public", "transcription", datetime.now(), datetime.now()),
        )

        new_notebook_id = cursor.lastrowid
        print(f"   ✅ Notebook creado con ID: {new_notebook_id}")

        # 2. Actualizar transcripción ID 2 para que apunte al nuevo notebook
        print("2. Actualizando transcripción ID 2...")
        cursor.execute(
            """
            UPDATE audiotranscription
            SET notebook_id = ?
            WHERE id = 2
        """,
            (new_notebook_id,),
        )
        print(f"   ✅ Transcripción ID 2 ahora apunta al notebook {new_notebook_id}")

        # 3. Corregir transcripción ID 1 (debería apuntar al notebook 3, no al 2)
        print("3. Corrigiendo transcripción ID 1...")
        cursor.execute(
            """
            UPDATE audiotranscription
            SET notebook_id = 3
            WHERE id = 1
        """,
        )
        print("   ✅ Transcripción ID 1 ahora apunta al notebook 3 (correcto)")

        # 4. Verificar resultados
        print("\n=== VERIFICANDO RESULTADOS ===")
        cursor.execute("SELECT id, filename, notebook_id FROM audiotranscription ORDER BY id")
        transcriptions = cursor.fetchall()

        cursor.execute("SELECT id, title, notebook_type FROM notebook ORDER BY id")
        notebooks = cursor.fetchall()

        print("Notebooks después de la corrección:")
        for nb in notebooks:
            print(f"   ID: {nb[0]}, Título: {nb[1]}, Tipo: {nb[2]}")

        print("\nTranscripciones después de la corrección:")
        for tr in transcriptions:
            print(f"   ID: {tr[0]}, Archivo: {tr[1]}, Notebook_ID: {tr[2]}")

        # 5. Commit cambios
        conn.commit()
        print("\n✅ CORRECCIÓN COMPLETADA EXITOSAMENTE")

    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    fix_transcription_database()
