   Feature: Repetir otra búsqueda o terminar el programa
     Scenario: El usuario decide buscar otro tema
       Given un artículo mostrado en la terminal
       When el usuario elige buscar otro tema
       Then el sistema solicita un nuevo tema y muestra su artículo

     Scenario: El usuario decide salir
       Given un artículo mostrado en la terminal
       When el usuario elige salir
       Then el sistema muestra "Programa finalizado." y termina sin errores

     Scenario: Falla porque la opción elegida no es válida
       Given un artículo mostrado en la terminal
       When el usuario introduce una opción que no existe
       Then el sistema informa de que la opción no es válida y vuelve a preguntar