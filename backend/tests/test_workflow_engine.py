import unittest
from unittest.mock import AsyncMock, patch

from app.models.project import Task, TaskObservation
from app.services.adk_task_executor import AdkTaskExecutor
from app.services.calle_task_executor import CalleTaskExecutor
from app.services.capability_registry import CapabilityRegistry
from app.services.task_executor import TaskExecutionResult, TaskExecutor
from app.services.workflow_engine import WorkflowEngine


class SuccessfulExecutor(TaskExecutor):
    async def execute(self, task: Task) -> TaskExecutionResult:
        return TaskExecutionResult(
            success=True,
            output=f"Executed: {task.title}",
        )


class FailedExecutor(TaskExecutor):
    async def execute(self, task: Task) -> TaskExecutionResult:
        return TaskExecutionResult(
            success=False,
            error=f"Failed: {task.title}",
        )


class ExceptionExecutor(TaskExecutor):
    async def execute(self, task: Task) -> TaskExecutionResult:
        raise RuntimeError("executor exploded")


class RecordingExecutor(TaskExecutor):
    def __init__(self, result: TaskExecutionResult):
        self.result = result
        self.calls = 0

    async def execute(self, task: Task) -> TaskExecutionResult:
        self.calls += 1
        return self.result


class WorkflowEngineExecutionTests(unittest.IsolatedAsyncioTestCase):
    def test_task_capability_defaults_to_none(self):
        task = Task(title="Do default work")
        self.assertIsNone(task.capability)
        self.assertEqual(task.inputs, {})

    async def test_successful_execution_marks_task_completed(self):
        task = Task(title="Do successful work")
        engine = WorkflowEngine(executor=SuccessfulExecutor())

        result = await engine.execute_task(task)

        self.assertTrue(result.success)
        self.assertEqual(task.status, "completed")
        self.assertIn("Executed:", task.output)
        self.assertIsInstance(result.observation, TaskObservation)
        self.assertEqual(result.observation.outcome, "completed")
        self.assertEqual(result.observation.summary, result.output)
        self.assertEqual(result.observation.capability, "reasoning")
        self.assertFalse(hasattr(result.observation, "provider"))

    async def test_failed_execution_marks_task_failed(self):
        task = Task(title="Do failing work")
        engine = WorkflowEngine(executor=FailedExecutor())

        result = await engine.execute_task(task)

        self.assertFalse(result.success)
        self.assertEqual(task.status, "failed")
        self.assertIn("Failed:", task.output)
        self.assertIsInstance(result.observation, TaskObservation)
        self.assertEqual(result.observation.outcome, "failed")
        self.assertEqual(result.observation.error, result.error)
        self.assertEqual(result.observation.summary, result.error)

    async def test_executor_exception_becomes_controlled_failure(self):
        task = Task(title="Do explosive work")
        engine = WorkflowEngine(executor=ExceptionExecutor())

        result = await engine.execute_task(task)

        self.assertFalse(result.success)
        self.assertEqual(task.status, "failed")
        self.assertIn("Executor raised an exception:", task.output)
        self.assertEqual(result.observation.outcome, "failed")

    async def test_none_capability_executes_reasoning_executor(self):
        task = Task(title="No capability task", capability=None)
        executor = RecordingExecutor(
            TaskExecutionResult(success=True, output="Reasoned"),
        )
        engine = WorkflowEngine(executor=executor)

        result = await engine.execute_task(task)

        self.assertTrue(result.success)
        self.assertEqual(executor.calls, 1)
        self.assertEqual(task.status, "completed")
        self.assertEqual(task.output, "Reasoned")

    async def test_reasoning_capability_executes_reasoning_executor(self):
        task = Task(title="Reasoning task", capability="reasoning")
        executor = RecordingExecutor(
            TaskExecutionResult(success=True, output="Reasoned"),
        )
        engine = WorkflowEngine(executor=executor)

        result = await engine.execute_task(task)

        self.assertTrue(result.success)
        self.assertEqual(executor.calls, 1)
        self.assertEqual(task.status, "completed")
        self.assertEqual(task.output, "Reasoned")

    async def test_registered_custom_capability_executes_registered_executor(self):
        task = Task(title="Research task", capability="research")
        executor = RecordingExecutor(
            TaskExecutionResult(success=True, output="Researched"),
        )
        capability_registry = CapabilityRegistry()
        capability_registry.register("research", executor)
        engine = WorkflowEngine(capability_registry=capability_registry)

        result = await engine.execute_task(task)

        self.assertTrue(result.success)
        self.assertEqual(executor.calls, 1)
        self.assertEqual(task.status, "completed")
        self.assertEqual(task.output, "Researched")
        self.assertEqual(result.observation.capability, "research")

    async def test_unsupported_phone_call_capability_fails_without_fallback(self):
        task = Task(
            title="Call target customers",
            capability="phone_call",
        )
        executor = RecordingExecutor(
            TaskExecutionResult(success=True, output="Call completed"),
        )
        engine = WorkflowEngine(executor=executor)

        result = await engine.execute_task(task)

        self.assertFalse(result.success)
        self.assertEqual(
            result.error,
            "No executor registered for capability: phone_call",
        )
        self.assertEqual(task.status, "failed")
        self.assertEqual(
            task.output,
            "No executor registered for capability: phone_call",
        )
        self.assertEqual(executor.calls, 0)
        self.assertEqual(result.observation.outcome, "unsupported")
        self.assertEqual(result.observation.capability, "phone_call")

    def test_default_reasoning_registration_uses_adk_executor(self):
        engine = WorkflowEngine()

        resolved = engine._capability_registry.resolve("reasoning")

        self.assertIsInstance(resolved, AdkTaskExecutor)

    def test_default_phone_call_registration_uses_calle_executor(self):
        engine = WorkflowEngine()

        resolved = engine._capability_registry.resolve("phone_call")

        self.assertIsInstance(resolved, CalleTaskExecutor)

    async def test_default_none_capability_uses_reasoning_registration(self):
        task = Task(title="Default reasoning task", capability=None)
        engine = WorkflowEngine()
        execute_mock = AsyncMock(
            return_value=TaskExecutionResult(
                success=True,
                output="ADK default execution",
            )
        )

        with patch.object(
            AdkTaskExecutor,
            "execute",
            new=execute_mock,
        ):
            result = await engine.execute_task(task)

        execute_mock.assert_awaited_once()
        self.assertTrue(result.success)
        self.assertEqual(task.status, "completed")
        self.assertEqual(task.output, "ADK default execution")

    async def test_unsupported_research_capability_fails_by_default(self):
        task = Task(title="Research market", capability="research")
        engine = WorkflowEngine()

        result = await engine.execute_task(task)

        self.assertFalse(result.success)
        self.assertEqual(
            result.error,
            "No executor registered for capability: research",
        )
        self.assertEqual(task.status, "failed")
        self.assertEqual(
            task.output,
            "No executor registered for capability: research",
        )
        self.assertEqual(result.observation.outcome, "unsupported")
        self.assertEqual(result.observation.capability, "research")

    async def test_unsupported_document_generation_capability_fails_by_default(self):
        task = Task(title="Draft report", capability="document_generation")
        engine = WorkflowEngine()

        result = await engine.execute_task(task)

        self.assertFalse(result.success)
        self.assertEqual(
            result.error,
            "No executor registered for capability: document_generation",
        )
        self.assertEqual(task.status, "failed")
        self.assertEqual(
            task.output,
            "No executor registered for capability: document_generation",
        )
        self.assertEqual(result.observation.outcome, "unsupported")
        self.assertEqual(result.observation.capability, "document_generation")

    async def test_non_pending_task_produces_failure_observation(self):
        task = Task(title="Already done", status="completed")
        engine = WorkflowEngine(executor=SuccessfulExecutor())

        result = await engine.execute_task(task)

        self.assertFalse(result.success)
        self.assertEqual(result.observation.outcome, "failed")
        self.assertEqual(result.observation.status, "completed")

    async def test_authority_required_result_produces_authority_required_observation(self):
        task = Task(title="Call customer", capability="phone_call")
        executor = RecordingExecutor(
            TaskExecutionResult(
                success=False,
                error="Authorization required.",
                outcome="authority_required",
            ),
        )
        capability_registry = CapabilityRegistry()
        capability_registry.register("phone_call", executor)
        engine = WorkflowEngine(capability_registry=capability_registry)

        result = await engine.execute_task(task)

        self.assertFalse(result.success)
        self.assertEqual(task.status, "failed")
        self.assertEqual(result.observation.outcome, "authority_required")
        self.assertEqual(result.observation.summary, "Authorization required.")


class StartupImportTests(unittest.TestCase):
    def test_app_startup_import(self):
        from app.main import app

        self.assertIsNotNone(app)
