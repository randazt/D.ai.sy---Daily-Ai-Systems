import asyncio
import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from app.models.project import Task
from app.services.task_executor import TaskExecutionResult, TaskExecutor


class CalleTransportError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        payload: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.payload = payload or {}


class CalleSafetyError(Exception):
    pass


class CalleTransport(ABC):
    @abstractmethod
    async def plan_call(
        self,
        *,
        destination: str,
        objective: str,
        language: str | None = None,
        region: str | None = None,
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    async def run_call(
        self,
        *,
        plan_id: str,
        confirm_token: str,
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    async def get_call_run(
        self,
        *,
        run_id: str,
    ) -> dict[str, Any]:
        pass


class CalleCliTransport(CalleTransport):
    def __init__(
        self,
        calle_command: str = "calle",
        real_calls_env: str = "DAISY_ENABLE_REAL_CALLS",
    ):
        self._calle_command = calle_command
        self._real_calls_env = real_calls_env

    async def plan_call(
        self,
        *,
        destination: str,
        objective: str,
        language: str | None = None,
        region: str | None = None,
    ) -> dict[str, Any]:
        args: dict[str, Any] = {
            "to_phones": [destination],
            "goal": objective,
        }
        if language:
            args["language"] = language
        if region:
            args["region"] = region
        return await self._call_tool("plan_call", args)

    async def run_call(
        self,
        *,
        plan_id: str,
        confirm_token: str,
    ) -> dict[str, Any]:
        return await self._call_tool(
            "run_call",
            {
                "plan_id": plan_id,
                "confirm_token": confirm_token,
            },
        )

    async def get_call_run(
        self,
        *,
        run_id: str,
    ) -> dict[str, Any]:
        return await self._call_tool("get_call_run", {"run_id": run_id})

    async def _call_tool(
        self,
        tool_name: str,
        tool_args: dict[str, Any],
    ) -> dict[str, Any]:
        if os.getenv(self._real_calls_env) != "1":
            raise CalleSafetyError(
                "Real CALL-E execution is disabled. "
                "Set DAISY_ENABLE_REAL_CALLS=1 to enable live calling."
            )

        command = [
            self._calle_command,
            "mcp",
            "call",
            tool_name,
            "--args-json",
            json.dumps(tool_args, ensure_ascii=True),
            "--json",
        ]

        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except FileNotFoundError as e:
            raise CalleTransportError(
                code="calle_executable_unavailable",
                message=(
                    "CALL-E executable not found. "
                    "Ensure 'calle' is installed and available on PATH."
                ),
            ) from e

        stdout_bytes, stderr_bytes = await process.communicate()
        stdout_text = stdout_bytes.decode("utf-8", errors="replace").strip()
        stderr_text = stderr_bytes.decode("utf-8", errors="replace").strip()

        payload = self._decode_payload(stdout_text, tool_name)

        if process.returncode != 0 or payload.get("ok") is False:
            error_payload = payload.get("error")
            error_code = (
                error_payload.get("code")
                if isinstance(error_payload, dict)
                else "calle_transport_error"
            )
            error_message = (
                error_payload.get("message")
                if isinstance(error_payload, dict)
                else stderr_text or f"{tool_name} failed."
            )
            raise CalleTransportError(
                code=str(error_code),
                message=str(error_message),
                payload=payload,
            )

        result = payload.get("result")
        if not isinstance(result, dict):
            raise CalleTransportError(
                code="calle_malformed_response",
                message=f"{tool_name} returned a malformed result payload.",
                payload=payload,
            )

        return result

    @staticmethod
    def _decode_payload(stdout_text: str, tool_name: str) -> dict[str, Any]:
        if not stdout_text:
            raise CalleTransportError(
                code="calle_empty_response",
                message=f"{tool_name} returned an empty response.",
            )

        try:
            payload = json.loads(stdout_text)
        except json.JSONDecodeError as e:
            raise CalleTransportError(
                code="calle_malformed_response",
                message=f"{tool_name} returned non-JSON output.",
            ) from e

        if not isinstance(payload, dict):
            raise CalleTransportError(
                code="calle_malformed_response",
                message=f"{tool_name} returned a non-object JSON payload.",
            )

        return payload


@dataclass
class CalleExecutionConfig:
    poll_interval_seconds: float = 2.0
    poll_timeout_seconds: float = 120.0


class CalleTaskExecutor(TaskExecutor):
    SUCCESS_STATUSES = {"COMPLETED"}
    FAILED_STATUSES = {
        "FAILED",
        "DECLINED",
        "NO_ANSWER",
        "BUSY",
        "CANCELED",
        "CANCELLED",
        "VOICEMAIL",
        "EXPIRED",
    }

    def __init__(
        self,
        transport: CalleTransport | None = None,
        config: CalleExecutionConfig | None = None,
    ):
        self._transport = transport or CalleCliTransport()
        self._config = config or CalleExecutionConfig()

    async def execute(self, task: Task) -> TaskExecutionResult:
        destination = self._extract_destination(task)
        if not destination:
            return TaskExecutionResult(
                success=False,
                error="Missing required phone_call input: destination.",
            )

        objective = self._build_objective(task)
        language = self._extract_optional_string(task, "language")
        region = self._extract_optional_string(task, "region")

        try:
            plan_result = await self._transport.plan_call(
                destination=destination,
                objective=objective,
                language=language,
                region=region,
            )
        except CalleSafetyError as e:
            return TaskExecutionResult(success=False, error=str(e))
        except CalleTransportError as e:
            return TaskExecutionResult(
                success=False,
                error=self._format_transport_error("plan_call", e),
            )
        except Exception as e:
            return TaskExecutionResult(
                success=False,
                error=f"CALL-E transport exception during plan_call: {e}",
            )

        structured_plan = self._structured_payload(plan_result)
        ready_to_run = structured_plan.get("ready_to_run")
        if ready_to_run is False:
            clarification = self._first_clarifying_question(structured_plan)
            detail = f" Clarification needed: {clarification}" if clarification else ""
            return TaskExecutionResult(
                success=False,
                error=f"CALL-E plan is not ready to run.{detail}",
            )
        if ready_to_run is not True:
            return TaskExecutionResult(
                success=False,
                error="CALL-E plan response missing ready_to_run=true.",
            )

        try:
            plan_id = self._extract_required_string(
                plan_result,
                "plan_id",
                "plan_call",
            )
            confirm_token = self._extract_required_string(
                plan_result,
                "confirm_token",
                "plan_call",
            )
        except ValueError as e:
            return TaskExecutionResult(success=False, error=str(e))

        try:
            run_result = await self._transport.run_call(
                plan_id=plan_id,
                confirm_token=confirm_token,
            )
        except CalleSafetyError as e:
            return TaskExecutionResult(success=False, error=str(e))
        except CalleTransportError as e:
            return TaskExecutionResult(
                success=False,
                error=self._format_transport_error("run_call", e),
            )
        except Exception as e:
            return TaskExecutionResult(
                success=False,
                error=f"CALL-E transport exception during run_call: {e}",
            )

        try:
            run_id = self._extract_required_string(
                run_result,
                "run_id",
                "run_call",
            )
        except ValueError as e:
            return TaskExecutionResult(success=False, error=str(e))

        try:
            final_status_result = await self._poll_until_terminal(run_result, run_id)
        except TimeoutError as e:
            return TaskExecutionResult(success=False, error=str(e))
        except CalleSafetyError as e:
            return TaskExecutionResult(success=False, error=str(e))
        except CalleTransportError as e:
            return TaskExecutionResult(
                success=False,
                error=self._format_transport_error("get_call_run", e),
            )
        except Exception as e:
            return TaskExecutionResult(
                success=False,
                error=f"CALL-E transport exception during status polling: {e}",
            )

        structured_status = self._structured_payload(final_status_result)
        status = self._normalize_status(structured_status.get("status"))
        if status is None:
            return TaskExecutionResult(
                success=False,
                error="CALL-E status response is missing a terminal status.",
            )

        if status in self.FAILED_STATUSES:
            summary = self._extract_summary(structured_status)
            detail = f" ({summary})" if summary else ""
            return TaskExecutionResult(
                success=False,
                error=f"CALL-E call ended with status {status}.{detail}",
            )

        if status not in self.SUCCESS_STATUSES:
            return TaskExecutionResult(
                success=False,
                error=f"CALL-E ended in unsupported terminal status: {status}.",
            )

        success_payload = self._build_success_payload(structured_status)
        if success_payload is None:
            return TaskExecutionResult(
                success=False,
                error="CALL-E completed but returned no usable result.",
            )

        return TaskExecutionResult(
            success=True,
            output=json.dumps(success_payload, ensure_ascii=True),
        )

    async def _poll_until_terminal(
        self,
        initial_run_result: dict[str, Any],
        run_id: str,
    ) -> dict[str, Any]:
        current_result = initial_run_result
        start_time = asyncio.get_running_loop().time()

        while True:
            structured = self._structured_payload(current_result)
            status = self._normalize_status(structured.get("status"))
            if status is None:
                raise CalleTransportError(
                    code="calle_malformed_response",
                    message="CALL-E status payload is missing status.",
                    payload=current_result,
                )

            if status in self.SUCCESS_STATUSES or status in self.FAILED_STATUSES:
                return current_result

            elapsed = asyncio.get_running_loop().time() - start_time
            if elapsed >= self._config.poll_timeout_seconds:
                raise TimeoutError(
                    "CALL-E status polling timed out before terminal status."
                )

            await asyncio.sleep(self._config.poll_interval_seconds)
            current_result = await self._transport.get_call_run(run_id=run_id)

    def _build_objective(self, task: Task) -> str:
        explicit = self._extract_optional_string(task, "objective")
        if explicit:
            return explicit

        fallback = task.description.strip() or task.title.strip()
        questions = task.inputs.get("questions") if isinstance(task.inputs, dict) else None
        question_items = self._normalize_questions(questions)
        if question_items:
            question_block = "\n".join(f"- {question}" for question in question_items)
            return f"{fallback}\n\nQuestions to ask:\n{question_block}"

        return fallback

    @staticmethod
    def _extract_destination(task: Task) -> str | None:
        if not isinstance(task.inputs, dict):
            return None

        destination = task.inputs.get("destination")
        if isinstance(destination, str) and destination.strip():
            return destination.strip()

        return None

    @staticmethod
    def _extract_optional_string(task: Task, key: str) -> str | None:
        if not isinstance(task.inputs, dict):
            return None

        value = task.inputs.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

        return None

    @staticmethod
    def _normalize_questions(value: object) -> list[str]:
        if not isinstance(value, list):
            return []

        normalized: list[str] = []
        for item in value:
            if isinstance(item, str) and item.strip():
                normalized.append(item.strip())
        return normalized

    @staticmethod
    def _structured_payload(result: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(result, dict):
            return {}

        if isinstance(result.get("structuredContent"), dict):
            return result["structuredContent"]
        if isinstance(result.get("structured_content"), dict):
            return result["structured_content"]

        return result

    @classmethod
    def _extract_required_string(
        cls,
        payload: dict[str, Any],
        field_name: str,
        context: str,
    ) -> str:
        structured = cls._structured_payload(payload)
        value = structured.get(field_name)
        if isinstance(value, str) and value.strip():
            return value.strip()

        raise ValueError(f"CALL-E {context} did not return required field: {field_name}.")

    @staticmethod
    def _first_clarifying_question(structured_plan: dict[str, Any]) -> str | None:
        questions = structured_plan.get("clarifying_questions")
        if isinstance(questions, list):
            for item in questions:
                if isinstance(item, str) and item.strip():
                    return item.strip()
        return None

    @staticmethod
    def _normalize_status(status: object) -> str | None:
        if not isinstance(status, str):
            return None

        normalized = status.strip().upper().replace(" ", "_")
        return normalized or None

    @classmethod
    def _extract_summary(cls, structured_status: dict[str, Any]) -> str | None:
        result = structured_status.get("result")
        if not isinstance(result, dict):
            return None

        for key in ("summary", "post_summary"):
            value = result.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

        return None

    @classmethod
    def _build_success_payload(
        cls,
        structured_status: dict[str, Any],
    ) -> dict[str, Any] | None:
        result = structured_status.get("result")
        if not isinstance(result, dict):
            return None

        summary = cls._extract_summary(structured_status)
        outcome = result.get("outcome") if isinstance(result.get("outcome"), dict) else None
        extracted = result.get("extracted") if isinstance(result.get("extracted"), dict) else None

        if not summary and not outcome and not extracted:
            return None

        payload: dict[str, Any] = {
            "framework": "call-e",
            "status": "COMPLETED",
        }
        if summary:
            payload["summary"] = summary
        if outcome:
            payload["outcome"] = outcome
        if extracted:
            payload["extracted"] = extracted

        return payload

    @staticmethod
    def _format_transport_error(stage: str, error: CalleTransportError) -> str:
        code = (error.code or "").strip()
        message = (error.message or "").strip() or f"{stage} failed."

        if code == "auth_required":
            return f"CALL-E authentication required during {stage}: {message}"
        if code == "plan_not_ready":
            return f"CALL-E plan rejected during {stage}: {message}"
        if code == "calle_executable_unavailable":
            return message
        if code:
            return f"CALL-E {stage} failed ({code}): {message}"

        return f"CALL-E {stage} failed: {message}"
