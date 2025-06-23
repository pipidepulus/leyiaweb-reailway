# /home/pipid/legalcolrag/asistente_legal_constitucional_con_ia/states/app_state.py
import reflex as rx
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import Dict, List

# --- Modelos de Datos ---
class Prompt(rx.Base):
    title: str
    description: str
    content: str

Proyecto = Dict[str, str]




class AppState(rx.State):
    # --- Variables de Proyectos ---
    proyectos: List[Proyecto] = []
    proyectos_cargando: bool = False
    proyectos_error: str = ""
    proyectos_initial_load_done: bool = False

    # --- Variables de Prompts ---
    copied_feedback: Dict[str, bool] = {}

    # --- Eventos de Proyectos ---
    @rx.event(background=True)
    async def scrape_proyectos_data(self):
        async with self:
            self.proyectos_cargando = True
            self.proyectos_error = ""
            self.proyectos = []
        try:
            # ... (Lógica de scraping de proyectos_page.py, idéntica)
            url_camara = "https://www.camara.gov.co/secretaria/proyectos-de-ley#menu"
            # ... resto del código de scraping ...
            base_url_camara = "https://www.camara.gov.co"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            
            # Usamos requests de forma síncrona, es más simple para este caso de fondo
            response = requests.get(url_camara, timeout=20, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')
            tabla_proyectos = soup.find('table', class_='table')
            proyectos_list = []
            if tabla_proyectos:
                tbody = tabla_proyectos.find('tbody')
                if tbody:
                    filas_proyecto = tbody.find_all('tr', class_='tablacomispro', limit=20)
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
                        proyectos_list.append({'Número': numero_proyecto, 'Título': titulo_proyecto, 'Enlace': enlace_proyecto})

            async with self:
                self.proyectos = proyectos_list
        except Exception as e:
            async with self:
                self.proyectos_error = f"Error en scraping: {e}"
        finally:
            async with self:
                self.proyectos_cargando = False
    
    @rx.event
    def cargar_proyectos_si_necesario(self):
        if not self.proyectos_initial_load_done:
            self.reset()
            self.proyectos_initial_load_done = True
            return AppState.scrape_proyectos_data

    @rx.event
    def limpiar_proyectos_y_redirigir(self):
        self.proyectos = []
        self.proyectos_cargando = False
        self.proyectos_error = ""
        self.proyectos_initial_load_done = False
        return rx.redirect("/")

    # --- Eventos de Prompts ---
    def handle_prompt_change(self, phase_key: str, index: int, new_content: str):
        self.prompt_phases[phase_key][index].content = new_content
        prompt_unique_id = f"{phase_key}-{index}"
        # If user edits a prompt that was showing "Copied!", clear that specific feedback.
        if self.copied_feedback.get(prompt_unique_id):
            # Create a new dictionary for the state update to ensure Reflex detects the change.
            new_feedback_state = self.copied_feedback.copy()
            new_feedback_state[prompt_unique_id] = False
            self.copied_feedback = new_feedback_state
    
    def copy_to_clipboard_and_show_feedback(self, content: str, phase_key: str, index: int):
        prompt_unique_id = f"{phase_key}-{index}"

        # Create a new dictionary: set all to False, then current to True.
        # This ensures that only one "Copied!" message is shown at a time.
        # Make sure to iterate over a copy of keys if modifying dict during iteration, or build anew.
        current_feedback_state = {
            k: False for k in list(self.copied_feedback.keys())}
        current_feedback_state[prompt_unique_id] = True
        self.copied_feedback = current_feedback_state

        return rx.set_clipboard(content)  # Return the clipboard event

    @rx.event
    def limpiar_prompts_y_redirigir(self):
        # Aquí podrías resetear prompts editados si quisieras
        return rx.redirect("/")