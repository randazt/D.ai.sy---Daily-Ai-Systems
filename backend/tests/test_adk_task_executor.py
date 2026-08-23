import unittest
from unittest.mock import AsyncMock, patch

from app.models.project import Task
from app.services.adk_task_executor import AdkTaskExecutor
from app.services.task_executor import TaskExecutionResult


class AdkTaskExecutorTests(unittest.IsolatedAsyncioTestCase):
    async def test_claim_boundary_instruction_is_supplied_to_reasoning_model(self):
        executor = AdkTaskExecutor()
        task = Task(
            title="Deconstruct value proposition",
            description="Evaluate an affordable AI call-handling service",
        )

        with patch.object(
            executor,
            "_run_with_adk",
            new=AsyncMock(return_value="Bounded reasoning"),
        ) as run_mock:
            await executor.execute(task)

        prompt = run_mock.await_args.args[0]
        agent_instruction = executor._build_agent_instruction()

        for instruction in (prompt, agent_instruction):
            self.assertIn("D.A.I.S.Y. is the agentic system", instruction)
            self.assertIn(
                "user-proposed product, business, service, or concept "
                "is separate",
                instruction,
            )
            self.assertIn("hypothetical or unverified product capabilities", instruction)
            self.assertIn("could exist", instruction)
            self.assertIn("would need to be implemented or validated", instruction)
            self.assertIn(
                "Do not imply D.A.I.S.Y. currently implements",
                instruction,
            )
            self.assertIn("creative reasoning", instruction)

    async def test_evidence_boundary_instruction_is_supplied_to_reasoning_model(self):
        executor = AdkTaskExecutor()
        task = Task(
            title="Define initial target niche",
            description="Analyze small businesses that miss customer calls",
        )

        with patch.object(
            executor,
            "_run_with_adk",
            new=AsyncMock(return_value="Evidence-framed reasoning"),
        ) as run_mock:
            await executor.execute(task)

        prompt = run_mock.await_args.args[0]
        agent_instruction = executor._build_agent_instruction()

        for instruction in (prompt, agent_instruction):
            self.assertIn("reason creatively and generate hypotheses", instruction)
            self.assertIn("External facts, statistics, market behaviors", instruction)
            self.assertIn("prices, performance claims", instruction)
            self.assertIn("availability claims, or business outcomes", instruction)
            self.assertIn("not supplied by the task/context", instruction)
            self.assertIn("must not be presented as established facts", instruction)
            self.assertIn("assumptions, hypotheses, estimates", instruction)
            self.assertIn("illustrative examples", instruction)
            self.assertIn("requiring validation", instruction)
            self.assertIn("Do not fabricate citations", instruction)
            self.assertIn("external verification occurred", instruction)
            self.assertIn("useful business/product reasoning", instruction)

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
