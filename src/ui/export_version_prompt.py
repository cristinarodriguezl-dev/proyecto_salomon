"""Permite elegir qué versión de un artículo se guardará."""

from src.models.article import Article


class ExportVersionPrompt:
    """Muestra solo las versiones disponibles y devuelve el texto elegido."""

    def ask(self, article: Article) -> str:
        """Pregunta hasta que el usuario elija una versión disponible."""
        versions = {"1": ("Original", "\n\n".join(article.paragraphs))}

        if article.enriched.strip():
            versions["2"] = ("Enriquecida", article.enriched)
        if article.translated.strip():
            versions["3"] = ("Traducida", article.translated)

        while True:
            print("\n¿Qué versión quieres guardar?")
            for option, (label, _) in versions.items():
                print(f"{option}. {label}")

            choice = input("Elige una opción: ").strip()
            if choice in versions:
                return versions[choice][1]

            print("Esa versión no está disponible. Elige una de las opciones mostradas.")
