Feature: Resolver búsquedas de Wikipedia sin resultado válido
  Scenario: El tema no tiene un artículo válido
    Given Wikipedia no devuelve un artículo con contenido válido
    When se busca ese tema
    Then se informa que no se encontró un artículo
    And se permite introducir otro tema

  Scenario: El tema lleva a una página de desambiguación
    Given Wikipedia clasifica la página como desambiguación
    When se busca ese tema
    Then se indica que el tema es ambiguo y se sugiere concretarlo
    And se permite introducir otro tema
