from src.translation.translation_service import TranslationService


def main():
    service = TranslationService()

    text = (
        "La inteligencia artificial permite que los "
        "ordenadores realicen tareas que requieren "
        "capacidades similares a las humanas."
    )

    try:
        translated = service.translate(
            content=text,
            target_language="en",
            source_language="es",
        )

        print("\nTEXTO ORIGINAL:")
        print(text)

        print("\nTEXTO TRADUCIDO:")
        print(translated)

    except Exception as error:
        print(f"Error durante la prueba: {error}")


if __name__ == "__main__":
    main()
