"""
LLM client module.

Wraps the Groq API client to send prompts to a hosted LLM
(Llama 3.3 70B) and return generated text responses.
"""

import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables (e.g. GROQ_API_KEY) from a local .env file.
load_dotenv()


class LLM:
    """Thin wrapper around the Groq chat completions API."""

    def __init__(self):
        # API key is read from the environment; must be set in .env as GROQ_API_KEY.
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"

    def generate(self, prompt: str) -> str:
        """
        Send a single-turn prompt to the LLM and return its text response.

        Args:
            prompt: The full prompt string (already includes any context,
                     history, and the user's question).

        Returns:
            The generated response text, with leading/trailing whitespace stripped.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()


# Singleton instance so the Groq client is created only once.
llm = LLM()