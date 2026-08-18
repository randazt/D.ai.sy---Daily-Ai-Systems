import unittest
from unittest.mock import AsyncMock, patch

from app.models.project import Task
from app.services.adk_task_executor import AdkTaskExecutor
from app.services.task_executor import TaskExecutionResult


class AdkTaskExecutorTests(unittest.IsolatedAsyncioTestCase):
    async def test_success_maps_to_task_execution_result(self):
        executor = AdkTaskExecutor()
        task = Task(title="Summarize findings", description="Keep it concise")

        with patch.object(
            executor,
            "_run_with_adk",
            new=AsyncMock(return_value="Done through ADK"),
        ):
            result = await executor.execute(task)

        self.assertIsInstance(result, TaskExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.output, "Done through ADK")
        self.assertEqual(result.error, "")

    async def test_adk_failure_maps_to_controlled_error(self):
        executor = AdkTaskExecutor()
        task = Task(title="Summarize findings")

        with patch.object(
            executor,
            "_run_with_adk",
            new=AsyncMock(side_effect=RuntimeError("adk failed")),
        ):
            result = await executor.execute(task)

        self.assertFalse(result.success)
        self.assertEqual(result.output, "")
        self.assertIn("ADK execution failed:", result.error)

    async def test_missing_adk_dependency_maps_to_controlled_error(self):
        executor = AdkTaskExecutor()
        task = Task(title="Summarize findings")

        with patch.object(
            executor,
            "_run_with_adk",
            new=AsyncMock(side_effect=ImportError("No module named google.adk")),
        ):
            result = await executor.execute(task)

        self.assertFalse(result.success)
        self.assertEqual(result.output, "")
        self.assertIn("google-adk is not installed", result.error)
