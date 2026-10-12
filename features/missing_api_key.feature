Feature: Detectar la ausencia de la clave de Gemini
  Scenario: La clave de Gemini está configurada
    Given: una clave de Gemini configurada
    When: se solicita un texto a Gemini
    Then: se devuelve la respuesta de Gemini

  Scenario: Falla porque la clave de Gemini está ausente
    Given: una clave de Gemini vacía
    When: se solicita un texto a Gemini
    Then: se informa de forma controlada de que falta la clave
    And: no se llama a Gemini