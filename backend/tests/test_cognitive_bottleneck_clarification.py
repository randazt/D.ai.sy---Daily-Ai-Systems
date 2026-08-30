import unittest

from app.services.clarification_service import (
    DECISION_CLARIFY,
    ClarificationService,
)


EXPECTED_COGNITIVE_BOTTLENECK_QUESTION = (
    "When you look at everything you need to do, where do you "
    "get stuck first: deciding what matters most, choosing "
    "between things that all feel important, or holding too "
    "many things in your head at once?"
)


class FabricatedProjectTradeoffModelService:
    """
    Simulates the failure observed in the live D.AI.SY flow.

    The human-decision model incorrectly interprets an everyday
    cognition-first request as a project-style priority conflict.
    """

    def __init__(self):
        self.calls: list[str] = []

    def generate(self, message: str, config=None):
        self.calls.append(message)

        if "human-decision boundary" in message:
            return {
                "reply": (
                    '{"has_user_value_conflict": true,'
                    '"conflicting_priorities": ['
                    '"rapid momentum",'
                    '"deeply resolving conceptual difficulties"'
                    '],'
                    '"can_external_evidence_resolve_it": false,'
                    '"why_human_judgment_is_required": '
                    '"The user must choose which priority matters more.",'
                    '"question": '
                    '"Are you looking to prioritize rapid momentum to ship '
                    'quickly, or do you prefer to pause and deeply resolve '
                    'the underlying conceptual difficulties first?",'
                    '"decision": "CLARIFY"}'
                )
            }

        return {
            "reply": (
                '{"decision": "CLEAR",'
                '"missing_user_judgment": "",'
                '"why_planning_now_would_choose_for_user": "",'
                '"question": ""}'
            )
        }


class CognitiveBottleneckClarificationTests(unittest.TestCase):
    def assert_cognition_first_clarification(self, decision):
        self.assertEqual(decision.decision, DECISION_CLARIFY)
        self.assertTrue(decision.needs_clarification)
        self.assertEqual(
            decision.question,
            EXPECTED_COGNITIVE_BOTTLENECK_QUESTION,
        )

        self.assertNotIn("ship", decision.question.lower())
        self.assertNotIn("rapid momentum", decision.question.lower())
        self.assertNotIn("conceptual difficulties", decision.question.lower())

        self.assertEqual(
            decision.missing_user_judgment,
            (
                "The user wants help understanding the cognitive bottleneck "
                "before D.AI.SY turns it into a system or plan."
            ),
        )
        self.assertIn(
            "understand the bottleneck",
            decision.why_planning_now_would_choose_for_user.lower(),
        )

    def test_cognition_first_request_clarifies_bottleneck_before_tradeoff_gate(
        self,
    ):
        model = FabricatedProjectTradeoffModelService()
        service = ClarificationService(model_service=model)

        decision = service.evaluate(
            "Before we build the system, help me figure out what's actually "
            "making this hard for me."
        )

        self.assert_cognition_first_clarification(decision)
        self.assertEqual(model.calls, [])

    def test_everyday_overwhelm_request_clarifies_before_prescribing_system(
        self,
    ):
        model = FabricatedProjectTradeoffModelService()
        service = ClarificationService(model_service=model)

        decision = service.evaluate(
            "I keep putting off organizing my week because everything feels "
            "equally important and I don't know where to start. Help me turn "
            "this into a simple system I can actually use."
        )

        self.assert_cognition_first_clarification(decision)
        self.assertEqual(model.calls, [])


if __name__ == "__main__":
    unittest.main()
