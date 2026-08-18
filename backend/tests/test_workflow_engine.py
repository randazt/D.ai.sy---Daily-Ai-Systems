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


class WorkflowEngineExecutionTests(unittest.IsolatedAsyncioTestCase):
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


class StartupImportTests(unittest.TestCase):
    def test_app_startup_import(self):
        from app.main import app

        self.assertIsNotNone(app)
