from app.agents.registry import registry
from app.orchestration.router import router
from app.services.clarification_service import (
    ClarificationService,
    ClarificationTokenError,
    clarification_service,
)
from app.services.memory_authorization_service import (
    MemoryAuthorizationError,
    MemoryAuthorizationService,
    memory_authorization_service,
)
from app.services.memory_service import (
    MemoryService,
    memory_service,
)


class ChatService:
    """
    Coordinates requests through D.AI.S.Y.'s orchestration layer.

    ChatService is responsible for routing a request to the
    appropriate registered agent and returning that agent's result.

    Explicit memory proposal and approval actions are handled before
    normal routing so persistent user-owned memory cannot be created
    implicitly by an agent or by ordinary conversational language.

    A proposal does not persist memory. It binds the exact strategy
    presented by the human to the exact client identity in a signed,
    short-lived authorization token. Persistence happens only after
    that proposal is explicitly approved.

    Project state is owned by the agents and ProjectService,
    not duplicated here.
    """

    def __init__(
        self,
        *,
        agent_registry=registry,
        agent_router=router,
        clarification_gate: ClarificationService = clarification_service,
        memory_manager: MemoryService = memory_service,
        memory_authorization: MemoryAuthorizationService = (
            memory_authorization_service
        ),
    ):
        self._registry = agent_registry
        self._router = agent_router
        self._clarification_gate = clarification_gate
        self._memory_manager = memory_manager
        self._memory_authorization = memory_authorization

    async def chat(
        self,
        message: str,
        clarification_token: str | None = None,
        client_id: str | None = None,
        memory_action: str | None = None,
        memory_token: str | None = None,
    ):
        if memory_action is not None:
            return self._handle_memory_action(
                message=message,
                client_id=client_id,
                memory_action=memory_action,
                memory_token=memory_token,
            )

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
                        "Clarification is unavailable. "
                        "Please restate your goal clearly."
                    )

        # Retrieve the selected agent
        agent = self._registry.get(agent_name)

        # Execute the selected agent
        result = await agent.run(message)

        # Return the agent result without duplicating domain state
        return result

    def _handle_memory_action(
        self,
        *,
        message: str,
        client_id: str | None,
        memory_action: str,
        memory_token: str | None,
    ):
        if memory_action == "propose":
            return self._propose_memory_strategy(
                client_id=client_id,
                strategy=message,
            )

        if memory_action == "approve":
            return self._approve_memory_strategy(
                client_id=client_id,
                memory_token=memory_token,
            )

        return self._invalid_memory_authorization_response()

    def _propose_memory_strategy(
        self,
        *,
        client_id: str | None,
        strategy: str,
    ):
        if not client_id or not client_id.strip():
            return self._invalid_memory_authorization_response()

        if not strategy or not strategy.strip():
            return self._invalid_memory_authorization_response()

        normalized_client_id = client_id.strip()
        normalized_strategy = strategy.strip()

        try:
            proposal = self._memory_authorization.create_proposal(
                client_id=normalized_client_id,
                strategy=normalized_strategy,
            )
        except (MemoryAuthorizationError, ValueError):
            return self._invalid_memory_authorization_response()

        return {
            "agent": "memory",
            "status": "approval_required",
            "strategy": proposal["strategy"],
            "memory_token": proposal["memory_token"],
            "expires_at": proposal["expires_at"],
            "message": (
                "Would you like me to remember this strategy for "
                "future conversations?"
            ),
        }

    def _approve_memory_strategy(
        self,
        *,
        client_id: str | None,
        memory_token: str | None,
    ):
        if not client_id or not client_id.strip():
            return self._invalid_memory_authorization_response()

        if not memory_token:
            return self._invalid_memory_authorization_response()

        normalized_client_id = client_id.strip()

        try:
            payload = self._memory_authorization.validate_token(
                memory_token
            )
        except MemoryAuthorizationError:
            return self._invalid_memory_authorization_response()

        signed_client_id = payload.get("client_id")
        strategy = payload.get("strategy")

        if signed_client_id != normalized_client_id:
            return self._invalid_memory_authorization_response()

        if not isinstance(strategy, str) or not strategy.strip():
            return self._invalid_memory_authorization_response()

        memory = self._memory_manager.remember_approved_strategy(
            client_id=normalized_client_id,
            strategy=strategy,
        )

        return {
            "agent": "memory",
            "status": "remembered",
            "strategy": memory.strategy,
        }

    @staticmethod
    def _invalid_memory_authorization_response():
        return {
            "agent": "memory",
            "status": "invalid_authorization",
            "message": (
                "Memory authorization is invalid or unavailable. "
                "Nothing was remembered."
            ),
        }

    async def _answer_clarification(
        self,
        *,
        message: str,
        clarification_token: str,
    ):
        try:
            payload = self._clarification_gate.validate_token(
                clarification_token
            )
        except ClarificationTokenError:
            return self._clarification_gate.invalid_context_response()

        if self._is_execution_command(message):
            return self._clarification_gate.invalid_context_response(
                "Clarification answer cannot be an execution command. "
                "Please answer the clarification question or omit the token "
                "to start over."
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