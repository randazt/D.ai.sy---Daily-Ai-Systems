"""
Agent registry for D.AI.SY.

Provides a central location for creating and retrieving
agent instances.
"""

from app.agents.conversation_agent import ConversationAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.execution_agent import ExecutionAgent

from app.services.gemini_service import GeminiService


class AgentRegistry:
    """
    Stores and provides access to D.AI.SY agents.
    """

    def __init__(self):
        gemini_service = GeminiService()

        self._agents = {
    "conversation": ConversationAgent(gemini_service),
    "planner": PlannerAgent(),
    "execution": ExecutionAgent(),
}

    def get(self, name: str):
        """
        Retrieve an agent by name.
        """
        if name not in self._agents:
            raise ValueError(f"Unknown agent: {name}")

        return self._agents[name]

    def list(self):
        """
        Return a list of registered agent names.
        """
        return list(self._agents.keys())


registry = AgentRegistry()