# asistente_legal_constitucional_con_ia/util/tools.py
import os
import json
from tavily import TavilyClient

# --- INICIO DE LA MODIFICACIÓN ---
# Límite de caracteres para el snippet de contenido de cada resultado.
# 1500 caracteres es un buen balance: suficiente contexto, pero no sobrecarga.
MAX_CONTENT_SNIPPET_LENGTH = 2000
# --- FIN DE LA MODIFICACIÓN ---

# Carga la API key desde las variables de entorno, igual que haces con OpenAI y Clerk
try:
    tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
except KeyError:
    print("ADVERTENCIA: La variable de entorno TAVILY_API_KEY no está configurada.")
    tavily_client = None

def buscar_en_internet(query: str) -> str:
    """
    Busca en internet usando la API de Tavily para encontrar información relevante.
    Devuelve un resumen de los resultados y las fuentes.
    """
    if not tavily_client:
        return "Error: El servicio de búsqueda no está configurado (falta TAVILY_API_KEY)."

    print(f"--- Herramienta 'buscar_en_internet' llamada con query: '{query}' ---")
    try:
        response = tavily_client.search(
            query=query,
            search_depth="advanced",
            # Limita la búsqueda a sitios gubernamentales y de alta autoridad legal de Colombia
            include_domains=[
                "corteconstitucional.gov.co",
                "suin-juriscol.gov.co",                
                "svrpubindc.imprenta.gov.co/senado",
                "https://www.corteconstitucional.gov.co/relatoria/buscador-jurisprudencia",               
            ],
        )
        results_to_return = []
        for result in response.get('results', [])[:3]:  # Tomamos los 3 más relevantes
            # Truncamos el contenido a nuestro límite definido
            snippet = result.get('content', '')[:MAX_CONTENT_SNIPPET_LENGTH]
            # --- FIN DE LA MODIFICACIÓN ---
            results_to_return.append({
                "url": result.get('url'),
                "title": result.get('title'),
                "content": snippet 
            })
        
        if not results_to_return:
            return "No se encontraron resultados relevantes en internet."
        
        # Devolvemos un string JSON para que el asistente lo pueda procesar fácilmente
        return json.dumps(results_to_return)

    except Exception as e:
        print(f"Error durante la búsqueda en internet: {e}")
        return f"Hubo un error al intentar buscar en internet: {str(e)}"