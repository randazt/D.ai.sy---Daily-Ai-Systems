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

    Explicit memory actions are handled before normal routing.

    A memory proposal does not persist memory. Persistence happens
    only after explicit human approval of the signed proposal.

    Approved strategies may later be offered to the same client.
    Applying a strategy requires an explicit memory_id and current
    user request. The stored, approved strategy is retrieved
    server-side before use.

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
        memory_id: str | None = None,
    ):
        if memory_action is not None:
            return await self._handle_memory_action(
                message=message,
                client_id=client_id,
                memory_action=memory_action,
                memory_token=memory_token,
                memory_id=memory_id,
            )

        if clarification_token:
            return await self._answer_clarification(
                message=message,
                clarification_token=clarification_token,
            )

        return await self._route_and_run(message)

    async def _route_and_run(self, message: str):
        cognition_first = self._clarification_gate._cognitive_bottleneck_decision(
            message
        )
        if cognition_first is not None and cognition_first.needs_clarification:
            try:
                return self._clarification_gate.create_clarification_response(
                    original_goal=message,
                    question=cognition_first.question,
                )
            except ClarificationTokenError:
                return self._clarification_gate.invalid_context_response(
                    "Clarification is unavailable. "
                    "Please restate your goal clearly."
                )

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

        agent = self._registry.get(agent_name)
        result = await agent.run(message)

        return result

    async def _handle_memory_action(
        self,
        *,
        message: str,
        client_id: str | None,
        memory_action: str,
        memory_token: str | None,
        memory_id: str | None,
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

        if memory_action == "offer":
            return self._offer_memory_strategy(
                client_id=client_id,
                original_message=message,
            )

        if memory_action == "apply":
            return await self._apply_memory_strategy(
                client_id=client_id,
                memory_id=memory_id,
                message=message,
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

    def _offer_memory_strategy(
        self,
        *,
        client_id: str | None,
        original_message: str,
    ):
        if not client_id or not client_id.strip():
            return self._invalid_memory_authorization_response()

        normalized_client_id = client_id.strip()

        try:
            memories = self._memory_manager.get_approved_strategies(
                client_id=normalized_client_id,
            )
        except ValueError:
            return self._invalid_memory_authorization_response()

        if not memories:
            return {
                "agent": "memory",
                "status": "no_strategy",
                "original_message": original_message,
                "message": (
                    "No approved strategy is available for this client."
                ),
            }

        memory = memories[-1]

        return {
            "agent": "memory",
            "status": "strategy_available",
            "memory_id": memory.id,
            "strategy": memory.strategy,
            "original_message": original_message,
            "message": (
                "You previously taught D.AI.SY this strategy. "
                "Would you like me to use it for this request?"
            ),
        }

    async def _apply_memory_strategy(
        self,
        *,
        client_id: str | None,
        memory_id: str | None,
        message: str,
    ):
        if not client_id or not client_id.strip():
            return self._invalid_memory_authorization_response()

        if not memory_id or not memory_id.strip():
            return self._invalid_memory_authorization_response()

        if not message or not message.strip():
            return self._invalid_memory_authorization_response()

        normalized_client_id = client_id.strip()
        normalized_memory_id = memory_id.strip()

        try:
            memories = self._memory_manager.get_approved_strategies(
                client_id=normalized_client_id,
            )
        except ValueError:
            return self._invalid_memory_authorization_response()

        selected_memory = next(
            (
                memory
                for memory in memories
                if memory.id == normalized_memory_id
            ),
            None,
        )

        if selected_memory is None:
            return self._invalid_memory_authorization_response()

        agent_name = self._router.route(message)
        agent = self._registry.get(agent_name)

        adapted_message = self._build_adapted_message(
            original_message=message,
            strategy=selected_memory.strategy,
        )

        return await agent.run(adapted_message)

    @staticmethod
    def _build_adapted_message(
        *,
        original_message: str,
        strategy: str,
    ) -> str:
        return (
            f"User's current request:\n{original_message.strip()}\n\n"
            f"User-approved strategy:\n{strategy.strip()}\n\n"
            "Adapt your response using the user's approved strategy. "
            "Make the adaptation observable while keeping the initial "
            "response concise and low in cognitive load.\n\n"
            "Use progressive disclosure:\n"
            "1. Start with a short big-picture orientation to the whole "
            "system, usually two to four sentences.\n"
            "2. Identify only the main components needed for orientation, "
            "preferably three to five.\n"
            "3. Show the key relationship or flow between those components "
            "concisely when relevant.\n"
            "4. Stop before expanding the components, sequence, examples, "
            "frameworks, or supporting details.\n"
            "5. Invite the user to choose where to go deeper next.\n\n"
            "Do not provide every layer of explanation in the first "
            "response. Do not turn 'whole system first' into 'all details "
            "at once.' The goal is orientation first, then user-directed "
            "depth.\n\n"
            "Use only the strategy the user explicitly approved. Do not "
            "label, diagnose, or infer a learning style, disability, "
            "personality type, or other trait from that strategy.\n\n"
            "Preserve human authority. The strategy guides how the "
            "information is presented; it does not authorize D.AI.SY "
            "to make consequential decisions for the user."
        )

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