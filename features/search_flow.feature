# language: es
Característica: Coordinar la búsqueda y mostrar el artículo original

  Escenario: Buscar y mostrar el artículo original
    Dado que el usuario introduce un tema válido
    Y Wikipedia devuelve el artículo encontrado
    Cuando se ejecuta el flujo principal de búsqueda
    Entonces se consulta Wikipedia con el tema sin espacios sobrantes
    Y se muestra el título y los párrafos originales

  Escenario: Reintentar la búsqueda cuando falla la conexión
    Dado que la primera conexión con Wikipedia falla
    Y el usuario introduce otro tema para reintentar
    Cuando se ejecuta el flujo principal de búsqueda
    Entonces se informa claramente del fallo de conexión
    Y se solicita otro tema y se muestra el artículo encontrado

  Escenario: Reintentar la búsqueda ante un error HTTP
    Dado que la primera respuesta de Wikipedia contiene un error HTTP
    Y el usuario introduce otro tema para reintentar
    Cuando se ejecuta el flujo principal de búsqueda
    Entonces se informa claramente del código de error
    Y se solicita otro tema y se muestra el artículo encontrado
