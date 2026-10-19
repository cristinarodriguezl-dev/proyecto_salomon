Feature: Elegir el formato y el nombre para exportar un documento
  Scenario: Elegir un destino TXT válido
    Given el usuario elige el formato TXT
    When escribe el nombre informe
    Then el destino preparado es informe.txt

  Scenario: Elegir el formato desde el menú
    Given el menú de formato se muestra
    When el usuario elige PDF con las flechas y pulsa Enter
    Then puede escribir el nombre del archivo

  Scenario: Corregir un nombre vacío
    Given el usuario elige un formato admitido
    When deja vacío el nombre del archivo
    Then recibe un mensaje claro y puede introducir otro nombre

  Scenario: Corregir una ruta no válida
    Given el usuario elige un formato admitido
    When escribe una ruta como ../informe
    Then recibe un mensaje claro y puede introducir otro nombre
