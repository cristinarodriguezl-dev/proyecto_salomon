   Feature: Repetir otra búsqueda o terminar el programa
     Scenario: El usuario decide buscar otro tema
       Given un artículo mostrado en la terminal
       When el usuario elige buscar otro tema
       Then el sistema solicita un nuevo tema y muestra su artículo

     Scenario: El usuario decide salir
       Given un artículo mostrado en la terminal
       When el usuario elige salir
       Then el sistema muestra "Programa finalizado." y termina sin errores

     Scenario: Solo se pueden elegir las opciones del menú
       Given un artículo mostrado en la terminal
       When el menú de continuación se muestra
       Then las únicas opciones disponibles son "Buscar otro tema" y "Salir"
       And la respuesta se confirma con la tecla Enter