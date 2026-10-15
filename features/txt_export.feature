Feature: Guardar el contenido elegido en un archivo TXT
  Scenario: Guardar un artículo con título y párrafos
    Given un contenido con título, párrafos y caracteres especiales
    When se guarda el contenido en un archivo TXT
    Then el archivo empieza por el título como encabezado
    And los párrafos siguen separados por una línea en blanco
    And el texto conserva los acentos y los caracteres especiales