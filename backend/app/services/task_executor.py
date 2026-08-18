from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.models.project import Task


@dataclass
class TaskExecutionResult:
    success: bool
    output: str = ""
    error: str = ""


class TaskExecutor(ABC):
    @abstractmethod
    async def execute(self, task: Task) -> TaskExecutionResult:
        pass


class GeminiTaskExecutor(TaskExecutor):
    async def execute(self, task: Task) -> TaskExecutionResult:
        from app.services.gemini_service import gemini_service

        prompt = (
            "You are D.A.I.S.Y.'s execution backend.\n\n"
            "Execute the following task and return a concise execution result.\n\n"
            f"Task Title: {task.title}\n"
            f"Task Description: {task.description}\n"
        )

        response = gemini_service.generate(prompt)

        if not isinstance(response, dict):
            return TaskExecutionResult(
                success=False,
                error="Execution backend returned a non-dict response.",
            )

        error = response.get("error")
        if error:
            return TaskExecutionResult(
                success=False,
                error=str(error),
            )

        reply = response.get("reply")
        if not reply:
            return TaskExecutionResult(
                success=False,
                error="Execution backend did not return output.",
            )

        return TaskExecutionResult(
            success=True,
            output=str(reply),
        )
