Feature: Avisar si el archivo de destino ya existe

  Scenario: Sobrescribir un archivo existente tras confirmarlo
    Given: ya existe un archivo llamado informe.txt
    When: el usuario elige TXT, escribe el nombre informe y confirma la sobrescritura
    Then: el destino preparado es informe.txt

  Scenario: Elegir otro nombre al rechazar la sobrescritura
    Given: ya existe un archivo llamado informe.txt
    When: el usuario elige TXT, escribe el nombre informe y rechaza la sobrescritura
    Then: el archivo existente se conserva sin cambios
    And: el programa le pide otro nombre de archivo

  Scenario: La confirmación solo admite sí o no
    Given: ya existe un archivo llamado informe.txt
    When: el usuario elige entre "Sí" y "No" con las flechas
    Then: el programa aplica la opción elegida sin volver a preguntar