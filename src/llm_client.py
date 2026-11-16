
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai


class GeminiClient:
    """Reusable client for communicating with Google's Gemini API."""

    def __init__(self, model="gemini-3.8-flash"):
        # Locate the project's .env file
        project_root = Path(__file__).resolve().parents[1]
        env_path = project_root / ".env"

        load_dotenv(dotenv_path=env_path)

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY was not found in the .env file."
            )

        self.client = genai.Client(api_key=api_key)
        self.model = model

    def generate_text(self, prompt):
        """Send a prompt to Gemini and return its response."""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        return response.text

    def close(self):
        """Close the Gemini client."""
        self.client.close()
