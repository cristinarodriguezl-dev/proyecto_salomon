from dataclasses import dataclass

@dataclass
class Article:
    title: str
    paragraphs: list[str]
    suggestion: str = ""
    enriched: str = ""
    translated: str = ""
    summary: str = ""