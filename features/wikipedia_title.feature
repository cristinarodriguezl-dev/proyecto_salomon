Feature: Extraer el título principal de un artículo de Wikipedia
  Scenario: El HTML contiene un artículo válido
    Given una respuesta HTML con el título principal del artículo
    When se procesa el HTML recibido de Wikipedia
    Then se devuelve solo el nombre del artículo

  Scenario: El HTML no contiene un título principal válido
    Given una respuesta HTML sin el encabezado principal del artículo
    When se procesa el HTML recibido de Wikipedia
    Then se informa claramente que no se encontró un título válido
