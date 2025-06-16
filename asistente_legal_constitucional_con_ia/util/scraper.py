import logging
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
from typing import Optional

logging.basicConfig(level=logging.INFO)


def scrape_proyectos_recientes_camara(
    num_proyectos: int = 15,
) -> Optional[pd.DataFrame]:
    """Scrapes recent legislative projects from the Chamber of Representatives of Colombia."""
    url_camara = "https://www.camara.gov.co/secretaria/proyectos-de-ley#menu"
    base_url_camara = "https://www.camara.gov.co"
    logging.info(f"Scraping data from: {url_camara}")
    proyectos_list = []
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(
            url_camara, timeout=20, headers=headers
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")
        tabla_proyectos = soup.find("table", class_="table")
        if not tabla_proyectos:
            logging.error(
                f"Could not find projects table at {url_camara}"
            )
            return None
        tbody = tabla_proyectos.find("tbody")
        if not tbody:
            logging.error(
                f"Could not find 'tbody' in table at {url_camara}"
            )
            return None
        filas_proyecto = tbody.find_all(
            "tr",
            class_="tablacomispro",
            limit=num_proyectos,
        )
        if not filas_proyecto:
            return pd.DataFrame()
        for fila in filas_proyecto:
            num_td = fila.find(
                "td",
                headers="view-field-numero-de-proyecto-camara-table-column",
            )
            numero_proyecto = (
                num_td.get_text(strip=True)
                if num_td
                else "N/A"
            )
            tit_td = fila.find(
                "td", headers="view-title-table-column"
            )
            link_tag = tit_td.find("a") if tit_td else None
            if link_tag and link_tag.get("href"):
                titulo_proyecto = link_tag.get_text(
                    strip=True
                )
                enlace_proyecto = urljoin(
                    base_url_camara, link_tag["href"]
                )
            else:
                titulo_proyecto = (
                    tit_td.get_text(strip=True)
                    if tit_td
                    else "N/A"
                )
                enlace_proyecto = "N/A"
            est_td = fila.find(
                "td",
                headers="view-field-estadoley-table-column",
            )
            estado_proyecto = (
                est_td.get_text(strip=True)
                if est_td
                else "N/A"
            )
            proyectos_list.append(
                {
                    "Número": numero_proyecto,
                    "Título": titulo_proyecto,
                    "Estado": estado_proyecto,
                    "Enlace": enlace_proyecto,
                }
            )
        return pd.DataFrame(proyectos_list)
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error during scraping: {e}")
    except Exception as e:
        logging.error(
            f"Unexpected error during scraping: {e}",
            exc_info=True,
        )
    return None