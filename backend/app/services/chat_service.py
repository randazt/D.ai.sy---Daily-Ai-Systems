from app.services.gemini_service import gemini_service


class ChatService:
    def chat(self, message: str):
        return gemini_service.generate(message)


chat_service = ChatService()