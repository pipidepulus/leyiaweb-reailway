# Asistente Legal Constitucional con IA

Sistema especializado en análisis de jurisprudencia y leyes constitucionales utilizando Inteligencia Artificial.

## 🚀 Características

- **Análisis Constitucional**: Asistente especializado en derecho constitucional
- **Exploración de Proyectos**: Visualización de proyectos de ley recientes
- **Metodología de Prompts**: Guías especializadas para análisis legal
- **Interfaz Moderna**: Construido con Reflex (Python)

## 📋 Requisitos

- Python 3.12+
- Reflex Framework
- OpenAI API Key
- Tavily API Key

## ⚙️ Instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/TU_USUARIO/legalcolrag-noclerk.git
   cd legalcolrag-noclerk
   ```

2. **Crear entorno virtual**
   ```bash
   python3 -m venv env
   source env/bin/activate  # En Linux/Mac
   # o env\Scripts\activate en Windows
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   # Editar .env con tus API keys
   ```

5. **Inicializar Reflex**
   ```bash
   reflex init
   ```

6. **Ejecutar la aplicación**
   ```bash
   reflex run
   ```

## 🔧 Configuración

Crear un archivo `.env` con las siguientes variables:

```env
OPENAI_API_KEY="tu_openai_api_key"
TAVILY_API_KEY="tu_tavily_api_key"
ASSISTANT_ID_CONSTITUCIONAL="tu_assistant_id"
```

## 🌐 Uso

1. Accede a `http://localhost:3000`
2. Navega entre las diferentes secciones:
   - **Inicio**: Página principal
   - **Asistente Constitucional**: Chat especializado
   - **Proyectos de Ley**: Exploración de legislación
   - **Prompts**: Metodología de análisis

## 📁 Estructura del Proyecto

```
asistente_legal_constitucional_con_ia/
├── components/          # Componentes reutilizables
├── pages/              # Páginas de la aplicación
├── states/             # Estados globales
├── util/               # Utilidades
└── asistente_legal_constitucional_con_ia.py  # Archivo principal
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit tus cambios (`git commit -am 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Si tienes preguntas o necesitas ayuda, por favor abre un issue en GitHub.

---

Desarrollado con ❤️ usando [Reflex](https://reflex.dev)
