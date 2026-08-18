import os
import uuid
from typing import Any

from dotenv import load_dotenv

from app.models.project import Task
from app.services.task_executor import TaskExecutionResult, TaskExecutor

load_dotenv()


class AdkTaskExecutor(TaskExecutor):
    """
    Executes reasoning tasks through Google ADK.
    """

    def __init__(self, model: str | None = None):
        self._model = model or os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

    async def execute(self, task: Task) -> TaskExecutionResult:
        prompt = (
            "You are D.A.I.S.Y.'s execution backend.\n\n"
            "Execute the following task and return a concise execution result.\n\n"
            f"Task Title: {task.title}\n"
            f"Task Description: {task.description}\n"
        )

        try:
            output = await self._run_with_adk(prompt)
        except ImportError:
            return TaskExecutionResult(
                success=False,
                error=(
                    "google-adk is not installed. "
                    "Install backend dependencies to enable ADK execution."
                ),
            )
        except Exception as e:
            return TaskExecutionResult(
                success=False,
                error=f"ADK execution failed: {e}",
            )

        if not output:
            return TaskExecutionResult(
                success=False,
                error="ADK execution completed without textual output.",
            )

        return TaskExecutionResult(
            success=True,
            output=output,
        )

    async def _run_with_adk(self, prompt: str) -> str:
        from google.adk import Agent
        from google.adk.runners import InMemoryRunner
        from google.genai import types

        agent = Agent(
            name="daisy_reasoning_executor",
            model=self._model,
            instruction=(
                "You execute one D.A.I.S.Y. task at a time and return a concise,"
                " actionable result."
            ),
        )
        runner = InMemoryRunner(
            agent=agent,
            app_name="daisy-adk-executor",
        )

        user_id = "daisy-executor"
        session_id = str(uuid.uuid4())
        message = types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        )

        final_output = ""
        try:
            await runner.session_service.create_session(
                app_name=runner.app_name,
                user_id=user_id,
                session_id=session_id,
            )

            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=message,
            ):
                event_output = self._extract_event_output(event)
                if event_output:
                    final_output = event_output
        finally:
            await runner.close()

        return final_output.strip()

    @staticmethod
    def _extract_event_output(event: Any) -> str:
        message = getattr(event, "message", None)
        content = getattr(event, "content", None) or message
        parts = getattr(content, "parts", None)

        if parts:
            text_parts: list[str] = []
            for part in parts:
                part_text = getattr(part, "text", None)
                if isinstance(part_text, str) and part_text.strip():
                    text_parts.append(part_text.strip())
            if text_parts:
                return "\n".join(text_parts)

        output = getattr(event, "output", None)
        if isinstance(output, str) and output.strip():
            return output.strip()

        return ""
