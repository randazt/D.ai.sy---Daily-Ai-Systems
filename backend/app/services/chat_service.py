from app.agents.conversation_agent import ConversationAgent
from app.services.gemini_service import GeminiService


class ChatService:
    """
    Coordinates chat requests through the agent layer.
    """

    def __init__(self, conversation_agent: ConversationAgent):
        self._conversation_agent = conversation_agent

    def chat(self, message: str):
        return self._conversation_agent.run(message)


chat_service = ChatService(
    ConversationAgent(
        GeminiService()
    )
)