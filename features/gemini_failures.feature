Feature: Explicar los fallos de Gemini y continuar con el contenido original
  Scenario Outline: Gemini falla al enriquecer el artículo
    Given un artículo obtenido de Wikipedia
    When Gemini falla por <motivo>
    Then se explica el problema con un mensaje claro
    And se mantiene el artículo original de Wikipedia
    And la aplicación sigue permitiendo buscar otro tema o salir

    Examples:
      | motivo                       |
      | una clave inválida           |
      | el tiempo de espera agotado  |
      | el límite de uso             |
      | un fallo del servicio        |
      | un fallo de conexión         |
