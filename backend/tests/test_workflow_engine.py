import unittest

from app.models.project import Task
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

    async def test_successful_execution_marks_task_completed(self):
        task = Task(title="Do successful work")
        engine = WorkflowEngine(executor=SuccessfulExecutor())

        result = await engine.execute_task(task)

        self.assertTrue(result.success)
        self.assertEqual(task.status, "completed")
        self.assertIn("Executed:", task.output)

    async def test_failed_execution_marks_task_failed(self):
        task = Task(title="Do failing work")
        engine = WorkflowEngine(executor=FailedExecutor())

        result = await engine.execute_task(task)

        self.assertFalse(result.success)
        self.assertEqual(task.status, "failed")
        self.assertIn("Failed:", task.output)

    async def test_executor_exception_becomes_controlled_failure(self):
        task = Task(title="Do explosive work")
        engine = WorkflowEngine(executor=ExceptionExecutor())

        result = await engine.execute_task(task)

        self.assertFalse(result.success)
        self.assertEqual(task.status, "failed")
        self.assertIn("Executor raised an exception:", task.output)

    async def test_phone_call_capability_uses_existing_executor_for_now(self):
        task = Task(
            title="Call target customers",
            capability="phone_call",
        )
        executor = RecordingExecutor(
            TaskExecutionResult(success=True, output="Call completed"),
        )
        engine = WorkflowEngine(executor=executor)

        result = await engine.execute_task(task)

        self.assertTrue(result.success)
        self.assertEqual(executor.calls, 1)
        self.assertEqual(task.status, "completed")
        self.assertEqual(task.output, "Call completed")


class StartupImportTests(unittest.TestCase):
    def test_app_startup_import(self):
        from app.main import app

        self.assertIsNotNone(app)
