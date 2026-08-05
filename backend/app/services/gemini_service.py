import os
import traceback

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


class GeminiService:
    def generate(self, message: str):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=message,
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