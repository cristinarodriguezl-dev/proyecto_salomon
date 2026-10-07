"""Headers and separators shared by terminal and document outputs."""

TITLE_HEADER = "TITLE"
ORIGINAL_HEADER = "ORIGINAL"
ENRICHED_HEADER = "ENRICHED"
TRANSLATED_HEADER = "TRANSLATED"

SECTION_SEPARATOR = "=" * 60
SUBSECTION_SEPARATOR = "-" * 60


def format_title(text: str) -> str:
    """Wrap the article title between section separators."""
    return "\n".join([SECTION_SEPARATOR, text, SECTION_SEPARATOR])


def format_section(header: str, body: str = "") -> str:
    """Render one version with its header and separators."""
    lines = [header, SUBSECTION_SEPARATOR]
    if body:
        lines.append(body)
    lines.append(SUBSECTION_SEPARATOR)
    return "\n".join(lines)
