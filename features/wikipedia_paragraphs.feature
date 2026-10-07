Feature: Extraer los primeros párrafos del artículo de Wikipedia
  Scenario: El artículo contiene más de cinco párrafos con texto
    Given una respuesta HTML con contenido principal, navegación y párrafos vacíos
    When se extraen los párrafos del artículo
    Then se devuelven los primeros cinco párrafos con contenido en orden
    And se ignora el texto ajeno al artículo

  Scenario: El artículo contiene menos de cinco párrafos con texto
    Given una respuesta HTML con menos de cinco párrafos en el contenido principal
    When se extraen los párrafos del artículo
    Then se devuelven todos los párrafos disponibles en orden
