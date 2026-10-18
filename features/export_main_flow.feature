# language: es
Característica: Exportar un artículo desde el recorrido principal

  Escenario: Guardar la versión enriquecida en TXT y seguir buscando
    Dado que Wikipedia devuelve un artículo válido
    Y la IA genera una versión enriquecida
    Cuando el usuario elige guardar la versión enriquecida en TXT
    Y escribe un nombre de archivo válido
    Entonces se crea un TXT con el título y el texto enriquecido
    Y el usuario puede buscar otro tema o salir

  Escenario: Salir sin guardar
    Dado que se ha mostrado un artículo
    Cuando el usuario decide no guardarlo
    Entonces puede buscar otro tema o salir
