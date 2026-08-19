from app.services.capability_registry import CapabilityRegistry
from app.models.project import Task, TaskObservation
from app.services.adk_task_executor import AdkTaskExecutor
from app.services.calle_task_executor import CalleTaskExecutor
from app.services.task_executor import (
    TaskExecutionResult,
    TaskExecutor,
)


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

    @staticmethod
    def _normalize_capability(capability: str | None) -> str:
        if capability is None:
            return "reasoning"

        normalized = capability.strip().lower()
        if not normalized:
            return "reasoning"

        return normalized

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
