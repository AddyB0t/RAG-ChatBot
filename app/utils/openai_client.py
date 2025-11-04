import os
import json
import logging
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class OpenAIClient:
    """Direct OpenAI API client"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.base_url = "https://api.openai.com/v1/chat/completions"

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

    def invoke(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Send a prompt to OpenAI and return the response

        Args:
            prompt: The prompt to send
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response

        Returns:
            The model's response text
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": temperature
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"]

        except requests.exceptions.RequestException as e:
            logger.error(f"OpenAI API request failed: {e}")
            raise
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to parse OpenAI response: {e}")
            raise
