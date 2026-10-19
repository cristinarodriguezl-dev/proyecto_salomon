# Entradas interactivas con `questionary`

La aplicación ya no usa `input()` para preguntar al usuario. Todas las preguntas
se hacen con la librería [`questionary`](https://github.com/tmbo/questionary)
(instalada en `requirements.txt`), de modo que:

- Las preguntas de opción (sí/no, formato, versión, idioma, repetir o salir)
  se contestan moviéndote con las **flechas** y pulsando **Enter**.
- Las preguntas de texto libre (tema de búsqueda y nombre del archivo) se
  escriben en una línea de texto de `questionary`.
- Como solo se puede elegir entre las opciones mostradas, desaparecen los
  mensajes de "respuesta no válida" y los bucles de reintento de esas
  preguntas. Sigue existiendo validación de texto para el tema vacío y para
  nombres de archivo con rutas o caracteres prohibidos.

En el código se usa siempre `questionary.<tipo>(...).unsafe_ask()`:
`unsafe_ask()` devuelve la respuesta y deja propagarse `Ctrl+C`/`Ctrl+D`,
igual que hacía `input()`.

## Cambios archivo a archivo

### `src/ui/topic_input.py`

`request_topic()` usa `questionary.text(PROMPT_MESSAGE)`. El bucle que repite la
pregunta cuando el tema queda vacío se mantiene, con el mismo
`EMPTY_INPUT_MESSAGE`.

### `src/ui/summary_confirmation_prompt.py` y `src/ui/export_confirmation_prompt.py`

La pregunta s/n se convierte en un menú con las opciones `Sí` y `No`
(`questionary.select`) y se devuelve `True` solo si se elige `Sí`. Se eliminan
las constantes de respuestas válidas (`YES_ANSWERS`, `NO_ANSWERS`) y el mensaje
`Respuesta no válida. Escribe s o n.`.

### `src/ui/search_continuation_prompt.py`

El menú "1. Buscar otro tema / 2. Salir" se muestra con `questionary.select` y
las opciones pasan a llamarse `Buscar otro tema` y `Salir`. `ask_search_again()`
devuelve `True` o `False` según la opción elegida; se eliminan `VALID_OPTIONS`
y el mensaje `Opción no válida. Escribe 1 o 2.`.

### `src/ui/export_version_prompt.py`

`ask()` ofrece con `questionary.select` solo las versiones que existen
(`Original`, `Enriquecida`, `Traducida`) y devuelve directamente el contenido
de la elegida. Se elimina el mensaje `Esa versión no está disponible...`.

### `src/ui/export_destination_prompt.py`

- El formato se elige con `questionary.select` entre `TXT` y `PDF`
  (generados a partir de `VALID_FORMATS`), así que desaparece
  `INVALID_FORMAT_MESSAGE`.
- El nombre del archivo se escribe con `questionary.text` y conserva toda la
  validación anterior (`EMPTY_NAME_MESSAGE`, `INVALID_NAME_MESSAGE`,
  `WRONG_EXTENSION_MESSAGE`).
- La confirmación de sobrescritura es un menú `Sí`/`No` y ya no necesita
  `INVALID_ANSWER_MESSAGE`, `YES_ANSWERS` ni `NO_ANSWERS`.
- Los mensajes pierden el ": " final y el "(s/n)", porque `questionary` ya
  muestra el formato de la pregunta.

### `src/ui/translation_language_prompt.py`

`ask()` construye un `questionary.select` con un `Choice` por idioma
(título `código - nombre`, valor `código`) y una última opción
`Omitir traducción`. Se devuelve el código elegido o `None` cuando se omite;
ya no hace falta comprobar si el idioma está admitido.

### `docs/README.md` y `features/`

- El README explica la navegación con flechas y sus ejemplos de código ya no
  usan `input()`.
- Los escenarios Gherkin que describían respuestas inválidas escritas a mano
  (opción inexistente, formato erróneo, versión no disponible, respuesta rara
  a la confirmación) se reemplazan por escenarios de selección con el menú.

## Cambios en las pruebas

Los tests de `test/` simulaban la entrada del usuario con
`monkeypatch.setattr("builtins.input", ...)`. Ahora cada fichero de pruebas que
necesita respuestas define un pequeño `install_questionary(monkeypatch,
answers)` que:

1. Sustituye `questionary.text`, `questionary.select` y `questionary.confirm`
   por una función que devuelve un objeto con `unsafe_ask()`.
2. Devuelve la respuesta siguiente de la lista `answers` (en el orden en que el
   programa hace las preguntas).
3. Registra los mensajes (`prompts.messages`) y las opciones ofrecidas
   (`prompts.choices`) para poder comprobarlos.

Las respuestas de los menús son ahora los textos o valores que devuelve
`questionary`: `"No"`/`"Sí"` para las confirmaciones, `"TXT"`/`"PDF"` para el
formato, `"Original"`/`"Enriquecida"`/`"Traducida"` para la versión,
`"en"`/`"fr"` para el idioma y `"Buscar otro tema"`/`"Salir"` para el menú de
continuación.

Se eliminan las pruebas de respuestas inválidas escritas a mano (ya no existen
esos bucles de validación) y se sustituyen por comprobaciones de las opciones
que el programa ofrece en cada menú.

## Verificación

```bash
python -m pytest
```

La suite completa pasa (142 pruebas) y la cobertura se mantiene por encima del
70 % exigido en `pytest.ini`.
