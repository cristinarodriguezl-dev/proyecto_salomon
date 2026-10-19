# language: en
Feature: Coordinar la búsqueda y mostrar el artículo original

  Scenario: Buscar y mostrar el artículo original
    Given que el usuario introduce un tema válido
    And Wikipedia devuelve el artículo encontrado
    When se ejecuta el flujo principal de búsqueda
    Then se consulta Wikipedia con el tema sin espacios sobrantes
    And se muestra el título y los párrafos originales

  Scenario: Reintentar la búsqueda cuando falla la conexión
    Given que la primera conexión con Wikipedia falla
    And el usuario introduce otro tema para reintentar
    When se ejecuta el flujo principal de búsqueda
    Then se informa claramente del fallo de conexión
    And se solicita otro tema y se muestra el artículo encontrado

  Scenario: Reintentar la búsqueda ante un error HTTP
    Given que la primera respuesta de Wikipedia contiene un error HTTP
    And el usuario introduce otro tema para reintentar
    When se ejecuta el flujo principal de búsqueda
    Then se informa claramente del código de error
    And se solicita otro tema y se muestra el artículo encontrado
