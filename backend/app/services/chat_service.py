from app.agents.registry import registry
from app.orchestration.router import router
from app.services.clarification_service import (
    ClarificationService,
    ClarificationTokenError,
    clarification_service,
)


class ChatService:
    """
    Coordinates requests through D.AI.S.Y.'s orchestration layer.

    ChatService is responsible for routing a request to the
    appropriate registered agent and returning that agent's result.

    Project state is owned by the agents and ProjectService,
    not duplicated here.
    """

    def __init__(
        self,
        *,
        agent_registry=registry,
        agent_router=router,
        clarification_gate: ClarificationService = clarification_service,
    ):
        self._registry = agent_registry
        self._router = agent_router
        self._clarification_gate = clarification_gate

    async def chat(self, message: str, clarification_token: str | None = None):
        if clarification_token:
            return await self._answer_clarification(
                message=message,
                clarification_token=clarification_token,
            )

        # Determine which agent should handle the request
        agent_name = self._router.route(message)

        if agent_name == "planner":
            clarification = self._clarification_gate.evaluate(message)
            if clarification.needs_clarification:
                try:
                    return self._clarification_gate.create_clarification_response(
                        original_goal=message,
                        question=clarification.question,
                    )
                except ClarificationTokenError:
                    return self._clarification_gate.invalid_context_response(
                        "Clarification is unavailable. Please restate your goal clearly."
                    )

        # Retrieve the selected agent
        agent = self._registry.get(agent_name)

        # Execute the selected agent
        result = await agent.run(message)

        # Return the agent result without duplicating domain state
        return result

    async def _answer_clarification(
        self,
        *,
        message: str,
        clarification_token: str,
    ):
        try:
            payload = self._clarification_gate.validate_token(clarification_token)
        except ClarificationTokenError:
            return self._clarification_gate.invalid_context_response()

        if self._is_execution_command(message):
            return self._clarification_gate.invalid_context_response(
                "Clarification answer cannot be an execution command. "
                "Please answer the clarification question or omit the token to start over."
            )

        planner = self._registry.get("planner")
        clarified_goal = self._build_clarified_goal(
            original_goal=payload["original_goal"],
            question=payload["question"],
            answer=message,
        )
        return await planner.run(clarified_goal)

    @staticmethod
    def _is_execution_command(message: str) -> bool:
        return message.strip().lower() in {
            "execution",
            "/execution",
            "/execute",
            "execute",
            "run",
        }

    @staticmethod
    def _build_clarified_goal(
        *,
        original_goal: str,
        question: str,
        answer: str,
    ) -> str:
        return (
            f"Original goal: {original_goal}\n\n"
            f"Clarification question: {question}\n"
            f"User clarification answer: {answer}"
        )


# Singleton instance
chat_service = ChatService()
