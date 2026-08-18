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

    def __init__(self, executor: TaskExecutor | None = None):
        self._executor = executor or GeminiTaskExecutor()

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

        try:
            result = await self._executor.execute(task)
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


workflow_engine = WorkflowEngine()
