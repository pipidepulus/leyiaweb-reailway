import reflex as rx
import reflex_local_auth
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

@reflex_local_auth.require_login
def proyectos_page():
    def scrape_proyectos_recientes_camara(num_proyectos=15):
        url_camara = "https://www.camara.gov.co/secretaria/proyectos-de-ley#menu"
        base_url_camara = "https://www.camara.gov.co"
        proyectos_list = []
        try:
            headers = {
                'User-Agent': (
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/91.0.4472.124 Safari/537.36'
                )
            }
            response = requests.get(url_camara, timeout=20, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'lxml')
            tabla_proyectos = soup.find('table', class_='table')
            if not tabla_proyectos:
                print("[LOG] No se encontró la tabla de proyectos.")
                return []
            tbody = tabla_proyectos.find('tbody')
            if not tbody:
                print("[LOG] No se encontró tbody en la tabla.")
                return []
            filas_proyecto = tbody.find_all('tr', class_='tablacomispro', limit=num_proyectos)
            for fila in filas_proyecto:
                num_td = fila.find('td', headers='view-field-numero-de-proyecto-camara-table-column')
                numero_proyecto = num_td.get_text(strip=True) if num_td else "N/A"
                tit_td = fila.find('td', headers='view-title-table-column')
                link_tag = tit_td.find('a') if tit_td else None
                if link_tag and link_tag.get('href'):
                    titulo_proyecto = link_tag.get_text(strip=True)
                    enlace_proyecto = urljoin(base_url_camara, link_tag['href'])
                else:
                    titulo_proyecto = tit_td.get_text(strip=True) if tit_td else "N/A"
                    enlace_proyecto = "N/A"
                proyectos_list.append({
                    'Número': numero_proyecto,
                    'Título': titulo_proyecto,
                    'Enlace': enlace_proyecto
                })
            print(f"[LOG] Proyectos obtenidos: {proyectos_list}")
            return proyectos_list
        except Exception as e:
            print(f"[LOG] Error en scraping: {e}")
            return []

    proyectos = scrape_proyectos_recientes_camara(20)
    columns = [
        {"id": "Número", "title": "Número"},
        {"id": "Título", "title": "Título"},
        {"id": "Enlace", "title": "Enlace"},
    ]

    # Renderizado manual de la tabla para habilitar enlaces funcionales
    def render_table(data, columns):
        if not data:
            return rx.el.p("No se encontraron proyectos o hubo un error en el scraping.", class_name="text-red-500 mt-4")
        return rx.el.table(
            rx.el.thead(
                rx.el.tr(
                    rx.el.th(columns[0]["title"], class_name="border border-blue-400 bg-blue-100 text-center"),
                    rx.el.th(columns[1]["title"], class_name="border border-blue-400 bg-blue-100"),
                    rx.el.th(columns[2]["title"], class_name="border border-blue-400 bg-blue-100 text-center"),
                )
            ),
            rx.el.tbody(
                *[
                    rx.el.tr(
                        rx.el.td(row["Número"], class_name="border border-blue-400 text-center"),
                        rx.el.td(row["Título"], class_name="border border-blue-400"),
                        rx.el.td(
                            rx.el.a(
                                "Ver enlace",
                                href=row["Enlace"],
                                target="_blank",
                                class_name="text-blue-600 underline"
                            ) if row["Enlace"] != "N/A" else "N/A",
                            class_name="border border-blue-400 text-center"
                        ),
                        class_name="bg-blue-50 hover:bg-blue-100"
                    ) for row in data
                ]
            ),
            class_name="min-w-full table-auto border mt-4 border-blue-400"
        )

    print(f"[LOG] Columnas: {columns}")
    print(f"[LOG] Data para la tabla: {proyectos}")
    return rx.el.div(
        rx.el.button(
            "← Regresar a pantalla principal",
            on_click=rx.redirect("/"),
            class_name="mb-6 mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded shadow w-fit"
        ),
        rx.el.div(
            rx.el.h3(
                "Explorar Proyectos de Ley",
                class_name="font-semibold text-blue-700 text-2xl mb-2"
            ),
            rx.el.p(
                "Consulta últimas propuestas (Cámara).",
                class_name="text-base text-blue-600 mb-4"
            ),
            render_table(proyectos, columns),
            class_name="p-4 md:p-8 w-full overflow-y-auto"
        ),
        class_name="flex flex-col h-screen font-['Inter'] bg-gray-50 dark:bg-gray-900"
    )
# Nota: Reflex actualmente no soporta renderizado personalizado de celdas en data_table. El enlace se muestra como texto plano.
