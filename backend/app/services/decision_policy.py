from dataclasses import dataclass
from typing import Literal

from app.models.project import TaskObservation


Decision = Literal[
    "continue",
    "retry",
    "replan",
    "request_authority",
    "stop",
]


APPROVED_DECISIONS: tuple[Decision, ...] = (
    "continue",
    "retry",
    "replan",
    "request_authority",
    "stop",
)

ALLOWED_TRANSITIONS: dict[str, tuple[Decision, ...]] = {
    "completed": ("continue", "replan", "stop"),
    "failed": ("retry", "replan", "stop"),
    "unsupported": ("replan", "stop"),
    "authority_required": ("request_authority",),
}


@dataclass(frozen=True)
class TaskSummary:
    title: str
    capability: str | None
    status: str


@dataclass(frozen=True)
class DecisionContext:
    project_goal: str
    current_task: TaskSummary
    observation: TaskObservation
    remaining_tasks: list[TaskSummary]
    retry_count: int


@dataclass(frozen=True)
class TaskDecision:
    decision: Decision
    reason: str


def validate_transition(outcome: str, decision: str) -> None:
    if decision not in APPROVED_DECISIONS:
        raise ValueError(f"Unknown decision: {decision}")

    allowed = ALLOWED_TRANSITIONS.get(outcome)
    if allowed is None:
        raise ValueError(f"Unknown observation outcome: {outcome}")

    if decision not in allowed:
        raise ValueError(
            f"Decision '{decision}' is not allowed for outcome '{outcome}'."
        )


class DecisionPolicy:
    def __init__(self, max_retries: int = 2):
        if max_retries < 0:
            raise ValueError("max_retries must be greater than or equal to 0.")

        self.max_retries = max_retries

    def decide(self, context: DecisionContext) -> TaskDecision:
        outcome = context.observation.outcome
        has_remaining_tasks = bool(context.remaining_tasks)

        if outcome == "authority_required":
            return self._validated(
                outcome,
                "request_authority",
                "Human authority is required before any further action.",
            )

        if outcome == "unsupported":
            if has_remaining_tasks:
                return self._validated(
                    outcome,
                    "replan",
                    "Capability is unsupported; existing remaining work requires a revised plan.",
                )
            return self._validated(
                outcome,
                "stop",
                "Capability is unsupported and no remaining work is available to replan.",
            )

        if outcome == "failed":
            if context.retry_count < self.max_retries:
                return self._validated(
                    outcome,
                    "retry",
                    "Task failed and retry budget remains.",
                )
            if has_remaining_tasks:
                return self._validated(
                    outcome,
                    "replan",
                    "Task failed after retry budget was exhausted; remaining work requires a revised plan.",
                )
            return self._validated(
                outcome,
                "stop",
                "Task failed after retry budget was exhausted and no remaining work is available.",
            )

        if outcome == "completed":
            if has_remaining_tasks:
                return self._validated(
                    outcome,
                    "continue",
                    "Task completed and remaining work is available.",
                )
            return self._validated(
                outcome,
                "stop",
                "Task completed and no remaining work is available.",
            )

        raise ValueError(f"Unknown observation outcome: {outcome}")

    @staticmethod
    def _validated(
        outcome: str,
        decision: Decision,
        reason: str,
    ) -> TaskDecision:
        validate_transition(outcome, decision)
        return TaskDecision(decision=decision, reason=reason)
