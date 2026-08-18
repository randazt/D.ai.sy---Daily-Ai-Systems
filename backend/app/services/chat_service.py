from app.agents.registry import registry
from app.orchestration.router import router


class ChatService:
    """
    Coordinates requests through D.AI.S.Y.'s orchestration layer.

    ChatService is responsible for routing a request to the
    appropriate registered agent and returning that agent's result.

    Project state is owned by the agents and ProjectService,
    not duplicated here.
    """

    async def chat(self, message: str):

        # Determine which agent should handle the request
        agent_name = router.route(message)

        # Retrieve the selected agent
        agent = registry.get(agent_name)

        # Execute the selected agent
        result = await agent.run(message)

        # Return the agent result without duplicating domain state
        return result


# Singleton instance
chat_service = ChatService()