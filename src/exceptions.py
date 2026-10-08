class ContentEnricherError(Exception):
    """Clase base de todos los errores que lanza el proyecto."""


class SearchError(ContentEnricherError):
    """No se pudo consultar Wikipedia o no devolvió un artículo válido."""


class EnrichmentError(ContentEnricherError):
    """La IA no pudo enriquecer el contenido."""


class TranslationError(ContentEnricherError):
    """No se pudo traducir el contenido."""


class ExportError(ContentEnricherError):
    """No se pudo guardar el contenido en un archivo."""