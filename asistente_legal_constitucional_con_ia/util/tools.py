# asistente_legal_constitucional_con_ia/util/tools.py
# ESTE CÓDIGO ES CORRECTO Y NO REQUIERE CAMBIOS

import os
import json
from tavily import TavilyClient

MAX_CONTENT_SNIPPET_LENGTH = 2000

try:
    tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
except KeyError:
    print("ADVERTENCIA: La variable de entorno TAVILY_API_KEY no está configurada.")
    tavily_client = None

def buscar_documento_legal(query: str, sitio_preferido: str = None, filetype: str = None) -> str:
    """
    Herramienta de búsqueda avanzada para encontrar documentos legales colombianos
    (leyes, decretos, sentencias, gacetas) en internet, con capacidad para buscar tipos de archivo específicos.

    Args:
        query: La consulta de búsqueda muy específica y completa.
        sitio_preferido: (Opcional) Un dominio específico para priorizar la búsqueda.
        filetype: (Opcional) El tipo de archivo a buscar (ej: 'pdf').
    """
    if not tavily_client:
        return "Error: El servicio de búsqueda no está configurado."

    print(f"--- Herramienta 'buscar_documento_legal' con query: '{query}', sitio: {sitio_preferido}, filetype: {filetype} ---")
    
    final_query = query
    if sitio_preferido:
        final_query += f" site:{sitio_preferido}"
    if filetype:
        final_query += f" filetype:{filetype}"
    
    try:
        response = tavily_client.search(
            query=final_query,
            search_depth="advanced",
            max_results=5,
            timeout=30
        )
        
        results = response.get('results', [])
        if not results:
            return "No se encontraron resultados relevantes para la búsqueda especificada."
        
        results_to_return = [
            {"url": r.get('url'), "title": r.get('title'), "content": r.get('content', '')[:MAX_CONTENT_SNIPPET_LENGTH]}
            for r in results
        ]
        return json.dumps(results_to_return, ensure_ascii=False)
        
    except Exception as e:
        return f"Error al procesar la búsqueda en internet. El servicio devolvió el siguiente mensaje: {str(e)}"