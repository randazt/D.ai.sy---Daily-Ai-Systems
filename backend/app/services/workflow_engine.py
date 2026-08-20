from dataclasses import dataclass

from app.services.capability_registry import CapabilityRegistry
from app.models.project import Project, Task, TaskObservation
from app.services.adk_task_executor import AdkTaskExecutor
from app.services.calle_task_executor import CalleTaskExecutor
from app.services.decision_policy import (
    DecisionContext,
    DecisionPolicy,
    TaskDecision,
    TaskSummary,
)
from app.services.task_executor import (
    TaskExecutionResult,
    TaskExecutor,
)


@dataclass
class WorkflowTaskDecisionResult:
    execution_result: TaskExecutionResult
    decision: TaskDecision


class WorkflowEngine:
    """
    Coordinates execution of project tasks.

    The WorkflowEngine is responsible for moving tasks through
    the execution lifecycle while delegating actual work to
    execution infrastructure and tools.
    """

    def __init__(
        self,
        executor: TaskExecutor | None = None,
        capability_registry: CapabilityRegistry | None = None,
        decision_policy: DecisionPolicy | None = None,
    ):
        if executor is not None and capability_registry is not None:
            raise ValueError(
                "Provide either executor or capability_registry, not both."
            )

        if capability_registry is None:
            capability_registry = CapabilityRegistry()
            capability_registry.register(
                "reasoning",
                executor or AdkTaskExecutor(),
            )
            if executor is None:
                capability_registry.register(
                    "phone_call",
                    CalleTaskExecutor(),
                )

        self._capability_registry = capability_registry
        self._decision_policy = decision_policy or DecisionPolicy()

    async def execute_task(self, task: Task):
        """
        Execute a single task.

        Task execution behavior will be added incrementally.
        """
        normalized_capability = self._normalize_capability(task.capability)

        if task.status != "pending":
            return self._attach_observation(
                task=task,
                capability=normalized_capability,
                result=TaskExecutionResult(
                    success=False,
                    error=(
                        f"Task is not pending. Current status: {task.status}"
                    ),
                    outcome="failed",
                ),
            )

        task.status = "running"

        executor = self._capability_registry.resolve(task.capability)
        if executor is None:
            result = TaskExecutionResult(
                success=False,
                error=(
                    "No executor registered for capability: "
                    f"{normalized_capability}"
                ),
                outcome="unsupported",
            )
        else:
            try:
                result = await executor.execute(task)
            except Exception as e:
                result = TaskExecutionResult(
                    success=False,
                    error=f"Executor raised an exception: {e}",
                    outcome="failed",
                )

        if result.success:
            task.status = "completed"
            task.output = result.output
        else:
            task.status = "failed"
            task.output = result.error or result.output or "Execution failed."

        return self._attach_observation(
            task=task,
            capability=normalized_capability,
            result=result,
        )

    async def execute_task_with_decision(
        self,
        *,
        project: Project,
        task: Task,
    ) -> WorkflowTaskDecisionResult:
        """
        Execute one task, evaluate the next decision, and stop.
        """
        self._find_task_index(project=project, current_task=task)
        execution_result = await self.execute_task(task)

        if execution_result.observation is None:
            raise ValueError("Task execution did not produce an observation.")

        decision = self.evaluate_decision(
            project=project,
            current_task=task,
            observation=execution_result.observation,
        )

        return WorkflowTaskDecisionResult(
            execution_result=execution_result,
            decision=decision,
        )

    def evaluate_decision(
        self,
        *,
        project: Project,
        current_task: Task,
        observation: TaskObservation,
    ) -> TaskDecision:
        current_task_index = self._find_task_index(
            project=project,
            current_task=current_task,
        )
        context = DecisionContext(
            project_goal=project.title,
            current_task=self._build_task_summary(current_task),
            observation=observation,
            remaining_tasks=[
                self._build_task_summary(task)
                for task in project.tasks[current_task_index + 1:]
                if task.status == "pending"
            ],
            retry_count=current_task.retry_count,
        )

        return self._decision_policy.decide(context)

    @staticmethod
    def _normalize_capability(capability: str | None) -> str:
        if capability is None:
            return "reasoning"

        normalized = capability.strip().lower()
        if not normalized:
            return "reasoning"

        return normalized

    @staticmethod
    def _build_task_summary(task: Task) -> TaskSummary:
        return TaskSummary(
            title=task.title,
            capability=task.capability,
            status=task.status,
        )

    @staticmethod
    def _find_task_index(*, project: Project, current_task: Task) -> int:
        identity_matches = [
            index
            for index, task in enumerate(project.tasks)
            if task is current_task
        ]
        if len(identity_matches) == 1:
            return identity_matches[0]
        if len(identity_matches) > 1:
            raise ValueError("Current task appears multiple times in project.")

        value_matches = [
            index
            for index, task in enumerate(project.tasks)
            if task == current_task
        ]
        if len(value_matches) == 1:
            return value_matches[0]
        if not value_matches:
            raise ValueError("Current task does not belong to project.")

        raise ValueError("Current task position is ambiguous in project.")

    @classmethod
    def _attach_observation(
        cls,
        *,
        task: Task,
        capability: str,
        result: TaskExecutionResult,
    ) -> TaskExecutionResult:
        summary = cls._build_summary(task, result)
        result.observation = TaskObservation(
            task_title=task.title,
            capability=capability,
            status=task.status,
            success=result.success,
            outcome=cls._resolve_outcome(result),
            summary=summary,
            error=result.error,
        )
        return result

    @staticmethod
    def _build_summary(task: Task, result: TaskExecutionResult) -> str:
        if result.success:
            return result.output or task.output

        return result.error or result.output or task.output or "Execution failed."

    @staticmethod
    def _resolve_outcome(result: TaskExecutionResult) -> str:
        if result.success:
            return "completed"
        if result.outcome == "authority_required":
            return "authority_required"
        if result.outcome == "unsupported":
            return "unsupported"
        return "failed"


workflow_engine = WorkflowEngine()
