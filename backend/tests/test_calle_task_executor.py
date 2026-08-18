import json
import os
import unittest
from unittest.mock import patch

from app.models.project import Task
from app.services.calle_task_executor import (
    CalleCliTransport,
    CalleExecutionConfig,
    CalleSafetyError,
    CalleTaskExecutor,
    CalleTransport,
    CalleTransportError,
)


class FakeCalleTransport(CalleTransport):
    def __init__(self):
        self.plan_response: dict = {}
        self.run_response: dict = {}
        self.status_responses: list[dict] = []
        self.plan_exception: Exception | None = None
        self.run_exception: Exception | None = None
        self.status_exception: Exception | None = None
        self.plan_calls = 0
        self.run_calls = 0
        self.status_calls = 0
        self.last_plan_args: dict[str, object] = {}

    async def plan_call(
        self,
        *,
        destination: str,
        objective: str,
        language: str | None = None,
        region: str | None = None,
    ) -> dict:
        self.plan_calls += 1
        self.last_plan_args = {
            "destination": destination,
            "objective": objective,
            "language": language,
            "region": region,
        }
        if self.plan_exception:
            raise self.plan_exception
        return self.plan_response

    async def run_call(self, *, plan_id: str, confirm_token: str) -> dict:
        self.run_calls += 1
        if self.run_exception:
            raise self.run_exception
        return self.run_response

    async def get_call_run(self, *, run_id: str) -> dict:
        self.status_calls += 1
        if self.status_exception:
            raise self.status_exception
        if self.status_responses:
            return self.status_responses.pop(0)
        return {"status": "IN_PROGRESS"}


class CalleTaskExecutorTests(unittest.IsolatedAsyncioTestCase):
    def _executor(
        self,
        transport: CalleTransport | None = None,
        timeout_seconds: float = 10.0,
        interval_seconds: float = 0.0,
    ) -> CalleTaskExecutor:
        return CalleTaskExecutor(
            transport=transport or FakeCalleTransport(),
            config=CalleExecutionConfig(
                poll_interval_seconds=interval_seconds,
                poll_timeout_seconds=timeout_seconds,
            ),
        )

    async def test_task_inputs_default_to_empty_dict(self):
        task = Task(title="Call contact", capability="phone_call")
        self.assertEqual(task.inputs, {})

    async def test_existing_task_constructor_remains_valid(self):
        task = Task(title="Call contact")
        self.assertEqual(task.title, "Call contact")
        self.assertEqual(task.inputs, {})

    async def test_missing_destination_returns_controlled_failure(self):
        executor = self._executor()
        task = Task(title="Call customer", capability="phone_call")

        result = await executor.execute(task)

        self.assertFalse(result.success)
        self.assertIn("Missing required phone_call input: destination", result.error)

    async def test_objective_falls_back_to_description_then_title(self):
        transport = FakeCalleTransport()
        transport.plan_response = {
            "ready_to_run": True,
            "plan_id": "plan_1",
            "confirm_token": "token_1",
        }
        transport.run_response = {"run_id": "run_1", "status": "IN_PROGRESS"}
        transport.status_responses = [
            {
                "run_id": "run_1",
                "status": "COMPLETED",
                "result": {"summary": "Call finished successfully."},
            }
        ]

        executor = self._executor(transport=transport)

        description_task = Task(
            title="Fallback title",
            description="Description objective",
            capability="phone_call",
            inputs={"destination": "+15551234567"},
        )
        await executor.execute(description_task)
        self.assertEqual(
            transport.last_plan_args["objective"],
            "Description objective",
        )

        title_task = Task(
            title="Title objective",
            capability="phone_call",
            inputs={"destination": "+15557654321"},
        )
        await executor.execute(title_task)
        self.assertEqual(
            transport.last_plan_args["objective"],
            "Title objective",
        )

    async def test_successful_plan_run_status_lifecycle_returns_success(self):
        transport = FakeCalleTransport()
        transport.plan_response = {
            "ready_to_run": True,
            "plan_id": "plan_1",
            "confirm_token": "token_1",
        }
        transport.run_response = {"run_id": "run_1", "status": "PREPARING"}
        transport.status_responses = [
            {"run_id": "run_1", "status": "IN_PROGRESS"},
            {
                "run_id": "run_1",
                "status": "COMPLETED",
                "result": {
                    "summary": "Call complete.",
                    "outcome": {"task_completed": True},
                    "extracted": {"decision": "yes"},
                    "transcript": "private transcript not surfaced",
                },
            },
        ]
        executor = self._executor(transport=transport)
        task = Task(
            title="Call customer",
            capability="phone_call",
            inputs={"destination": "+15551230001", "objective": "Collect decision"},
        )

        result = await executor.execute(task)

        self.assertTrue(result.success)
        payload = json.loads(result.output)
        self.assertEqual(payload["framework"], "call-e")
        self.assertEqual(payload["status"], "COMPLETED")
        self.assertEqual(payload["summary"], "Call complete.")
        self.assertEqual(payload["extracted"], {"decision": "yes"})
        self.assertNotIn("transcript", payload)
        self.assertEqual(transport.plan_calls, 1)
        self.assertEqual(transport.run_calls, 1)
        self.assertGreaterEqual(transport.status_calls, 1)

    async def test_plan_not_ready_returns_failure(self):
        transport = FakeCalleTransport()
        transport.plan_response = {
            "ready_to_run": False,
            "clarifying_questions": ["What is the recipient timezone?"],
        }
        executor = self._executor(transport=transport)
        task = Task(
            title="Call customer",
            capability="phone_call",
            inputs={"destination": "+15551230002"},
        )

        result = await executor.execute(task)

        self.assertFalse(result.success)
        self.assertIn("CALL-E plan is not ready to run", result.error)
        self.assertIn("Clarification needed", result.error)

    async def test_auth_required_maps_to_failure(self):
        transport = FakeCalleTransport()
        transport.plan_exception = CalleTransportError(
            code="auth_required",
            message="Login required.",
        )
        executor = self._executor(transport=transport)
        task = Task(
            title="Call customer",
            capability="phone_call",
            inputs={"destination": "+15551230003"},
        )

        result = await executor.execute(task)

        self.assertFalse(result.success)
        self.assertIn("CALL-E authentication required during plan_call", result.error)

    async def test_executable_unavailable_maps_to_failure(self):
        transport = FakeCalleTransport()
        transport.plan_exception = CalleTransportError(
            code="calle_executable_unavailable",
            message="CALL-E executable not found.",
        )
        executor = self._executor(transport=transport)
        task = Task(
            title="Call customer",
            capability="phone_call",
            inputs={"destination": "+15551230004"},
        )

        result = await executor.execute(task)

        self.assertFalse(result.success)
        self.assertIn("CALL-E executable not found", result.error)

    async def test_polling_timeout_maps_to_failure(self):
        transport = FakeCalleTransport()
        transport.plan_response = {
            "ready_to_run": True,
            "plan_id": "plan_2",
            "confirm_token": "token_2",
        }
        transport.run_response = {"run_id": "run_2", "status": "IN_PROGRESS"}
        executor = self._executor(
            transport=transport,
            timeout_seconds=0.01,
            interval_seconds=0.01,
        )
        task = Task(
            title="Call customer",
            capability="phone_call",
            inputs={"destination": "+15551230005"},
        )

        result = await executor.execute(task)

        self.assertFalse(result.success)
        self.assertIn("status polling timed out", result.error)

    async def test_run_rejected_maps_to_failure(self):
        transport = FakeCalleTransport()
        transport.plan_response = {
            "ready_to_run": True,
            "plan_id": "plan_run_reject",
            "confirm_token": "token_run_reject",
        }
        transport.run_response = {
            "run_id": "run_run_reject",
            "status": "FAILED",
            "error": "run request rejected",
        }
        executor = self._executor(transport=transport)
        task = Task(
            title="Call customer",
            capability="phone_call",
            inputs={"destination": "+15551239999"},
        )

        result = await executor.execute(task)

        self.assertFalse(result.success)
        self.assertIn("status FAILED", result.error)

    async def test_failed_terminal_status_maps_to_failure(self):
        transport = FakeCalleTransport()
        transport.plan_response = {
            "ready_to_run": True,
            "plan_id": "plan_3",
            "confirm_token": "token_3",
        }
        transport.run_response = {"run_id": "run_3", "status": "IN_PROGRESS"}
        transport.status_responses = [
            {
                "run_id": "run_3",
                "status": "FAILED",
                "result": {"summary": "Carrier error."},
            }
        ]
        executor = self._executor(transport=transport)
        task = Task(
            title="Call customer",
            capability="phone_call",
            inputs={"destination": "+15551230006"},
        )

        result = await executor.execute(task)

        self.assertFalse(result.success)
        self.assertIn("status FAILED", result.error)

    async def test_declined_terminal_status_maps_to_failure(self):
        transport = FakeCalleTransport()
        transport.plan_response = {
            "ready_to_run": True,
            "plan_id": "plan_4",
            "confirm_token": "token_4",
        }
        transport.run_response = {"run_id": "run_4", "status": "IN_PROGRESS"}
        transport.status_responses = [
            {"run_id": "run_4", "status": "DECLINED", "result": {"summary": "Declined."}}
        ]
        executor = self._executor(transport=transport)
        task = Task(
            title="Call customer",
            capability="phone_call",
            inputs={"destination": "+15551230007"},
        )

        result = await executor.execute(task)

        self.assertFalse(result.success)
        self.assertIn("status DECLINED", result.error)

    async def test_no_answer_terminal_status_maps_to_failure(self):
        transport = FakeCalleTransport()
        transport.plan_response = {
            "ready_to_run": True,
            "plan_id": "plan_5",
            "confirm_token": "token_5",
        }
        transport.run_response = {"run_id": "run_5", "status": "IN_PROGRESS"}
        transport.status_responses = [
            {"run_id": "run_5", "status": "NO ANSWER", "result": {"summary": "No answer."}}
        ]
        executor = self._executor(transport=transport)
        task = Task(
            title="Call customer",
            capability="phone_call",
            inputs={"destination": "+15551230008"},
        )

        result = await executor.execute(task)

        self.assertFalse(result.success)
        self.assertIn("status NO_ANSWER", result.error)

    async def test_malformed_response_maps_to_failure(self):
        transport = FakeCalleTransport()
        transport.plan_response = {"ready_to_run": True}
        executor = self._executor(transport=transport)
        task = Task(
            title="Call customer",
            capability="phone_call",
            inputs={"destination": "+15551230009"},
        )

        result = await executor.execute(task)

        self.assertFalse(result.success)
        self.assertIn("did not return required field: plan_id", result.error)

    async def test_malformed_status_response_maps_to_failure(self):
        transport = FakeCalleTransport()
        transport.plan_response = {
            "ready_to_run": True,
            "plan_id": "plan_8",
            "confirm_token": "token_8",
        }
        transport.run_response = {"run_id": "run_8", "status": "IN_PROGRESS"}
        transport.status_responses = [{"run_id": "run_8"}]
        executor = self._executor(transport=transport)
        task = Task(
            title="Call customer",
            capability="phone_call",
            inputs={"destination": "+15551230014"},
        )

        result = await executor.execute(task)

        self.assertFalse(result.success)
        self.assertIn("status payload is missing status", result.error)

    async def test_completed_without_usable_result_maps_to_failure(self):
        transport = FakeCalleTransport()
        transport.plan_response = {
            "ready_to_run": True,
            "plan_id": "plan_6",
            "confirm_token": "token_6",
        }
        transport.run_response = {"run_id": "run_6", "status": "IN_PROGRESS"}
        transport.status_responses = [
            {"run_id": "run_6", "status": "COMPLETED", "result": {}}
        ]
        executor = self._executor(transport=transport)
        task = Task(
            title="Call customer",
            capability="phone_call",
            inputs={"destination": "+15551230010"},
        )

        result = await executor.execute(task)

        self.assertFalse(result.success)
        self.assertIn("completed but returned no usable result", result.error)

    async def test_transport_exception_maps_to_controlled_failure(self):
        transport = FakeCalleTransport()
        transport.plan_exception = RuntimeError("unexpected transport error")
        executor = self._executor(transport=transport)
        task = Task(
            title="Call customer",
            capability="phone_call",
            inputs={"destination": "+15551230011"},
        )

        result = await executor.execute(task)

        self.assertFalse(result.success)
        self.assertIn("transport exception during plan_call", result.error)

    async def test_fake_transport_avoids_real_cli_invocation(self):
        transport = FakeCalleTransport()
        transport.plan_response = {
            "ready_to_run": True,
            "plan_id": "plan_7",
            "confirm_token": "token_7",
        }
        transport.run_response = {"run_id": "run_7", "status": "IN_PROGRESS"}
        transport.status_responses = [
            {
                "run_id": "run_7",
                "status": "COMPLETED",
                "result": {"summary": "Done"},
            }
        ]
        executor = self._executor(transport=transport)
        task = Task(
            title="Call customer",
            capability="phone_call",
            inputs={"destination": "+15551230012"},
        )

        with patch(
            "app.services.calle_task_executor.asyncio.create_subprocess_exec",
            side_effect=AssertionError("real CLI invocation should not happen"),
        ) as subprocess_mock:
            result = await executor.execute(task)

        self.assertTrue(result.success)
        subprocess_mock.assert_not_called()

    async def test_real_call_guard_blocks_cli_transport_by_default(self):
        transport = CalleCliTransport(calle_command="calle")

        with patch.dict(os.environ, {"DAISY_ENABLE_REAL_CALLS": "0"}, clear=False):
            with self.assertRaises(CalleSafetyError):
                await transport.plan_call(
                    destination="+15551230013",
                    objective="Confirm appointment",
                )
