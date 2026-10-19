Feature: Elegir la versión del artículo que se va a guardar
  Scenario: Guardar el contenido original
    Given un artículo con varios párrafos originales
    When el usuario elige la versión original
    Then se utiliza el texto original con sus párrafos separados

  Scenario: Guardar una versión generada
    Given un artículo con versiones enriquecida y traducida
    When el usuario elige una de esas versiones
    Then se utiliza el texto de la versión elegida sin sustituir el original

  Scenario: Solo se ofrecen las versiones disponibles
    Given un artículo que solo tiene contenido original
    When el menú de versiones se muestra
    Then la única opción disponible es la versión original
