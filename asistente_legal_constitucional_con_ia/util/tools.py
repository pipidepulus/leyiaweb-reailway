# asistente_legal_constitucional_con_ia/util/tools.py

import os
import json
from tavily import TavilyClient
from dotenv import load_dotenv

MAX_CONTENT_SNIPPET_LENGTH = 2000

try:
    # Es una buena práctica cargar las variables de entorno al inicio.
    load_dotenv()
    tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
except KeyError:
    print("ADVERTENCIA: La variable de entorno TAVILY_API_KEY no está configurada.")
    tavily_client = None

def buscar_documento_legal(query: str, tipo_documento: str, sitio_preferido: str = None) -> str:
    """
    Herramienta de búsqueda avanzada para encontrar documentos legales colombianos
    (leyes, decretos, sentencias, gacetas) en internet.

    Args:
        query: La consulta de búsqueda muy específica. Ej: 'Sentencia C-123 de 2023', 'Ley 1437 de 2011', '758 de 2017'.
        tipo_documento: El tipo de documento a buscar. Valores posibles: 'sentencia', 'ley', 'gaceta'.
        sitio_preferido: (Opcional) Un dominio específico para priorizar la búsqueda.
    """
    if not tavily_client:
        return "Error: El servicio de búsqueda no está configurado."

    print(f"--- Herramienta 'buscar_documento_legal' con query: '{query}', tipo: {tipo_documento}, sitio: {sitio_preferido} ---")
    
    final_query = query
    filetype = None

    # Estrategias de búsqueda por tipo de documento
    if tipo_documento == 'gaceta':
        # Para gacetas, construimos un query más robusto.
        final_query = f'"Gaceta del Congreso" {query}'
        filetype = 'pdf'
        # No se recomienda un sitio preferido para gacetas para ampliar la búsqueda.
    elif tipo_documento == 'sentencia' and not sitio_preferido:
        # Si es una sentencia y no hay sitio, acotamos el query.
        final_query = f'"{query}"'
    elif tipo_documento == 'ley' and not sitio_preferido:
         # Si es una ley y no hay sitio, acotamos el query.
        final_query = f'"{query}"'

    if sitio_preferido:
        final_query += f" site:{sitio_preferido}"
    if filetype:
        final_query += f" filetype:{filetype}"
    
    print(f"--- Query final enviado a Tavily: '{final_query}' ---")

    try:
        response = tavily_client.search(
            query=final_query,
            search_depth="advanced",
            max_results=5,
            include_raw_content=False, # Optimización: no necesitamos el contenido crudo si solo queremos el snippet
            timeout=30
        )
        
        results = response.get('results', [])
        if not results:
            return "No se encontraron resultados relevantes para la búsqueda especificada."
        
        # Devolvemos solo la información esencial para el LLM.
        results_to_return = [
            {"url": r.get('url'), "title": r.get('title'), "snippet": r.get('content', '')[:MAX_CONTENT_SNIPPET_LENGTH]}
            for r in results
        ]
        return json.dumps(results_to_return, ensure_ascii=False)
        
    except Exception as e:
        return f"Error al procesar la búsqueda en internet. El servicio devolvió el siguiente mensaje: {str(e)}"