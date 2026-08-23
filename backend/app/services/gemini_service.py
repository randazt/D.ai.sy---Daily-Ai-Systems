import os
import traceback
from typing import Any

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


class GeminiService:
    def generate(self, message: str, config: Any = None):
        try:
            request = {
                "model": "gemini-3.5-flash-lite",
                "contents": message,
            }
            if config is not None:
                request["config"] = config

            response = client.models.generate_content(
                **request,
            )

            return {
                "reply": response.text
            }

        except Exception as e:
            traceback.print_exc()

            return {
                "error": str(e)
            }


gemini_service = GeminiService()
