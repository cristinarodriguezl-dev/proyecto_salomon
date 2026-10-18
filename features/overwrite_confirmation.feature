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

  Scenario: Corregir una respuesta no válida a la confirmación
    Given: ya existe un archivo llamado informe.txt
    When: el usuario responde algo distinto de sí o no a la confirmación
    Then: recibe un mensaje claro y se le vuelve a preguntar