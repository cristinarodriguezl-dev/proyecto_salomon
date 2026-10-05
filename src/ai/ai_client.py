from google import genai

MODEL_NAME = "gemini-3.8-flash"

class AIClient:
    """Talks to the Gemini API."""
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)

    def generate_text(self, prompt):
        """Send a prompt to Gemini and return its answer as text."""
        response = self.client.models.generate_content(model=MODEL_NAME, contents=prompt)
        return response.text

