"""Página para visualizar proyectos de ley recientes, usando el layout principal."""

import reflex as rx
from ..components.layout import main_layout
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import Dict, List
from ..util.auth import require_login  # <-- 1. IMPORTAMOS NUESTRO DECORADOR

Proyecto = Dict[str, str]


class ProyectosState(rx.State):
    """Maneja el estado y la lógica para la página de proyectos de ley."""

    proyectos: List[Proyecto] = []
    cargando: bool = False
    error: str = ""

    @rx.event(background=True)
    async def scrape_proyectos(self):
        """
        Realiza web scraping en segundo plano para obtener los proyectos de ley.
        """
        async with self:
            self.cargando = True
            self.error = ""
        try:
            url_camara = "https://www.camara.gov.co/secretaria/proyectos-de-ley#menu"
            base_url_camara = "https://www.camara.gov.co"
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/91.0.4472.124 Safari/537.36"
                )
            }
            response = requests.get(url_camara, timeout=20, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "lxml")
            tabla_proyectos = soup.find("table", class_="table")
            proyectos_list = []
            if tabla_proyectos:
                tbody = tabla_proyectos.find("tbody")
                if tbody:
                    filas = tbody.find_all("tr", class_="tablacomispro", limit=20)
                    for fila in filas:
                        num_td = fila.find("td", headers="view-field-numero-de-proyecto-camara-table-column")
                        tit_td = fila.find("td", headers="view-title-table-column")
                        link_tag = tit_td.find("a") if tit_td else None

                        enlace_proyecto = "N/A"
                        if link_tag and link_tag.get("href"):
                            titulo_proyecto = link_tag.get_text(strip=True)
                            enlace_proyecto = urljoin(base_url_camara, link_tag["href"])
                        else:
                            titulo_proyecto = tit_td.get_text(strip=True) if tit_td else "N/A"

                        proyectos_list.append({
                            "Número": num_td.get_text(strip=True) if num_td else "N/A",
                            "Título": titulo_proyecto,
                            "Enlace": enlace_proyecto,
                        })
            async with self:
                self.proyectos = proyectos_list
        except Exception as e:
            async with self:
                self.error = f"Error al obtener proyectos: {e}"
        finally:
            async with self:
                self.cargando = False


def render_table(data: rx.Var[list]) -> rx.Component:
    """Función auxiliar para renderizar la tabla de proyectos."""
    return rx.el.table(
        rx.el.thead(
            rx.el.tr(
                rx.el.th("Número", class_name="border border-blue-400 bg-blue-100 text-center"),
                rx.el.th("Título", class_name="border border-blue-400 bg-blue-100"),
                rx.el.th("Enlace", class_name="border border-blue-400 bg-blue-100 text-center"),
            )
        ),
        rx.el.tbody(
            rx.foreach(
                data,
                lambda row: rx.el.tr(
                    rx.el.td(
                        row["Número"],
                        class_name="border border-blue-400 text-center",
                        style={"font_size": "14px"},
                    ),
                    rx.el.td(
                        row["Título"],
                        class_name="border border-blue-400",
                        style={"font_size": "14px"},
                    ),
                    rx.el.td(
                        rx.cond(
                            row["Enlace"] != "N/A",
                            rx.link("Ver enlace", href=row["Enlace"], target="_blank", class_name="text-blue-600 underline"),
                            "N/A",
                        ),
                        class_name="border border-blue-400 text-center",
                    ),
                    class_name="bg-blue-50 hover:bg-blue-100",
                ),
            )
        ),
        class_name="min-w-full table-auto border mt-4 border-blue-400",
    )


# --- CAMBIO PRINCIPAL AQUÍ ---
# 2. QUITAMOS @rx.page(...) Y AÑADIMOS @require_login
@require_login
def proyectos_page() -> rx.Component:
    """Define el contenido de la página de proyectos."""
    content = rx.el.div(
        rx.el.h3("Explorar Proyectos de Ley", class_name="font-semibold text-blue-700 text-2xl mb-2"),
        rx.el.p("Consulta últimas propuestas (Cámara).", class_name="text-base text-blue-600 mb-4"),
        rx.cond(
            ProyectosState.cargando,
            rx.el.div(
                rx.spinner(size="3"),
                rx.text("Cargando proyectos...", class_name="text-blue-600 ml-4"),
                display="flex",
                align_items="center",
            ),
            rx.cond(
                ProyectosState.error != "",
                rx.el.p(ProyectosState.error, class_name="text-red-500 mb-4"),
                rx.cond(
                    ProyectosState.proyectos.length() > 0,
                     # --- AQUÍ ESTÁ EL CAMBIO ---
                    rx.box(
                        render_table(ProyectosState.proyectos),
                        overflow_x="auto" # Permite scroll horizontal en la tabla
                    ),
                    # --- FIN DEL CAMBIO ---
                    rx.el.p("No hay proyectos disponibles.", class_name="text-gray-400 text-center py-4"),
                ),
            ),
        ),
        class_name="p-4 md:p-8 w-full",
    )
    return main_layout(content)