import unittest
from dataclasses import fields
from unittest.mock import patch

from app.models.project import Task, TaskObservation
from app.services.decision_policy import (
    ALLOWED_TRANSITIONS,
    APPROVED_DECISIONS,
    DecisionContext,
    DecisionPolicy,
    TaskSummary,
    validate_transition,
)


def observation(outcome: str) -> TaskObservation:
    return TaskObservation(
        task_title="Current task",
        capability="reasoning",
        status="failed" if outcome != "completed" else "completed",
        success=outcome == "completed",
        outcome=outcome,
        summary=f"{outcome} summary",
    )


def context(
    outcome: str,
    *,
    remaining_tasks: list[TaskSummary] | None = None,
    retry_count: int = 0,
) -> DecisionContext:
    return DecisionContext(
        project_goal="Finish the project",
        current_task=TaskSummary(
            title="Current task",
            capability="reasoning",
            status="failed" if outcome != "completed" else "completed",
        ),
        observation=observation(outcome),
        remaining_tasks=remaining_tasks or [],
        retry_count=retry_count,
    )


class DecisionPolicyTests(unittest.TestCase):
    def test_default_task_retry_count_is_zero(self):
        task = Task(title="Existing constructor")

        self.assertEqual(task.retry_count, 0)

    def test_existing_task_constructor_remains_valid(self):
        task = Task(title="Existing constructor")

        self.assertEqual(task.title, "Existing constructor")
        self.assertEqual(task.inputs, {})
        self.assertEqual(task.status, "pending")

    def test_completed_with_remaining_task_continues(self):
        decision = DecisionPolicy().decide(
            context(
                "completed",
                remaining_tasks=[
                    TaskSummary(
                        title="Next task",
                        capability="reasoning",
                        status="pending",
                    ),
                ],
            )
        )

        self.assertEqual(decision.decision, "continue")

    def test_completed_with_no_remaining_task_stops(self):
        decision = DecisionPolicy().decide(context("completed"))

        self.assertEqual(decision.decision, "stop")

    def test_failed_below_retry_limit_retries(self):
        decision = DecisionPolicy(max_retries=2).decide(
            context("failed", retry_count=1)
        )

        self.assertEqual(decision.decision, "retry")

    def test_failed_at_retry_limit_does_not_retry(self):
        decision = DecisionPolicy(max_retries=2).decide(
            context(
                "failed",
                retry_count=2,
                remaining_tasks=[
                    TaskSummary(
                        title="Alternate task",
                        capability="reasoning",
                        status="pending",
                    ),
                ],
            )
        )

        self.assertEqual(decision.decision, "replan")

    def test_failed_above_retry_limit_does_not_retry(self):
        decision = DecisionPolicy(max_retries=2).decide(
            context("failed", retry_count=3)
        )

        self.assertEqual(decision.decision, "stop")

    def test_unsupported_never_retries(self):
        decision = DecisionPolicy().decide(
            context(
                "unsupported",
                remaining_tasks=[
                    TaskSummary(
                        title="Remaining task",
                        capability="reasoning",
                        status="pending",
                    ),
                ],
            )
        )

        self.assertNotEqual(decision.decision, "retry")

    def test_unsupported_never_continues(self):
        decision = DecisionPolicy().decide(
            context(
                "unsupported",
                remaining_tasks=[
                    TaskSummary(
                        title="Remaining task",
                        capability="reasoning",
                        status="pending",
                    ),
                ],
            )
        )

        self.assertNotEqual(decision.decision, "continue")

    def test_authority_required_requests_authority(self):
        decision = DecisionPolicy().decide(context("authority_required"))

        self.assertEqual(decision.decision, "request_authority")

    def test_authority_required_rejects_every_other_decision(self):
        for decision in APPROVED_DECISIONS:
            if decision == "request_authority":
                continue
            with self.subTest(decision=decision):
                with self.assertRaises(ValueError):
                    validate_transition("authority_required", decision)

    def test_invalid_decision_vocabulary_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_transition("completed", "bypass")

    def test_transition_validation_accepts_every_legal_combination(self):
        for outcome, decisions in ALLOWED_TRANSITIONS.items():
            for decision in decisions:
                with self.subTest(outcome=outcome, decision=decision):
                    validate_transition(outcome, decision)

    def test_transition_validation_rejects_every_illegal_combination(self):
        for outcome, allowed_decisions in ALLOWED_TRANSITIONS.items():
            for decision in APPROVED_DECISIONS:
                if decision in allowed_decisions:
                    continue
                with self.subTest(outcome=outcome, decision=decision):
                    with self.assertRaises(ValueError):
                        validate_transition(outcome, decision)

    def test_max_retries_zero_prevents_retry(self):
        decision = DecisionPolicy(max_retries=0).decide(
            context(
                "failed",
                retry_count=0,
                remaining_tasks=[
                    TaskSummary(
                        title="Remaining task",
                        capability="reasoning",
                        status="pending",
                    ),
                ],
            )
        )

        self.assertNotEqual(decision.decision, "retry")
        self.assertEqual(decision.decision, "replan")

    def test_negative_max_retries_is_rejected(self):
        with self.assertRaises(ValueError):
            DecisionPolicy(max_retries=-1)

    def test_decision_context_contains_no_task_inputs_or_provider_fields(self):
        context_fields = {field.name for field in fields(DecisionContext)}
        task_summary_fields = {field.name for field in fields(TaskSummary)}
        forbidden = {
            "inputs",
            "plan_id",
            "confirm_token",
            "phone_provider",
            "runtime_id",
            "credentials",
            "raw_response",
        }

        self.assertEqual(context_fields & forbidden, set())
        self.assertEqual(task_summary_fields & forbidden, set())

    def test_policy_evaluation_does_not_mutate_retry_count(self):
        decision_context = context("failed", retry_count=1)

        DecisionPolicy(max_retries=2).decide(decision_context)

        self.assertEqual(decision_context.retry_count, 1)

    def test_calle_executor_is_never_invoked_by_decision_policy(self):
        with patch(
            "app.services.calle_task_executor.CalleTaskExecutor.execute",
        ) as execute_mock:
            DecisionPolicy().decide(context("authority_required"))

        execute_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
