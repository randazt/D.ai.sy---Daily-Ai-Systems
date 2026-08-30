import os
import unittest
from unittest.mock import patch

from app.schemas.chat import ChatRequest
from app.services.chat_service import ChatService
from app.services.clarification_service import (
    CLARIFICATION_TOKEN_SECRET_ENV,
    ClarificationDecision,
    ClarificationService,
)
from app.services.project_service import project_service


TEST_SECRET = "test-clarification-secret"


class StaticRouter:
    def __init__(self, route_name: str):
        self.route_name = route_name
        self.calls: list[str] = []

    def route(self, message: str) -> str:
        self.calls.append(message)
        return self.route_name


class FailingRouter:
    def route(self, message: str) -> str:
        raise AssertionError("routing should not run for token-bearing requests")


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


def clarification_gate(decision: ClarificationDecision | None = None, **kwargs):
    gate = ClarificationService(**kwargs)
    if decision is not None:
        gate.evaluate = lambda message: decision
    return gate


class ClarificationFlowTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        project_service._projects.clear()

    async def test_cognition_first_request_clarifies_before_conversation_routing(self):
        registry = RecordingRegistry()
        router = StaticRouter("conversation")
        gate = clarification_gate()

        service = ChatService(
            agent_registry=registry,
            agent_router=router,
            clarification_gate=gate,
        )

        message = (
            "I keep putting off organizing my week because everything feels "
            "equally important and I don't know where to start. Help me turn "
            "this into a simple system I can actually use."
        )

        with patch.dict(
            os.environ,
            {CLARIFICATION_TOKEN_SECRET_ENV: TEST_SECRET},
            clear=False,
        ):
            response = await service.chat(message)

        self.assertEqual(response["agent"], "clarification")
        self.assertEqual(response["status"], "needs_clarification")
        self.assertEqual(
            response["question"],
            (
                "When you look at everything you need to do, where do you "
                "get stuck first: deciding what matters most, choosing "
                "between things that all feel important, or holding too "
                "many things in your head at once?"
            ),
        )
        self.assertEqual(registry.conversation.calls, [])
        self.assertEqual(registry.planner.calls, [])
        self.assertEqual(registry.execution.calls, [])

    async def test_ambiguous_request_returns_one_clarification_question(self):
        registry = RecordingRegistry()
        service = ChatService(
            agent_registry=registry,
            agent_router=StaticRouter("planner"),
            clarification_gate=clarification_gate(
                ClarificationDecision(
                    needs_clarification=True,
                    question=(
                        "Before we build the plan, what matters most right now?"
                    ),
                )
            ),
        )

        with patch.dict(
            os.environ,
            {CLARIFICATION_TOKEN_SECRET_ENV: TEST_SECRET},
            clear=False,
        ):
            response = await service.chat(
                "Plan an AI service, but I am not sure who needs it or what to do first."
            )

        self.assertEqual(response["agent"], "clarification")
        self.assertEqual(response["status"], "needs_clarification")
        self.assertEqual(response["question"].count("?"), 1)
        self.assertTrue(response["clarification_token"])
        self.assertTrue(response["expires_at"])
        self.assertEqual(registry.planner.calls, [])

    async def test_ambiguous_request_creates_no_project(self):
        registry = RecordingRegistry()
        service = ChatService(
            agent_registry=registry,
            agent_router=StaticRouter("planner"),
            clarification_gate=clarification_gate(
                ClarificationDecision(
                    needs_clarification=True,
                    question="Which uncertainty should we resolve first?",
                )
            ),
        )

        with patch.dict(
            os.environ,
            {CLARIFICATION_TOKEN_SECRET_ENV: TEST_SECRET},
            clear=False,
        ):
            await service.chat(
                "Plan a project, but I do not know whether to build or interview users."
            )

        self.assertEqual(project_service.list_projects(), [])
        self.assertEqual(registry.planner.calls, [])

    async def test_clear_planning_request_still_plans_immediately(self):
        registry = RecordingRegistry()
        message = "Plan a project to research three named customer segments."
        service = ChatService(
            agent_registry=registry,
            agent_router=StaticRouter("planner"),
            clarification_gate=clarification_gate(
                ClarificationDecision(needs_clarification=False)
            ),
        )

        response = await service.chat(message)

        self.assertEqual(response["agent"], "planner")
        self.assertEqual(registry.planner.calls, [message])

    async def test_valid_token_answer_reaches_planner_with_original_goal_and_answer(self):
        registry = RecordingRegistry()
        original_goal = "Plan a project for an uncertain service idea."
        answer = "Choosing the first customer matters most."
        gate = clarification_gate()

        with patch.dict(
            os.environ,
            {CLARIFICATION_TOKEN_SECRET_ENV: TEST_SECRET},
            clear=False,
        ):
            token, _ = gate.issue_token(
                original_goal=original_goal,
                question="What matters most?",
            )
            service = ChatService(
                agent_registry=registry,
                agent_router=FailingRouter(),
                clarification_gate=gate,
            )
            response = await service.chat(answer, clarification_token=token)

        self.assertEqual(response["agent"], "planner")
        self.assertEqual(len(registry.planner.calls), 1)
        clarified_goal = registry.planner.calls[0]
        self.assertIn(original_goal, clarified_goal)
        self.assertIn(answer, clarified_goal)

    async def test_answer_without_planning_keywords_still_reaches_planner(self):
        registry = RecordingRegistry()
        gate = clarification_gate()

        with patch.dict(
            os.environ,
            {CLARIFICATION_TOKEN_SECRET_ENV: TEST_SECRET},
            clear=False,
        ):
            token, _ = gate.issue_token(
                original_goal="Plan an ambiguous product validation project.",
                question="What matters most?",
            )
            service = ChatService(
                agent_registry=registry,
                agent_router=FailingRouter(),
                clarification_gate=gate,
            )
            await service.chat("Customers.", clarification_token=token)

        self.assertEqual(len(registry.planner.calls), 1)
        self.assertIn("Customers.", registry.planner.calls[0])

    async def test_malformed_token_fails_closed(self):
        registry = RecordingRegistry()
        service = ChatService(
            agent_registry=registry,
            agent_router=FailingRouter(),
            clarification_gate=clarification_gate(),
        )

        with patch.dict(
            os.environ,
            {CLARIFICATION_TOKEN_SECRET_ENV: TEST_SECRET},
            clear=False,
        ):
            response = await service.chat(
                "Use this answer",
                clarification_token="not-a-token",
            )

        self.assertEqual(response["agent"], "clarification")
        self.assertEqual(response["status"], "invalid_context")
        self.assertEqual(registry.planner.calls, [])
        self.assertEqual(registry.execution.calls, [])

    async def test_tampered_token_fails_closed(self):
        registry = RecordingRegistry()
        gate = clarification_gate()

        with patch.dict(
            os.environ,
            {CLARIFICATION_TOKEN_SECRET_ENV: TEST_SECRET},
            clear=False,
        ):
            token, _ = gate.issue_token(
                original_goal="Plan an ambiguous project.",
                question="What matters most?",
            )
            tampered_token = f"{token[:-1]}x"
            service = ChatService(
                agent_registry=registry,
                agent_router=FailingRouter(),
                clarification_gate=gate,
            )
            response = await service.chat(
                "Use this answer",
                clarification_token=tampered_token,
            )

        self.assertEqual(response["status"], "invalid_context")
        self.assertEqual(registry.planner.calls, [])
        self.assertEqual(registry.execution.calls, [])

    async def test_expired_token_fails_closed(self):
        registry = RecordingRegistry()

        with patch.dict(
            os.environ,
            {CLARIFICATION_TOKEN_SECRET_ENV: TEST_SECRET},
            clear=False,
        ):
            issuing_gate = clarification_gate(ttl_seconds=-1)
            token, _ = issuing_gate.issue_token(
                original_goal="Plan an ambiguous project.",
                question="What matters most?",
            )
            service = ChatService(
                agent_registry=registry,
                agent_router=FailingRouter(),
                clarification_gate=clarification_gate(),
            )
            response = await service.chat(
                "Use this answer",
                clarification_token=token,
            )

        self.assertEqual(response["status"], "invalid_context")
        self.assertEqual(registry.planner.calls, [])
        self.assertEqual(registry.execution.calls, [])

    async def test_execution_like_answer_with_valid_token_does_not_execute(self):
        registry = RecordingRegistry()
        gate = clarification_gate()

        with patch.dict(
            os.environ,
            {CLARIFICATION_TOKEN_SECRET_ENV: TEST_SECRET},
            clear=False,
        ):
            token, _ = gate.issue_token(
                original_goal="Plan an ambiguous product validation project.",
                question="What matters most?",
            )
            service = ChatService(
                agent_registry=registry,
                agent_router=FailingRouter(),
                clarification_gate=gate,
            )
            response = await service.chat("execute", clarification_token=token)

        self.assertEqual(response["agent"], "clarification")
        self.assertEqual(response["status"], "invalid_context")
        self.assertEqual(registry.execution.calls, [])
        self.assertEqual(registry.planner.calls, [])

    async def test_omitting_token_allows_new_independent_request(self):
        registry = RecordingRegistry()
        message = "Plan a clear new project."
        gate = clarification_gate(
            ClarificationDecision(needs_clarification=False)
        )
        service = ChatService(
            agent_registry=registry,
            agent_router=StaticRouter("planner"),
            clarification_gate=gate,
        )

        response = await service.chat(message)

        self.assertEqual(response["agent"], "planner")
        self.assertEqual(registry.planner.calls, [message])

    async def test_missing_secret_fails_closed_when_issuing_clarification_token(self):
        registry = RecordingRegistry()
        service = ChatService(
            agent_registry=registry,
            agent_router=StaticRouter("planner"),
            clarification_gate=clarification_gate(
                ClarificationDecision(
                    needs_clarification=True,
                    question="What matters most?",
                )
            ),
        )

        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop(CLARIFICATION_TOKEN_SECRET_ENV, None)
            response = await service.chat("Plan an ambiguous project.")

        self.assertEqual(response["agent"], "clarification")
        self.assertEqual(response["status"], "invalid_context")
        self.assertEqual(registry.planner.calls, [])
        self.assertEqual(project_service.list_projects(), [])

    async def test_missing_secret_fails_closed_when_validating_clarification_token(self):
        registry = RecordingRegistry()
        gate = clarification_gate()

        with patch.dict(
            os.environ,
            {CLARIFICATION_TOKEN_SECRET_ENV: TEST_SECRET},
            clear=False,
        ):
            token, _ = gate.issue_token(
                original_goal="Plan an ambiguous project.",
                question="What matters most?",
            )

        service = ChatService(
            agent_registry=registry,
            agent_router=FailingRouter(),
            clarification_gate=gate,
        )
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop(CLARIFICATION_TOKEN_SECRET_ENV, None)
            response = await service.chat(
                "Use this answer",
                clarification_token=token,
            )

        self.assertEqual(response["status"], "invalid_context")
        self.assertEqual(registry.planner.calls, [])

    def test_existing_message_only_request_remains_valid(self):
        request = ChatRequest(message="Plan a clear project.")

        self.assertEqual(request.message, "Plan a clear project.")
        self.assertIsNone(request.clarification_token)


if __name__ == "__main__":
    unittest.main()
