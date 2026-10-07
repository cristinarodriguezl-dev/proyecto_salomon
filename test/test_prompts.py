from src.ai.prompts import build_enrichment_prompt


def test_build_enrichment_prompt_includes_title_and_text():
    prompt = build_enrichment_prompt("Python", "Python is a language.")

    assert "Python" in prompt
    assert "Python is a language." in prompt