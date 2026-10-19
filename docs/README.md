# 📚 Content Enrichment (Salomón)

Aplicación de consola que busca un tema en **Wikipedia**, enriquece el artículo con **Google Gemini**, permite resumirlo y traducirlo con **MyMemory**, y guarda la versión elegida en **TXT o PDF**.

No hace falta saber programar para usarla: la propia aplicación te va preguntando qué quieres buscar y qué hacer a continuación.

Las preguntas se contestan con el teclado: escribes cuando te pide un texto y, cuando te ofrece opciones, te mueves con las **flechas** y confirmas con **Enter**.

---

## 🎯 ¿Qué hace la app?

- Te pide que escribas un tema (por ejemplo: "Python", "Mercurio" o "Árbol").

- Busca ese tema en la Wikipedia en español.

- Muestra el título y los primeros párrafos del artículo original.

- Pide a la inteligencia artificial (Google Gemini) que amplíe y mejore ese texto.

- Muestra el artículo mejorado en pantalla.

- Ofrece un resumen del contenido enriquecido y lo muestra en la terminal.

- Permite traducir al alemán, inglés, español, francés, italiano o portugués, conservando el orden y la separación de los párrafos.

- Permite guardar la versión original, enriquecida o traducida en TXT o PDF, con el nombre que elijas.

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

  Imprime el resultado de la IA debajo del original. Si Gemini falla, explica el problema y conserva el artículo original para continuar.

- **Paso 8 — Ofrece generar un resumen.**

  Si respondes que sí, pide a Gemini un resumen del texto enriquecido y lo muestra en la terminal. Si no hay contenido enriquecido o el servicio falla, informa del problema y continúa. El resumen se muestra, pero no aparece entre las versiones disponibles para guardar.

- **Paso 9 — Ofrece traducir.**

  Puedes elegir un código o nombre de idioma admitido, o escribir `0` para omitir la traducción. Se traduce el contenido enriquecido; si no existe, se usa el original. La traducción se guarda por separado y se muestra con el nombre del idioma. Ante un fallo, puedes elegir otro idioma, reintentar u omitir.

- **Paso 10 — Ofrece guardar el resultado.**

  Si aceptas, eliges una de las versiones disponibles: original, enriquecida o traducida. Después indicas TXT o PDF y un nombre de archivo sin ruta. Se guarda en la carpeta `exports/`, dentro del directorio desde el que ejecutas el programa. La carpeta se crea automáticamente al exportar si todavía no existe. Si el archivo existe, se pide confirmación antes de sobrescribirlo; si rechazas, puedes indicar otro nombre. Un error de escritura se muestra sin impedir continuar o salir.

- **Paso 11 — Te pregunta qué hacer.**

  Te ofrece "Buscar otro tema" o "Salir". Te mueves entre las dos opciones con las flechas y confirmas con Enter: si eliges buscar otro, el proceso empieza de nuevo; si eliges salir, muestra "Programa finalizado." y termina.

---

## 💻 El código más importante, explicado

En cada parte del código verás dos explicaciones:

- **En pocas palabras:** para quien no programa.

- **Detalle técnico:** para quien sí programa.

### 1. El director de orquesta: `src/main.py`

Es el punto de entrada. Carga y valida la configuración una sola vez, construye los servicios y coordina los pasos anteriores. El tiempo de espera configurado llega al cliente de Wikipedia:

```python
settings = load_settings()
search_service = WikipediaSearchService(
    wikipedia_client=WikipediaClient(timeout_seconds=settings.wikipedia_timeout)
)
ai_client = AIClient(settings.gemini_api_key)
```

- **En pocas palabras:** si la búsqueda falla, vuelve a pedir un tema. Si sale bien, presenta el artículo y ofrece resumen, traducción y guardado antes de preguntar si quieres continuar.

- **Detalle técnico:** captura errores de búsqueda, enriquecimiento, resumen, traducción y exportación en cada etapa. Una configuración inválida se informa antes de iniciar los clientes. Un fallo de Gemini conserva el original; un fallo de traducción repite la selección de idioma. `ask_search_again()` decide si empieza otra consulta o termina.

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

- **En pocas palabras:** es una "ficha" donde se guardan el título y los párrafos originales. Los campos `enriched`, `translated` y `summary` contienen, respectivamente, el texto mejorado, su traducción y el resumen. Estas versiones se guardan sin sustituir los párrafos originales.

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

- **`content_summarizer.py`** pide un resumen del contenido enriquecido y lo guarda en `summary` cuando el usuario lo solicita.

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

- **En pocas palabras:** muestra el artículo original, el mejorado por la IA y la traducción disponible. El resumen se presenta desde `summary_display.py`.

- **Detalle técnico:** `show_original_article` imprime el título y los párrafos separados; `show_enriched_article` imprime `CONTENIDO ENRIQUECIDO (IA)`; `show_translated_article` imprime `CONTENIDO TRADUCIDO` con el idioma de destino y el contenido de `article.translated`.

---

### 10. La configuración: `src/settings.py`

- **En pocas palabras:** lee tu configuración desde un archivo `.env`, como la clave de Gemini y cuántos segundos esperar a Wikipedia.

- **Detalle técnico:** `python-dotenv` carga el archivo `.env` y `load_settings()` devuelve un `Settings` inmutable (`frozen=True`). `WIKIPEDIA_TIMEOUT` debe ser un entero mayor que cero; si falta se usan 10 segundos. `main()` pasa ese valor al cliente de Wikipedia y muestra un error controlado si la configuración no es válida.

---

### 11. Traducción y exportación

- `TranslationService` consulta directamente la API HTTP de MyMemory y valida los idiomas. `ArticleTranslator` traduce cada párrafo por separado y solo guarda la traducción completa en `article.translated` cuando termina correctamente.
- Los selectores de terminal recogen la versión, el formato y el nombre del documento. Solo se permite guardar una versión que exista en el artículo.
- `ExportService` selecciona `TxtExporter` o `PdfExporter`. Ambos guardan el título y el contenido elegido. El TXT usa UTF-8 y un encabezado subrayado; el PDF organiza el título y los párrafos en páginas A4.
- Los nombres no pueden incluir rutas ni caracteres prohibidos. La extensión se añade si falta y debe coincidir con el formato elegido. Los archivos TXT y PDF se guardan en `exports/`, una ruta relativa al directorio de ejecución. Por ejemplo, si ejecutas el programa desde `proyecto_salomon/`, el nombre `informe` en formato TXT se guarda en `proyecto_salomon/exports/informe.txt`. `ExportService` crea la carpeta automáticamente al guardar si no existe y comunica los errores de creación o escritura para permitir continuar o salir.

---

## 🗂️ Estructura del proyecto

```text
proyecto_salomon/
├── src/
│   ├── main.py                            → Punto de entrada (dirige todo)
│   ├── settings.py                        → Configuración (.env)
│   ├── exceptions.py                      → Errores personalizados
│   ├── ui/                               → Preguntas y presentación en terminal
│   ├── services/                         → Coordinación de búsqueda y parseo
│   ├── scraping/                         → Cliente y parser de Wikipedia
│   ├── models/                           → Article y sus distintas versiones
│   ├── ai/                               → Cliente Gemini, enriquecimiento y resumen
│   ├── translation/                      → MyMemory y traducción por párrafos
│   └── export/                           → Servicio y exportadores TXT/PDF
├── docs/README.md                        → Documentación de instalación y uso
├── features/                              → Escenarios de ejemplo (Gherkin)
├── test/                                  → Pruebas automáticas
├── pytest.ini                            → Cobertura mínima automatizada
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

  El tiempo de espera se expresa en segundos y debe ser un entero positivo. Por ejemplo, `WIKIPEDIA_TIMEOUT=5` aplica cinco segundos a cada consulta a Wikipedia. La clave de Gemini se necesita para enriquecer y resumir; si falta o falla la IA, el programa informa y permite continuar con el artículo original.

- **Paso 5 — Ejecutar la app:**

  ```bash
  python -m src.main
  ```

- **Paso 6 — Ejecutar las pruebas (opcional):**

  ```bash
  python -m pytest
  ```

---

## 🧪 Pruebas

El proyecto incluye pruebas automáticas en la carpeta `test/` que cubren:

- La búsqueda en Wikipedia y sus errores de red y de tiempo de espera.

- El parser (extracción del título y de los párrafos).

- La entrada del usuario, la pregunta de repetir o salir y la muestra del artículo.

- Los prompts, el cliente de IA y la configuración.

- La traducción por párrafos, las respuestas defectuosas de MyMemory y la validación de textos e idiomas.

- La selección de versiones, la confirmación de sobrescritura y la exportación real a TXT y PDF.

- El flujo completo en `test_full_flow_integration.py`, simulando Wikipedia, Gemini y MyMemory para no depender de claves, cuotas ni disponibilidad de las APIs.

- La aplicación del tiempo de espera de Wikipedia desde `main()`, su valor predeterminado y el manejo de una configuración inválida.

Se ejecutan con `python -m pytest`. El umbral automatizado actual es del 70 % y está configurado en `pytest.ini`. El informe muestra la cobertura medida y las líneas pendientes; superar ese umbral no equivale a alcanzar el objetivo del 100 % de HU-19.

También hay escenarios de ejemplo en la carpeta `features/` (formato Gherkin) que describen el comportamiento esperado en lenguaje natural.
