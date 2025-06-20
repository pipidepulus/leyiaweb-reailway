import logging
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
from typing import Optional, List, Dict, Any

# --- Constants ---
URL_CAMARA = "https://www.camara.gov.co/secretaria/proyectos-de-ley#menu"
BASE_URL_CAMARA = "https://www.camara.gov.co"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
TIMEOUT = 20

# --- Logger Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def _fetch_html(url: str) -> Optional[BeautifulSoup]:
    """Fetches and parses HTML content from a URL."""
    logging.info(f"Fetching data from: {url}")
    try:
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(url, timeout=TIMEOUT, headers=headers)
        response.raise_for_status()
        return BeautifulSoup(response.content, "lxml")
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error while fetching {url}: {e}")
        return None


def _parse_proyectos(soup: BeautifulSoup, base_url: str, num_proyectos: int) -> Optional[List[Dict[str, Any]]]:
    """Parses the projects table from the BeautifulSoup object."""
    tabla_proyectos = soup.find("table", class_="table")
    if not tabla_proyectos:
        logging.error("Could not find the projects table in the HTML.")
        return None

    tbody = tabla_proyectos.find("tbody")
    if not tbody:
        logging.error("Could not find 'tbody' in the projects table.")
        return None

    filas_proyecto = tbody.find_all("tr", class_="tablacomispro", limit=num_proyectos)
    if not filas_proyecto:
        logging.warning("No project rows found in the table.")
        return []

    proyectos_list = []
    for fila in filas_proyecto:
        num_td = fila.find("td", headers="view-field-numero-de-proyecto-camara-table-column")
        tit_td = fila.find("td", headers="view-title-table-column")
        est_td = fila.find("td", headers="view-field-estadoley-table-column")

        numero_proyecto = num_td.get_text(strip=True) if num_td else "N/A"
        estado_proyecto = est_td.get_text(strip=True) if est_td else "N/A"
        
        titulo_proyecto = "N/A"
        enlace_proyecto = "N/A"
        link_tag = tit_td.find("a") if tit_td else None
        if link_tag and link_tag.get("href"):
            titulo_proyecto = link_tag.get_text(strip=True)
            enlace_proyecto = urljoin(base_url, link_tag["href"])
        elif tit_td:
            titulo_proyecto = tit_td.get_text(strip=True)

        proyectos_list.append({
            "Número": numero_proyecto,
            "Título": titulo_proyecto,
            "Estado": estado_proyecto,
            "Enlace": enlace_proyecto,
        })
    
    logging.info(f"Successfully scraped {len(proyectos_list)} projects.")
    return proyectos_list


def scrape_proyectos_recientes_camara(num_proyectos: int = 15) -> Optional[pd.DataFrame]:
    """
    Scrapes recent legislative projects from the Chamber of Representatives of Colombia.

    Args:
        num_proyectos: The maximum number of projects to scrape.

    Returns:
        A pandas DataFrame containing the scraped projects, or None if an error occurs.
    """
    soup = _fetch_html(URL_CAMARA)
    if not soup:
        return None

    try:
        proyectos_data = _parse_proyectos(soup, BASE_URL_CAMARA, num_proyectos)
        if proyectos_data is None:
            return None
        if not proyectos_data:
            return pd.DataFrame() # Return empty DataFrame if no projects found
            
        return pd.DataFrame(proyectos_data)

    except Exception as e:
        logging.error(f"An unexpected error occurred during scraping: {e}", exc_info=True)
        return None
