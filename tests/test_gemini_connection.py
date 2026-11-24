import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


def test_gemini_connection():
    api_key = os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("GEMINI_MODEL")

    assert api_key, "GEMINI_API_KEY is missing from .env"
    assert model_name, "GEMINI_MODEL is missing from .env"

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model=model_name,
        contents="Reply with exactly: Gemini connection successful.",
    )

    assert response.text
    print("\nGemini response:", response.text)