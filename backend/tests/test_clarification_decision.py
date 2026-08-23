import json
import os
import unittest
from unittest.mock import patch

from app.services.chat_service import ChatService
from app.services.clarification_service import (
    CLARIFICATION_TOKEN_SECRET_ENV,
    DECISION_CLARIFY,
    DECISION_CLEAR,
    DECISION_DISCOVER_IN_PLAN,
    ClarificationService,
)
from app.services.gemini_service import GeminiService
from app.services.project_service import project_service


TEST_SECRET = "test-clarification-secret"


def human_gate_pass():
    return {
        "has_user_value_conflict": False,
        "conflicting_priorities": [],
        "can_external_evidence_resolve_it": True,
        "why_human_judgment_is_required": "",
        "question": "",
    }


def human_value_conflict(
    priorities: tuple[str, str] = ("speed", "quality"),
    *,
    question: str = "Which priority should the plan optimize for first?",
    decision: str = DECISION_CLARIFY,
):
    return {
        "has_user_value_conflict": True,
        "conflicting_priorities": list(priorities),
        "can_external_evidence_resolve_it": False,
        "why_human_judgment_is_required": (
            "The preferred trade-off belongs to the user."
        ),
        "question": question,
        "decision": decision,
    }


def classifier_decision(decision: str):
    return {
        "decision": decision,
        "missing_user_judgment": "",
        "why_planning_now_would_choose_for_user": "",
        "question": "",
    }


class RecordingModelService:
    def __init__(
        self,
        human_decision_reply: dict | str,
        classifier_reply: dict | str | None = None,
    ):
        self.human_decision_reply = human_decision_reply
        self.classifier_reply = classifier_reply or human_decision_reply
        self.calls: list[tuple[str, object]] = []

    def generate(self, message: str, config=None):
        self.calls.append((message, config))
        reply = (
            self.human_decision_reply
            if "human-decision boundary" in message
            else self.classifier_reply
        )
        if isinstance(reply, str):
            return {"reply": reply}
        return {"reply": json.dumps(reply)}


class StaticRouter:
    def route(self, message: str) -> str:
        return "planner"


class RecordingAgent:
    def __init__(self):
        self.calls: list[str] = []

    async def run(self, message: str):
        self.calls.append(message)
        return {"agent": "planner", "message": message}


class RecordingRegistry:
    def __init__(self):
        self.planner = RecordingAgent()

    def get(self, name: str):
        if name != "planner":
            raise AssertionError(f"Unexpected agent: {name}")
        return self.planner


class ClarificationDecisionTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        project_service._projects.clear()

    def test_consequential_competing_user_directions_clarify(self):
        service = ClarificationService(
            model_service=RecordingModelService(
                human_value_conflict(("maximizing income", "minimizing stress"))
            )
        )

        decision = service.evaluate(
            "I want to plan a career change, but I can't decide whether my "
            "priority should be maximizing income or minimizing stress, and "
            "those would lead me in different directions."
        )

        self.assertEqual(decision.decision, DECISION_CLARIFY)
        self.assertTrue(decision.needs_clarification)
        self.assertEqual(decision.question.count("?"), 1)
        self.assertIn("maximizing income", decision.missing_user_judgment)

    def test_uncertain_but_explicit_objective_plans(self):
        service = ClarificationService(
            model_service=RecordingModelService(human_gate_pass())
        )

        decision = service.evaluate(
            "I'm not sure this idea will work, but plan three reasoning steps "
            "to test the value proposition before I spend money."
        )

        self.assertEqual(decision.decision, DECISION_DISCOVER_IN_PLAN)
        self.assertFalse(decision.needs_clarification)
        self.assertEqual(decision.question, "")

    def test_clear_planning_request_plans(self):
        service = ClarificationService(
            model_service=RecordingModelService(human_gate_pass())
        )

        decision = service.evaluate(
            "Plan a reasoning-only project to identify the riskiest assumption "
            "in my proposed service and choose one safe validation step."
        )

        self.assertEqual(decision.decision, DECISION_CLEAR)
        self.assertFalse(decision.needs_clarification)

    def test_missing_knowledge_that_belongs_in_plan_plans(self):
        service = ClarificationService(
            model_service=RecordingModelService(human_gate_pass())
        )

        decision = service.evaluate(
            "I don't know which customer segment has the biggest problem. "
            "Plan how I can compare the likely segments before choosing one."
        )

        self.assertEqual(decision.decision, DECISION_DISCOVER_IN_PLAN)
        self.assertFalse(decision.needs_clarification)

    def test_paired_authority_contrasts(self):
        clarify_cases = [
            (
                "business",
                (
                    "I want to validate my service, but I'm torn between "
                    "getting revenue as quickly as possible and understanding "
                    "the customer problem deeply before testing a solution. "
                    "Help me plan what to do."
                ),
                ("getting revenue quickly", "understanding the problem deeply"),
            ),
            (
                "career",
                (
                    "Help me plan a career change. I could optimize for "
                    "earning as much as possible or reducing stress and "
                    "having predictable hours, but I haven't decided which "
                    "matters more."
                ),
                ("earning as much as possible", "reducing stress"),
            ),
            (
                "product",
                (
                    "I can optimize this product for simplicity or advanced "
                    "customization, and both are viable, but I haven't "
                    "decided which experience I want customers to have."
                ),
                ("simplicity", "advanced customization"),
            ),
            (
                "time_quality",
                (
                    "I need a plan, but I haven't decided whether finishing "
                    "as fast as possible or maximizing quality matters more "
                    "to me."
                ),
                ("finishing fast", "maximizing quality"),
            ),
        ]
        for name, message, priorities in clarify_cases:
            with self.subTest(name=name):
                service = ClarificationService(
                    model_service=RecordingModelService(
                        human_value_conflict(priorities)
                    )
                )

                decision = service.evaluate(message)

                self.assertEqual(decision.decision, DECISION_CLARIFY)
                self.assertTrue(decision.needs_clarification)
                self.assertEqual(decision.question.count("?"), 1)

        discovery_cases = [
            (
                "business",
                (
                    "I don't know which customer segment has the biggest "
                    "problem. Plan how I can compare the likely segments "
                    "before choosing one."
                ),
            ),
            (
                "career",
                (
                    "I don't know which career field currently has better "
                    "opportunities for me. Plan how I can compare several "
                    "fields before choosing one."
                ),
            ),
            (
                "product",
                (
                    "I don't know whether customers actually prefer "
                    "simplicity or customization. Plan a low-cost way to test "
                    "which they prefer."
                ),
            ),
            (
                "time_quality",
                (
                    "I need to understand how much additional time higher "
                    "quality would actually require. Plan how to estimate "
                    "that before I choose."
                ),
            ),
        ]
        for name, message in discovery_cases:
            with self.subTest(name=name):
                service = ClarificationService(
                    model_service=RecordingModelService(human_gate_pass())
                )

                decision = service.evaluate(message)

                self.assertEqual(decision.decision, DECISION_DISCOVER_IN_PLAN)
                self.assertFalse(decision.needs_clarification)

    def test_human_decision_evidence_overrides_contradictory_clear_label(self):
        service = ClarificationService(
            model_service=RecordingModelService(
                human_value_conflict(
                    ("speed", "quality"),
                    question=(
                        "Which matters more to you right now: speed or "
                        "quality?"
                    ),
                    decision=DECISION_CLEAR,
                )
            )
        )

        decision = service.evaluate(
            "I need a plan, but I haven't decided whether speed or quality "
            "matters more."
        )

        self.assertEqual(decision.decision, DECISION_CLARIFY)
        self.assertEqual(
            decision.question,
            "Which matters more to you right now: speed or quality?",
        )

    def test_missing_consequential_user_preference_clarifies(self):
        service = ClarificationService(
            model_service=RecordingModelService(
                human_value_conflict(("keeping the budget low", "finishing fast"))
            )
        )

        decision = service.evaluate(
            "Plan a home renovation, but I can't decide whether my priority "
            "should be keeping the budget low or finishing as fast as possible."
        )

        self.assertEqual(decision.decision, DECISION_CLARIFY)
        self.assertTrue(decision.needs_clarification)

    def test_broad_but_decomposable_goal_plans(self):
        service = ClarificationService(
            model_service=RecordingModelService(human_gate_pass())
        )

        decision = service.evaluate(
            "Plan a project to improve how my team handles customer feedback."
        )

        self.assertEqual(decision.decision, DECISION_CLEAR)
        self.assertFalse(decision.needs_clarification)

    def test_same_model_input_repeated_uses_stable_config(self):
        model = RecordingModelService(
            human_gate_pass(),
            classifier_decision(DECISION_CLEAR),
        )
        service = ClarificationService(model_service=model)
        message = "I want to build something useful for my neighborhood."

        decisions = [service.evaluate(message).decision for _ in range(3)]

        self.assertEqual(decisions, [DECISION_CLEAR] * 3)
        self.assertEqual(len(model.calls), 6)
        for prompt, config in model.calls:
            self.assertTrue(
                "human-decision boundary" in prompt
                or "sufficiency and discovery classifier" in prompt
            )
            self.assertEqual(config.temperature, 0)
            self.assertEqual(config.seed, 1)
            self.assertEqual(config.response_mime_type, "application/json")

    def test_clarify_model_result_normalizes_to_one_question(self):
        model = RecordingModelService(
            human_value_conflict(
                question=(
                    "Which priority matters most for this plan? Should we "
                    "optimize for speed instead?"
                )
            )
        )
        service = ClarificationService(model_service=model)

        decision = service.evaluate(
            "I want to create a program for my department."
        )

        self.assertEqual(decision.decision, DECISION_CLARIFY)
        self.assertEqual(decision.question.count("?"), 1)
        self.assertEqual(
            decision.question,
            "Which priority matters most for this plan?",
        )

    def test_model_failure_fallback_prefers_planning_when_not_confident(self):
        service = ClarificationService(
            model_service=RecordingModelService("not json")
        )

        decision = service.evaluate(
            "I want to build something useful for my neighborhood."
        )

        self.assertEqual(decision.decision, DECISION_CLEAR)
        self.assertFalse(decision.needs_clarification)

    async def test_clarify_creates_no_project_before_answer_then_plans(self):
        registry = RecordingRegistry()
        service = ChatService(
            agent_registry=registry,
            agent_router=StaticRouter(),
            clarification_gate=ClarificationService(
                model_service=RecordingModelService(
                    human_value_conflict(
                        ("maximizing income", "minimizing stress")
                    )
                )
            ),
        )

        with patch.dict(
            os.environ,
            {CLARIFICATION_TOKEN_SECRET_ENV: TEST_SECRET},
            clear=False,
        ):
            response = await service.chat(
                "I want to plan a career change, but I can't decide whether "
                "my priority should be maximizing income or minimizing stress."
            )

            self.assertEqual(response["agent"], "clarification")
            self.assertEqual(response["status"], "needs_clarification")
            self.assertEqual(response["question"].count("?"), 1)
            self.assertEqual(registry.planner.calls, [])
            self.assertEqual(project_service.list_projects(), [])

            answered = await service.chat(
                "Reducing stress matters more.",
                clarification_token=response["clarification_token"],
            )

        self.assertEqual(answered["agent"], "planner")
        self.assertEqual(len(registry.planner.calls), 1)
        self.assertIn("Reducing stress matters more.", registry.planner.calls[0])


class GeminiServiceConfigTests(unittest.TestCase):
    def test_generate_accepts_optional_per_call_config(self):
        config = object()

        with patch(
            "app.services.gemini_service.client.models.generate_content"
        ) as generate_content:
            generate_content.return_value.text = "ok"

            result = GeminiService().generate("hello", config=config)

        self.assertEqual(result, {"reply": "ok"})
        generate_content.assert_called_once_with(
            model="gemini-3.5-flash-lite",
            contents="hello",
            config=config,
        )


if __name__ == "__main__":
    unittest.main()
