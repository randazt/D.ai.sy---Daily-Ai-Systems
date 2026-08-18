from app.services.capability_registry import CapabilityRegistry
from app.models.project import Task
from app.services.task_executor import (
    GeminiTaskExecutor,
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
                executor or GeminiTaskExecutor(),
            )

        self._capability_registry = capability_registry

    async def execute_task(self, task: Task):
        """
        Execute a single task.

        Task execution behavior will be added incrementally.
        """
        if task.status != "pending":
            return TaskExecutionResult(
                success=False,
                error=(
                    f"Task is not pending. Current status: {task.status}"
                ),
            )

        task.status = "running"

        normalized_capability = self._normalize_capability(task.capability)
        executor = self._capability_registry.resolve(task.capability)
        if executor is None:
            result = TaskExecutionResult(
                success=False,
                error=(
                    "No executor registered for capability: "
                    f"{normalized_capability}"
                ),
            )
        else:
            try:
                result = await executor.execute(task)
            except Exception as e:
                result = TaskExecutionResult(
                    success=False,
                    error=f"Executor raised an exception: {e}",
                )

        if result.success:
            task.status = "completed"
            task.output = result.output
        else:
            task.status = "failed"
            task.output = result.error or result.output or "Execution failed."

        return result

    @staticmethod
    def _normalize_capability(capability: str | None) -> str:
        if capability is None:
            return "reasoning"

        normalized = capability.strip().lower()
        if not normalized:
            return "reasoning"

        return normalized


workflow_engine = WorkflowEngine()
