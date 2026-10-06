Feature: Consulta HTTP a Wikipedia con tiempo de espera
  Scenario: Wikipedia devuelve una respuesta válida
    Given un tema solicitado por el usuario
    And Wikipedia responde a la consulta
    When se consulta Wikipedia con un tiempo de espera definido
    Then se devuelve la respuesta recibida

  Scenario: Wikipedia tarda más que el tiempo de espera
    Given un tema solicitado por el usuario
    And la petición a Wikipedia supera el tiempo de espera
    When se consulta Wikipedia con un tiempo de espera definido
    Then se informa del timeout de forma controlada
