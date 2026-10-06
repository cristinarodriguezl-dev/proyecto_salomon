Feature: Gestionar errores de la consulta HTTP a Wikipedia
  Scenario: No se puede establecer conexión con Wikipedia
    Given Wikipedia no está disponible para la conexión
    When se consulta un tema
    Then se informa claramente que no se pudo conectar

  Scenario: Wikipedia responde con un estado HTTP de error
    Given Wikipedia responde con un código HTTP de error
    When se consulta un tema
    Then se informa claramente del código de error recibido
