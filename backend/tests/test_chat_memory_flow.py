import os
import unittest
from unittest.mock import patch

from app.services.chat_service import ChatService
from app.services.memory_authorization_service import (
    MEMORY_AUTHORIZATION_SECRET_ENV,
    MemoryAuthorizationService,
)
from app.services.memory_service import (
    InMemoryMemoryStore,
    MemoryService,
)


TEST_SECRET = "test-chat-memory-secret"


class FailingRouter:
    def route(self, message: str) -> str:
        raise AssertionError(
            "routing should not run for explicit memory actions"
        )


class StaticRouter:
    def __init__(self, route_name: str):
        self.route_name = route_name
        self.calls: list[str] = []

    def route(self, message: str) -> str:
        self.calls.append(message)
        return self.route_name


class RecordingAgent:
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.calls: list[str] = []

    async def run(self, message: str):
        self.calls.append(message)
        return {
            "agent": self.agent_name,
            "message": message,
        }


class RecordingRegistry:
    def __init__(self):
        self.planner = RecordingAgent("planner")
        self.execution = RecordingAgent("execution")
        self.conversation = RecordingAgent("conversation")
        self._agents = {
            "planner": self.planner,
            "execution": self.execution,
            "conversation": self.conversation,
        }

    def get(self, name: str):
        return self._agents[name]


class ChatMemoryFlowTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.store = InMemoryMemoryStore()
        self.memory_service = MemoryService(self.store)
        self.authorization_service = MemoryAuthorizationService(
            now_provider=lambda: 1000.0,
            ttl_seconds=300,
        )

    def create_service(
        self,
        *,
        registry=None,
        router=None,
    ) -> ChatService:
        return ChatService(
            agent_registry=registry or RecordingRegistry(),
            agent_router=router or FailingRouter(),
            memory_manager=self.memory_service,
            memory_authorization=self.authorization_service,
        )

    async def test_proposal_returns_exact_strategy_signed_token_and_expiration(
        self,
    ):
        with patch.dict(
            os.environ,
            {MEMORY_AUTHORIZATION_SECRET_ENV: TEST_SECRET},
            clear=False,
        ):
            service = self.create_service()

            response = await service.chat(
                "  Show me the whole system before the details.  ",
                client_id="client-a",
                memory_action="propose",
            )

            self.assertEqual(response["agent"], "memory")
            self.assertEqual(response["status"], "approval_required")
            self.assertEqual(
                response["strategy"],
                "Show me the whole system before the details.",
            )
            self.assertIsInstance(response["memory_token"], str)
            self.assertTrue(response["memory_token"])
            self.assertEqual(
                response["expires_at"],
                "1970-01-01T00:21:40Z",
            )

            payload = self.authorization_service.validate_token(
                response["memory_token"]
            )

        self.assertEqual(payload["client_id"], "client-a")
        self.assertEqual(
            payload["strategy"],
            "Show me the whole system before the details.",
        )

    async def test_proposal_does_not_persist_strategy(self):
        with patch.dict(
            os.environ,
            {MEMORY_AUTHORIZATION_SECRET_ENV: TEST_SECRET},
            clear=False,
        ):
            service = self.create_service()

            response = await service.chat(
                "Show me the big picture first.",
                client_id="client-a",
                memory_action="propose",
            )

        self.assertEqual(response["status"], "approval_required")
        self.assertEqual(
            self.memory_service.get_approved_strategies(
                client_id="client-a"
            ),
            [],
        )

    async def test_proposal_without_client_id_fails_closed(self):
        with patch.dict(
            os.environ,
            {MEMORY_AUTHORIZATION_SECRET_ENV: TEST_SECRET},
            clear=False,
        ):
            service = self.create_service()

            response = await service.chat(
                "Show me the big picture first.",
                memory_action="propose",
            )

        self.assertEqual(response["agent"], "memory")
        self.assertEqual(response["status"], "invalid_authorization")
        self.assertNotIn("memory_token", response)

    async def test_proposal_with_empty_strategy_fails_closed(self):
        with patch.dict(
            os.environ,
            {MEMORY_AUTHORIZATION_SECRET_ENV: TEST_SECRET},
            clear=False,
        ):
            service = self.create_service()

            response = await service.chat(
                "   ",
                client_id="client-a",
                memory_action="propose",
            )

        self.assertEqual(response["agent"], "memory")
        self.assertEqual(response["status"], "invalid_authorization")
        self.assertNotIn("memory_token", response)
        self.assertEqual(
            self.memory_service.get_approved_strategies(
                client_id="client-a"
            ),
            [],
        )

    async def test_proposal_missing_signing_secret_fails_closed(self):
        with patch.dict(
            os.environ,
            {},
            clear=False,
        ):
            previous_secret = os.environ.pop(
                MEMORY_AUTHORIZATION_SECRET_ENV,
                None,
            )
            try:
                service = self.create_service()

                response = await service.chat(
                    "Show me the big picture first.",
                    client_id="client-a",
                    memory_action="propose",
                )
            finally:
                if previous_secret is not None:
                    os.environ[
                        MEMORY_AUTHORIZATION_SECRET_ENV
                    ] = previous_secret

        self.assertEqual(response["agent"], "memory")
        self.assertEqual(response["status"], "invalid_authorization")
        self.assertNotIn("memory_token", response)
        self.assertEqual(
            self.memory_service.get_approved_strategies(
                client_id="client-a"
            ),
            [],
        )

    async def test_memory_proposal_bypasses_normal_routing(self):
        registry = RecordingRegistry()

        with patch.dict(
            os.environ,
            {MEMORY_AUTHORIZATION_SECRET_ENV: TEST_SECRET},
            clear=False,
        ):
            service = self.create_service(
                registry=registry,
                router=FailingRouter(),
            )

            response = await service.chat(
                "Show me the big picture first.",
                client_id="client-a",
                memory_action="propose",
            )

        self.assertEqual(response["status"], "approval_required")
        self.assertEqual(registry.planner.calls, [])
        self.assertEqual(registry.execution.calls, [])
        self.assertEqual(registry.conversation.calls, [])

    async def test_explicit_approval_persists_exact_signed_strategy(self):
        with patch.dict(
            os.environ,
            {MEMORY_AUTHORIZATION_SECRET_ENV: TEST_SECRET},
            clear=False,
        ):
            proposal = self.authorization_service.create_proposal(
                client_id="client-a",
                strategy="Show me the whole system before the details.",
            )

            service = self.create_service()

            response = await service.chat(
                "Remember this strategy",
                client_id="client-a",
                memory_action="approve",
                memory_token=proposal["memory_token"],
            )

        memories = self.memory_service.get_approved_strategies(
            client_id="client-a"
        )

        self.assertEqual(len(memories), 1)
        self.assertEqual(
            memories[0].strategy,
            "Show me the whole system before the details.",
        )
        self.assertEqual(response["agent"], "memory")
        self.assertEqual(response["status"], "remembered")
        self.assertEqual(
            response["strategy"],
            "Show me the whole system before the details.",
        )

    async def test_approval_uses_signed_strategy_not_request_message(self):
        with patch.dict(
            os.environ,
            {MEMORY_AUTHORIZATION_SECRET_ENV: TEST_SECRET},
            clear=False,
        ):
            proposal = self.authorization_service.create_proposal(
                client_id="client-a",
                strategy="Show me the big picture first.",
            )

            service = self.create_service()

            await service.chat(
                "Remember a completely different strategy instead.",
                client_id="client-a",
                memory_action="approve",
                memory_token=proposal["memory_token"],
            )

        memories = self.memory_service.get_approved_strategies(
            client_id="client-a"
        )

        self.assertEqual(len(memories), 1)
        self.assertEqual(
            memories[0].strategy,
            "Show me the big picture first.",
        )

    async def test_approval_rejects_client_mismatch(self):
        with patch.dict(
            os.environ,
            {MEMORY_AUTHORIZATION_SECRET_ENV: TEST_SECRET},
            clear=False,
        ):
            proposal = self.authorization_service.create_proposal(
                client_id="client-a",
                strategy="Show me the big picture first.",
            )

            service = self.create_service()

            response = await service.chat(
                "Remember this strategy",
                client_id="client-b",
                memory_action="approve",
                memory_token=proposal["memory_token"],
            )

        self.assertEqual(response["agent"], "memory")
        self.assertEqual(response["status"], "invalid_authorization")
        self.assertEqual(
            self.memory_service.get_approved_strategies(
                client_id="client-a"
            ),
            [],
        )
        self.assertEqual(
            self.memory_service.get_approved_strategies(
                client_id="client-b"
            ),
            [],
        )

    async def test_tampered_memory_token_fails_closed(self):
        with patch.dict(
            os.environ,
            {MEMORY_AUTHORIZATION_SECRET_ENV: TEST_SECRET},
            clear=False,
        ):
            proposal = self.authorization_service.create_proposal(
                client_id="client-a",
                strategy="Show me the big picture first.",
            )

            payload_part, signature_part = (
                proposal["memory_token"].split(".", 1)
            )

            replacement = (
                "A" if payload_part[0] != "A" else "B"
            )
            tampered_payload = (
                replacement + payload_part[1:]
            )
            tampered_token = (
                f"{tampered_payload}.{signature_part}"
            )

            service = self.create_service()

            response = await service.chat(
                "Remember this strategy",
                client_id="client-a",
                memory_action="approve",
                memory_token=tampered_token,
            )

        self.assertEqual(response["agent"], "memory")
        self.assertEqual(response["status"], "invalid_authorization")
        self.assertEqual(
            self.memory_service.get_approved_strategies(
                client_id="client-a"
            ),
            [],
        )

    async def test_approval_without_memory_token_fails_closed(self):
        service = self.create_service()

        response = await service.chat(
            "Remember this strategy",
            client_id="client-a",
            memory_action="approve",
        )

        self.assertEqual(response["agent"], "memory")
        self.assertEqual(response["status"], "invalid_authorization")
        self.assertEqual(
            self.memory_service.get_approved_strategies(
                client_id="client-a"
            ),
            [],
        )

    async def test_approval_without_client_id_fails_closed(self):
        with patch.dict(
            os.environ,
            {MEMORY_AUTHORIZATION_SECRET_ENV: TEST_SECRET},
            clear=False,
        ):
            proposal = self.authorization_service.create_proposal(
                client_id="client-a",
                strategy="Show me the big picture first.",
            )

            service = self.create_service()

            response = await service.chat(
                "Remember this strategy",
                memory_action="approve",
                memory_token=proposal["memory_token"],
            )

        self.assertEqual(response["agent"], "memory")
        self.assertEqual(response["status"], "invalid_authorization")
        self.assertEqual(
            self.memory_service.get_approved_strategies(
                client_id="client-a"
            ),
            [],
        )

    async def test_unknown_memory_action_fails_closed(self):
        service = self.create_service()

        response = await service.chat(
            "Do something with memory",
            client_id="client-a",
            memory_action="delete",
            memory_token="unused",
        )

        self.assertEqual(response["agent"], "memory")
        self.assertEqual(response["status"], "invalid_authorization")
        self.assertEqual(
            self.memory_service.get_approved_strategies(
                client_id="client-a"
            ),
            [],
        )

    async def test_ordinary_chat_does_not_create_memory(self):
        registry = RecordingRegistry()
        router = StaticRouter("conversation")

        service = self.create_service(
            registry=registry,
            router=router,
        )

        message = (
            "I understand things better when I see the whole system "
            "before the individual pieces."
        )

        response = await service.chat(
            message,
            client_id="client-a",
        )

        self.assertEqual(response["agent"], "conversation")
        self.assertEqual(registry.conversation.calls, [message])
        self.assertEqual(
            self.memory_service.get_approved_strategies(
                client_id="client-a"
            ),
            [],
        )

    async def test_plain_yes_does_not_create_memory(self):
        registry = RecordingRegistry()
        router = StaticRouter("conversation")

        service = self.create_service(
            registry=registry,
            router=router,
        )

        response = await service.chat(
            "yes",
            client_id="client-a",
        )

        self.assertEqual(response["agent"], "conversation")
        self.assertEqual(registry.conversation.calls, ["yes"])
        self.assertEqual(
            self.memory_service.get_approved_strategies(
                client_id="client-a"
            ),
            [],
        )

    async def test_memory_approval_bypasses_normal_routing(self):
        registry = RecordingRegistry()

        with patch.dict(
            os.environ,
            {MEMORY_AUTHORIZATION_SECRET_ENV: TEST_SECRET},
            clear=False,
        ):
            proposal = self.authorization_service.create_proposal(
                client_id="client-a",
                strategy="Show me the big picture first.",
            )

            service = self.create_service(
                registry=registry,
                router=FailingRouter(),
            )

            response = await service.chat(
                "Remember this strategy",
                client_id="client-a",
                memory_action="approve",
                memory_token=proposal["memory_token"],
            )

        self.assertEqual(response["status"], "remembered")
        self.assertEqual(registry.planner.calls, [])
        self.assertEqual(registry.execution.calls, [])
        self.assertEqual(registry.conversation.calls, [])


if __name__ == "__main__":
    unittest.main()