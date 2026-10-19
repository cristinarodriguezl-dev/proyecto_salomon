ENRICHMENT_PROMPT = """
Title: {title}

Text: {text}

Expand and improve the provided article by explaining its ideas more clearly and adding useful detail.
Preserve all the information and facts from the original text, and do not invent, assume, or add any unsupported information.
Write the response in the same language as the original article.
Return only the enriched article text, without greetings, introductions, explanations, comments, or any other additional text.
""".strip()

SUMMARY_PROMPT = """
Title: {title}

Text: {text}

Summarize the provided text by explaining its main ideas in a short and clear summary.
Use only the information in the text, and do not invent, assume, or add any unsupported information.
Write the response in the same language as the text.
Return only the summary, without greetings, introductions, explanations, comments, or any other additional text.
""".strip()


def build_enrichment_prompt(title, text):
    """Return the prompt that asks Gemini to enrich an article."""
    return ENRICHMENT_PROMPT.format(title=title, text=text)


def build_summary_prompt(title, text):
    """Return the prompt that asks Gemini to summarize a text."""
    return SUMMARY_PROMPT.format(title=title, text=text)
