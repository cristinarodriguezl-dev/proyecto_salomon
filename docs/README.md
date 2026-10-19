# 📚 Content Enrichment (Salomón)

Aplicación de consola (línea de comandos) que busca un tema en **Wikipedia**, muestra el artículo y lo mejora con **inteligencia artificial**.

No hace falta saber programar para usarla: la propia aplicación te va preguntando qué quieres buscar y qué hacer a continuación.

Las preguntas se contestan con el teclado: escribes cuando te pide un texto y, cuando te ofrece opciones, te mueves con las **flechas** y confirmas con **Enter**.

---

## 🎯 ¿Qué hace la app?

- Te pide que escribas un tema (por ejemplo: "Python", "Mercurio" o "Árbol").

- Busca ese tema en la Wikipedia en español.

- Muestra el título y los primeros párrafos del artículo original.

- Pide a la inteligencia artificial (Google Gemini) que amplíe y mejore ese texto.

- Muestra el artículo mejorado en pantalla.

- Te pregunta si quieres buscar otro tema o salir del programa.

---

## 🔄 ¿Cómo funciona? Paso a paso

Cada paso es una acción que la aplicación hace por ti, en este orden:

- **Paso 1 — Te pregunta el tema.**

  Aparece un mensaje en pantalla pidiéndote que escribas algo. Si lo dejas vacío, te lo vuelve a pedir.

- **Paso 2 — Habla con Wikipedia.**

  La app envía una petición a Wikipedia (como si abrieras el navegador y buscaras ahí) y descarga la página con el resultado.

- **Paso 3 — Comprueba si hay error.**

  Si no hay internet o Wikipedia tarda demasiado, la app te avisa y vuelve a preguntar el tema. No se "rompe".

- **Paso 4 — Extrae lo importante de la página.**

  Wikipedia devuelve una página enorme con menús, imágenes y tablas. La app se queda solo con el título y hasta 5 párrafos de texto.

- **Paso 5 — Muestra el artículo original.**

  Imprime en pantalla el título y los párrafos tal cual salen de Wikipedia.

- **Paso 6 — Lo mejora con inteligencia artificial.**

  Junta los párrafos, se los envía a Google Gemini con la orden "mejora este texto sin inventar nada" y recibe una versión mejorada.

- **Paso 7 — Muestra el artículo mejorado.**

  Imprime el resultado de la IA justo debajo del original.

- **Paso 8 — Te pregunta qué hacer.**

  Te ofrece "Buscar otro tema" o "Salir". Te mueves entre las dos opciones con las flechas y confirmas con Enter: si eliges buscar otro, el proceso empieza de nuevo; si eliges salir, muestra "Programa finalizado." y termina.

---

## 💻 El código más importante, explicado

En cada parte del código verás dos explicaciones:

- **En pocas palabras:** para quien no programa.

- **Detalle técnico:** para quien sí programa.

### 1. El director de orquesta: `src/main.py`

Es el punto de entrada. No hace el trabajo pesado: llama a las demás piezas en el orden correcto.

```python
while True:
    topic = request_topic()

    try:
        article = search_service.search(topic)
    except (requests.exceptions.RequestException, TimeoutError) as error:
        print(error)
        continue

    show_original_article(article)
    article = content_enhancer.enhance(article)
    show_enriched_article(article)

    if not continuation_prompt.ask_search_again():
        print("Programa finalizado.")
        return
```

- **En pocas palabras:** el `while True` significa "repite esto". Si la búsqueda falla, vuelve a preguntarte el tema; si sale bien, muestra el artículo, lo mejora y te pregunta si quieres continuar.

- **Detalle técnico:** el `try/except` captura errores de red (`RequestException`) y de tiempo de espera (`TimeoutError`) para reintentar sin cerrar el programa. `ask_search_again()` devuelve `True` o `False`; cuando es `False` se sale con `return`.

---

### 2. Pedir el tema: `src/ui/topic_input.py`

```python
while True:
    topic = questionary.text(PROMPT_MESSAGE).unsafe_ask().strip()

    if topic:
        return topic

    print(EMPTY_INPUT_MESSAGE)
```

- **En pocas palabras:** lee lo que escribes. Si solo presionas "Enter" sin escribir nada, te pide que lo intentes otra vez.

- **Detalle técnico:** `questionary.text()` abre una línea de texto en la terminal y `unsafe_ask()` devuelve lo escrito (Ctrl+C se propaga igual que con `input()`); `.strip()` elimina los espacios del principio y del final. El bucle garantiza que nunca se devuelve una cadena vacía.

---

### 3. Repetir o salir: `src/ui/search_continuation_prompt.py`

```python
choice = questionary.select(
    self.MENU_MESSAGE, choices=self.OPTIONS
).unsafe_ask()

return choice == self.SEARCH_AGAIN_OPTION
```

- **En pocas palabras:** después de ver el artículo, pregunta qué hacer. Eliges "Buscar otro tema" o "Salir" moviéndote con las flechas y pulsando Enter; ya no hace falta escribir números.

- **Detalle técnico:** `questionary.select()` solo admite las opciones de la lista, así que la pregunta no puede recibir una respuesta inválida y el bucle de validación desaparece. Devuelve el texto elegido, que el método traduce en `True` (seguir) o `False` (salir).

---

### 4. Hablar con Wikipedia: `src/scraping/wikipedia_client.py`

```python
response = requests.get(
    WIKIPEDIA_SEARCH_URL,
    params={"search": topic},
    headers={"User-Agent": USER_AGENT},
    timeout=self.timeout_seconds,
)
response.raise_for_status()
```

- **En pocas palabras:** es la parte que "marca a Wikipedia por teléfono". Le dice qué buscar y espera la respuesta. Si Wikipedia tarda más de lo permitido, avisa en lugar de quedarse colgada.

- **Detalle técnico:** `requests.get` hace la petición HTTP; `params` añade el parámetro `search` a la URL; `raise_for_status()` lanza una excepción si la respuesta es un error (404, 500...); `timeout` evita bloqueos indefinidos. Los errores de tiempo de espera, conexión y HTTP se traducen a mensajes claros.

---

### 5. Separar el grano de la paja: `src/scraping/wikipedia_parser.py`

```python
content = soup.select_one("#mw-content-text .mw-parser-output")

for paragraph in content.find_all("p"):
    belongs_to_excluded_content = paragraph.find_parent(
        EXCLUDED_ANCESTOR_TAGS
    ) or paragraph.find_parent(class_=EXCLUDED_CONTAINER_CLASSES)

    if belongs_to_excluded_content:
        continue
```

- **En pocas palabras:** Wikipedia mezcla el artículo con cajas de información, menús y tablas. Este código "limpia" la página y se queda solo con los párrafos de texto del artículo (un máximo de 5).

- **Detalle técnico:** `BeautifulSoup` interpreta el HTML; `select_one` localiza el contenedor principal; `find_all("p")` recoge los párrafos; `find_parent` descarta los que están dentro de elementos no deseados (`aside`, `table`, `infobox`...). El límite `MAX_PARAGRAPHS = 5` corta el bucle con `break`. El método `extract_title` obtiene el título del encabezado `h1`.

---

### 6. El contenedor de datos: `src/models/article.py`

```python
@dataclass
class Article:
    title: str
    paragraphs: list[str]
    enriched: str = ""
    translated: str = ""
    summary: str = ""
```

- **En pocas palabras:** es una "ficha" donde se guarda lo encontrado sobre el tema: el título y los párrafos. Los campos `enriched`, `translated` y `summary` están reservados para el texto mejorado por la IA y para funciones futuras.

- **Detalle técnico:** un `dataclass` genera automáticamente el `__init__` y el `__repr__`. Los campos con valor por defecto (`""`) permiten crear instancias con solo el título y los párrafos.

---

### 7. Coordinar la búsqueda: `src/services/search_service.py`

```python
response = self.wikipedia_client.fetch(topic)
html = response.text

return Article(
    title=self.wikipedia_parser.extract_title(html),
    paragraphs=self.wikipedia_parser.extract_paragraphs(html),
)
```

- **En pocas palabras:** une las dos piezas anteriores: pide la página a Wikipedia y la convierte en una ficha `Article` lista para usar.

- **Detalle técnico:** el servicio recibe por parámetro un `WikipediaClient` y un `WikipediaParser`, lo que permite sustituirlos por versiones falsas en las pruebas sin acceder a la red.

---

### 8. La inteligencia artificial: `src/ai/`

Esta parte ya está escrita y probada:

- **`ai_client.py`** conecta con la API de Google Gemini y envía el texto para que la IA responda.

- **`prompts.py`** construye la instrucción que recibe la IA: ampliar el artículo sin inventar información y en el mismo idioma.

- **`content_enhancer.py`** junta los párrafos, pide el texto mejorado a la IA y lo guarda en el campo `enriched` del artículo.

Ejemplo de instrucción (en `prompts.py`):

```text
Expand and improve the provided article by explaining its ideas more clearly
and adding useful detail. Preserve all the information and facts from the
original text, and do not invent... Return only the enriched article text.
```

- **En pocas palabras:** es la "orden" que se le da a la IA: "mejora este texto, pero no inventes nada y respóndeme solo el texto".

- **Detalle técnico:** el prompt usa `str.format()` para inyectar el título y el texto, y delimita explícitamente la salida esperada para reducir respuestas con texto sobrante (saludos, comentarios). Si falta la clave de Gemini, el cliente lanza un error claro.

---

### 9. Mostrar el artículo: `src/ui/article_display.py`

- **En pocas palabras:** imprime en pantalla el artículo original y, debajo, el mejorado por la IA, con un encabezado que los diferencia.

- **Detalle técnico:** `show_original_article` imprime el título y los párrafos separados; `show_enriched_article` imprime el encabezado `CONTENIDO ENRIQUECIDO (IA)` y el texto, o un mensaje si no hay contenido.

---

### 10. La configuración: `src/settings.py`

- **En pocas palabras:** lee tu configuración desde un archivo `.env`, como la clave de Gemini y cuántos segundos esperar a Wikipedia.

- **Detalle técnico:** `load_settings()` usa `python-dotenv` para cargar las variables de entorno (`GEMINI_API_KEY`, `WIKIPEDIA_TIMEOUT`) y devuelve un `Settings` inmutable (`frozen=True`).

---

## 🗂️ Estructura del proyecto

```text
proyecto_salomon/
├── src/
│   ├── main.py                            → Punto de entrada (dirige todo)
│   ├── settings.py                        → Configuración (.env)
│   ├── exceptions.py                      → Errores personalizados
│   ├── ui/
│   │   ├── topic_input.py                 → Pide el tema
│   │   ├── search_continuation_prompt.py  → Pregunta repetir o salir
│   │   └── article_display.py             → Muestra el artículo
│   ├── services/
│   │   └── search_service.py              → Coordina búsqueda + parseo
│   ├── scraping/
│   │   ├── wikipedia_client.py            → Descarga la página
│   │   └── wikipedia_parser.py            → Extrae título y párrafos
│   ├── models/
│   │   └── article.py                     → Guarda los datos del artículo
│   ├── ai/
│   │   ├── ai_client.py                   → Conexión con Gemini
│   │   ├── prompts.py                     → Instrucción para la IA
│   │   └── content_enhancer.py            → Pide el texto mejorado
│   └── export/
│       └── exporter.py                    → Exportación a archivos (pendiente)
├── features/                              → Escenarios de ejemplo (Gherkin)
├── test/                                  → Pruebas automáticas
├── requirements.txt                       → Dependencias
└── .env.example                           → Ejemplo de configuración
```

---

## 🚀 Cómo instalarla y usarla

- **Paso 1 — Clonar el repositorio:**

  ```bash
  git clone https://github.com/cristinarodriguezl-dev/proyecto_salomon.git
  cd proyecto_salomon
  ```

- **Paso 2 — Crear un entorno virtual:**

  ```bash
  python -m venv .venv
  source .venv/bin/activate   # Linux/macOS
  .venv\Scripts\activate      # Windows
  ```

- **Paso 3 — Instalar las dependencias:**

  ```bash
  pip install -r requirements.txt
  ```

- **Paso 4 — Configurar las variables de entorno:**

  Copia `.env.example` a `.env` y rellena tus datos:

  ```env
  GEMINI_API_KEY=tu_clave_aqui
  WIKIPEDIA_TIMEOUT=10
  ```

- **Paso 5 — Ejecutar la app:**

  ```bash
  python -m src.main
  ```

- **Paso 6 — Ejecutar las pruebas (opcional):**

  ```bash
  pytest
  ```

---

## 🧪 Pruebas

El proyecto incluye pruebas automáticas en la carpeta `test/` que cubren:

- La búsqueda en Wikipedia y sus errores de red y de tiempo de espera.

- El parser (extracción del título y de los párrafos).

- La entrada del usuario, la pregunta de repetir o salir y la muestra del artículo.

- Los prompts, el cliente de IA y la configuración.

- El flujo completo en `test_main.py`, usando respuestas simuladas para no depender de internet.

Se ejecutan con `pytest`. La cobertura mínima exigida es del 70 % y está configurada en `pytest.ini`.

También hay escenarios de ejemplo en la carpeta `features/` (formato Gherkin) que describen el comportamiento esperado en lenguaje natural.
