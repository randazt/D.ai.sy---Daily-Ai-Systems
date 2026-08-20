import unittest
from unittest.mock import AsyncMock, patch

from app.models.project import Project, Task, TaskObservation
from app.services.decision_policy import TaskDecision
from app.services.adk_task_executor import AdkTaskExecutor
from app.services.calle_task_executor import CalleTaskExecutor
from app.services.capability_registry import CapabilityRegistry
from app.services.task_executor import TaskExecutionResult, TaskExecutor
from app.services.workflow_engine import (
    WorkflowContinueApplicationResult,
    WorkflowEngine,
    WorkflowTaskDecisionResult,
)


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


class QueueExecutor(TaskExecutor):
    def __init__(self, results: list[TaskExecutionResult]):
        self.results = list(results)
        self.calls: list[str] = []

    async def execute(self, task: Task) -> TaskExecutionResult:
        self.calls.append(task.title)
        if not self.results:
            raise AssertionError("Unexpected task execution.")

        result = self.results.pop(0)
        return TaskExecutionResult(
            success=result.success,
            output=result.output,
            error=result.error,
            outcome=result.outcome,
        )


class RecordingDecisionPolicy:
    def __init__(self, decision: TaskDecision | None = None):
        self.contexts = []
        self.decision = decision or TaskDecision(
            decision="stop",
            reason="Recorded decision.",
        )

    def decide(self, context):
        self.contexts.append(context)
        return self.decision


class WorkflowEngineExecutionTests(unittest.IsolatedAsyncioTestCase):
    def test_task_capability_defaults_to_none(self):
        task = Task(title="Do default work")
        self.assertIsNone(task.capability)
        self.assertEqual(task.inputs, {})

    async def test_successful_execution_marks_task_completed(self):
        task = Task(title="Do successful work")
        engine = WorkflowEngine(executor=SuccessfulExecutor())

        result = await engine.execute_task(task)

        self.assertIsInstance(result, TaskExecutionResult)
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

    async def test_execute_task_with_decision_returns_execution_result_and_decision(self):
        task = Task(title="Do successful work")
        project = Project(title="Complete project", tasks=[task])
        engine = WorkflowEngine(executor=SuccessfulExecutor())

        result = await engine.execute_task_with_decision(
            project=project,
            task=task,
        )

        self.assertIsInstance(result, WorkflowTaskDecisionResult)
        self.assertIsInstance(result.execution_result, TaskExecutionResult)
        self.assertEqual(result.decision.decision, "stop")

    async def test_completed_with_later_pending_task_decides_continue_only(self):
        current_task = Task(title="Current task")
        next_task = Task(title="Next task")
        project = Project(
            title="Complete project",
            tasks=[current_task, next_task],
        )
        executor = RecordingExecutor(
            TaskExecutionResult(success=True, output="Done"),
        )
        engine = WorkflowEngine(executor=executor)

        result = await engine.execute_task_with_decision(
            project=project,
            task=current_task,
        )

        self.assertEqual(result.decision.decision, "continue")
        self.assertEqual(executor.calls, 1)
        self.assertEqual(next_task.status, "pending")

    async def test_completed_with_no_later_pending_task_decides_stop(self):
        current_task = Task(title="Current task")
        completed_task = Task(title="Completed task", status="completed")
        project = Project(
            title="Complete project",
            tasks=[current_task, completed_task],
        )
        engine = WorkflowEngine(executor=SuccessfulExecutor())

        result = await engine.execute_task_with_decision(
            project=project,
            task=current_task,
        )

        self.assertEqual(result.decision.decision, "stop")

    async def test_failed_below_retry_bound_decides_retry_without_retrying(self):
        current_task = Task(title="Current task")
        project = Project(title="Complete project", tasks=[current_task])
        executor = RecordingExecutor(
            TaskExecutionResult(success=False, error="Failed once"),
        )
        engine = WorkflowEngine(executor=executor)

        result = await engine.execute_task_with_decision(
            project=project,
            task=current_task,
        )

        self.assertEqual(result.decision.decision, "retry")
        self.assertEqual(executor.calls, 1)
        self.assertEqual(current_task.retry_count, 0)

    async def test_retry_count_is_read_but_not_mutated(self):
        current_task = Task(title="Current task", retry_count=1)
        project = Project(title="Complete project", tasks=[current_task])
        engine = WorkflowEngine(executor=FailedExecutor())

        result = await engine.execute_task_with_decision(
            project=project,
            task=current_task,
        )

        self.assertEqual(result.decision.decision, "retry")
        self.assertEqual(current_task.retry_count, 1)

    async def test_authority_required_decides_request_authority(self):
        current_task = Task(title="Call customer", capability="phone_call")
        executor = RecordingExecutor(
            TaskExecutionResult(
                success=False,
                error="Authorization required.",
                outcome="authority_required",
            ),
        )
        capability_registry = CapabilityRegistry()
        capability_registry.register("phone_call", executor)
        project = Project(title="Complete project", tasks=[current_task])
        engine = WorkflowEngine(capability_registry=capability_registry)

        result = await engine.execute_task_with_decision(
            project=project,
            task=current_task,
        )

        self.assertEqual(result.decision.decision, "request_authority")
        self.assertEqual(executor.calls, 1)

    async def test_unsupported_capability_does_not_fallback_and_decides_replan(self):
        current_task = Task(
            title="Research market",
            capability="research",
        )
        next_task = Task(title="Synthesize results")
        project = Project(
            title="Complete project",
            tasks=[current_task, next_task],
        )
        executor = RecordingExecutor(
            TaskExecutionResult(success=True, output="Should not run"),
        )
        engine = WorkflowEngine(executor=executor)

        result = await engine.execute_task_with_decision(
            project=project,
            task=current_task,
        )

        self.assertEqual(executor.calls, 0)
        self.assertEqual(result.execution_result.observation.outcome, "unsupported")
        self.assertEqual(result.decision.decision, "replan")

    async def test_decision_context_remaining_tasks_are_sanitized_pending_and_ordered(self):
        before_task = Task(title="Before task")
        current_task = Task(
            title="Current task",
            inputs={
                "plan_id": "provider-plan",
                "confirm_token": "provider-token",
            },
        )
        completed_after_task = Task(
            title="Completed after task",
            status="completed",
        )
        first_pending_after_task = Task(
            title="First pending after task",
            inputs={"credentials": "not-for-context"},
        )
        failed_after_task = Task(title="Failed after task", status="failed")
        second_pending_after_task = Task(title="Second pending after task")
        project = Project(
            title="Complete project",
            tasks=[
                before_task,
                current_task,
                completed_after_task,
                first_pending_after_task,
                failed_after_task,
                second_pending_after_task,
            ],
        )
        decision_policy = RecordingDecisionPolicy()
        engine = WorkflowEngine(
            executor=SuccessfulExecutor(),
            decision_policy=decision_policy,
        )

        await engine.execute_task_with_decision(
            project=project,
            task=current_task,
        )

        context = decision_policy.contexts[0]
        self.assertEqual(
            [task.title for task in context.remaining_tasks],
            [
                "First pending after task",
                "Second pending after task",
            ],
        )
        self.assertEqual(context.project_goal, "Complete project")
        self.assertFalse(hasattr(context.current_task, "inputs"))
        for task_summary in context.remaining_tasks:
            self.assertFalse(hasattr(task_summary, "inputs"))
            self.assertFalse(hasattr(task_summary, "output"))
            self.assertFalse(hasattr(task_summary, "plan_id"))
            self.assertFalse(hasattr(task_summary, "confirm_token"))
            self.assertFalse(hasattr(task_summary, "credentials"))

    async def test_invalid_non_member_current_task_is_rejected_without_execution(self):
        current_task = Task(title="Current task")
        project = Project(title="Complete project", tasks=[])
        executor = RecordingExecutor(
            TaskExecutionResult(success=True, output="Should not run"),
        )
        engine = WorkflowEngine(executor=executor)

        with self.assertRaises(ValueError):
            await engine.execute_task_with_decision(
                project=project,
                task=current_task,
            )

        self.assertEqual(executor.calls, 0)

    async def test_replan_decision_does_not_call_planner_agent(self):
        current_task = Task(title="Current task", retry_count=2)
        next_task = Task(title="Next task")
        project = Project(
            title="Complete project",
            tasks=[current_task, next_task],
        )
        engine = WorkflowEngine(executor=FailedExecutor())

        with patch(
            "app.agents.planner_agent.PlannerAgent.run",
            new_callable=AsyncMock,
        ) as planner_run:
            result = await engine.execute_task_with_decision(
                project=project,
                task=current_task,
            )

        self.assertEqual(result.decision.decision, "replan")
        planner_run.assert_not_called()

    async def test_one_continue_applies_to_subsequent_reasoning_task(self):
        current_task = Task(title="Current task", capability="reasoning")
        next_task = Task(title="Next task", capability="reasoning")
        project = Project(
            title="Complete project",
            tasks=[current_task, next_task],
        )
        executor = QueueExecutor(
            [
                TaskExecutionResult(success=True, output="Current done"),
                TaskExecutionResult(success=True, output="Next done"),
            ],
        )
        engine = WorkflowEngine(executor=executor)

        result = await engine.execute_task_with_one_continue(
            project=project,
            task=current_task,
        )

        self.assertIsInstance(result, WorkflowContinueApplicationResult)
        self.assertTrue(result.continue_applied)
        self.assertEqual(result.continued_task, next_task)
        self.assertEqual(executor.calls, ["Current task", "Next task"])
        self.assertEqual(current_task.status, "completed")
        self.assertEqual(next_task.status, "completed")
        self.assertEqual(result.original.decision.decision, "continue")
        self.assertEqual(result.continued.decision.decision, "stop")

    async def test_second_continue_is_exposed_but_not_applied(self):
        current_task = Task(title="Current task", capability="reasoning")
        second_task = Task(title="Second task", capability="reasoning")
        third_task = Task(title="Third task", capability="reasoning")
        project = Project(
            title="Complete project",
            tasks=[current_task, second_task, third_task],
        )
        executor = QueueExecutor(
            [
                TaskExecutionResult(success=True, output="Current done"),
                TaskExecutionResult(success=True, output="Second done"),
                TaskExecutionResult(success=True, output="Should not run"),
            ],
        )
        engine = WorkflowEngine(executor=executor)

        result = await engine.execute_task_with_one_continue(
            project=project,
            task=current_task,
        )

        self.assertTrue(result.continue_applied)
        self.assertEqual(result.continued.decision.decision, "continue")
        self.assertEqual(executor.calls, ["Current task", "Second task"])
        self.assertEqual(third_task.status, "pending")

    async def test_phone_call_continuation_is_blocked_before_calle_execution(self):
        current_task = Task(title="Reason first", capability="reasoning")
        phone_task = Task(title="Call customer", capability="phone_call")
        project = Project(
            title="Complete project",
            tasks=[current_task, phone_task],
        )
        reasoning_executor = QueueExecutor(
            [TaskExecutionResult(success=True, output="Reasoned")],
        )
        capability_registry = CapabilityRegistry()
        capability_registry.register("reasoning", reasoning_executor)
        capability_registry.register("phone_call", CalleTaskExecutor())
        engine = WorkflowEngine(capability_registry=capability_registry)

        with patch.object(
            CalleTaskExecutor,
            "execute",
            new_callable=AsyncMock,
        ) as calle_execute:
            result = await engine.execute_task_with_one_continue(
                project=project,
                task=current_task,
            )

        self.assertFalse(result.continue_applied)
        self.assertEqual(result.continued_task, phone_task)
        self.assertIsNone(result.continued)
        self.assertIn("reasoning", result.continue_skipped_reason)
        self.assertEqual(reasoning_executor.calls, ["Reason first"])
        self.assertEqual(phone_task.status, "pending")
        calle_execute.assert_not_called()

    async def test_non_reasoning_capabilities_are_not_auto_continued(self):
        blocked_capabilities = [
            "research",
            "document_generation",
            "unknown",
        ]

        for capability in blocked_capabilities:
            with self.subTest(capability=capability):
                current_task = Task(title="Reason first", capability="reasoning")
                blocked_task = Task(
                    title=f"Blocked {capability}",
                    capability=capability,
                )
                project = Project(
                    title="Complete project",
                    tasks=[current_task, blocked_task],
                )
                executor = QueueExecutor(
                    [TaskExecutionResult(success=True, output="Reasoned")],
                )
                engine = WorkflowEngine(executor=executor)

                result = await engine.execute_task_with_one_continue(
                    project=project,
                    task=current_task,
                )

                self.assertFalse(result.continue_applied)
                self.assertEqual(result.continued_task, blocked_task)
                self.assertIsNone(result.continued)
                self.assertEqual(executor.calls, ["Reason first"])
                self.assertEqual(blocked_task.status, "pending")

    async def test_continue_with_no_next_pending_task_stops_safely(self):
        current_task = Task(title="Current task", capability="reasoning")
        project = Project(title="Complete project", tasks=[current_task])
        executor = QueueExecutor(
            [TaskExecutionResult(success=True, output="Done")],
        )
        decision_policy = RecordingDecisionPolicy(
            TaskDecision(
                decision="continue",
                reason="Forced continue for state-race coverage.",
            )
        )
        engine = WorkflowEngine(
            executor=executor,
            decision_policy=decision_policy,
        )

        result = await engine.execute_task_with_one_continue(
            project=project,
            task=current_task,
        )

        self.assertFalse(result.continue_applied)
        self.assertIsNone(result.continued_task)
        self.assertIsNone(result.continued)
        self.assertIn("No subsequent pending task", result.continue_skipped_reason)
        self.assertEqual(executor.calls, ["Current task"])

    async def test_second_task_failure_is_exposed_and_stops(self):
        current_task = Task(title="Current task", capability="reasoning")
        second_task = Task(title="Second task", capability="reasoning")
        third_task = Task(title="Third task", capability="reasoning")
        project = Project(
            title="Complete project",
            tasks=[current_task, second_task, third_task],
        )
        executor = QueueExecutor(
            [
                TaskExecutionResult(success=True, output="Current done"),
                TaskExecutionResult(success=False, error="Second failed"),
            ],
        )
        engine = WorkflowEngine(executor=executor)

        result = await engine.execute_task_with_one_continue(
            project=project,
            task=current_task,
        )

        self.assertTrue(result.continue_applied)
        self.assertFalse(result.continued.execution_result.success)
        self.assertEqual(
            result.continued.execution_result.observation.outcome,
            "failed",
        )
        self.assertEqual(result.continued.decision.decision, "retry")
        self.assertEqual(executor.calls, ["Current task", "Second task"])
        self.assertEqual(third_task.status, "pending")

    async def test_second_task_unsupported_is_exposed_and_stops(self):
        current_task = Task(title="Current task", capability="setup")
        second_task = Task(title="Second task", capability="reasoning")
        third_task = Task(title="Third task", capability="reasoning")
        project = Project(
            title="Complete project",
            tasks=[current_task, second_task, third_task],
        )
        setup_executor = QueueExecutor(
            [TaskExecutionResult(success=True, output="Current done")],
        )
        capability_registry = CapabilityRegistry()
        capability_registry.register("setup", setup_executor)
        engine = WorkflowEngine(capability_registry=capability_registry)

        result = await engine.execute_task_with_one_continue(
            project=project,
            task=current_task,
        )

        self.assertTrue(result.continue_applied)
        self.assertEqual(
            result.continued.execution_result.observation.outcome,
            "unsupported",
        )
        self.assertEqual(result.continued.decision.decision, "replan")
        self.assertEqual(setup_executor.calls, ["Current task"])
        self.assertEqual(third_task.status, "pending")

    async def test_second_task_authority_required_is_exposed_and_stops(self):
        current_task = Task(title="Current task", capability="setup")
        second_task = Task(title="Second task", capability="reasoning")
        third_task = Task(title="Third task", capability="reasoning")
        project = Project(
            title="Complete project",
            tasks=[current_task, second_task, third_task],
        )
        setup_executor = QueueExecutor(
            [TaskExecutionResult(success=True, output="Current done")],
        )
        reasoning_executor = QueueExecutor(
            [
                TaskExecutionResult(
                    success=False,
                    error="Authority required.",
                    outcome="authority_required",
                ),
            ],
        )
        capability_registry = CapabilityRegistry()
        capability_registry.register("setup", setup_executor)
        capability_registry.register("reasoning", reasoning_executor)
        engine = WorkflowEngine(capability_registry=capability_registry)

        result = await engine.execute_task_with_one_continue(
            project=project,
            task=current_task,
        )

        self.assertTrue(result.continue_applied)
        self.assertEqual(
            result.continued.execution_result.observation.outcome,
            "authority_required",
        )
        self.assertEqual(result.continued.decision.decision, "request_authority")
        self.assertEqual(reasoning_executor.calls, ["Second task"])
        self.assertEqual(third_task.status, "pending")

    async def test_retry_decision_is_not_applied_by_one_continue(self):
        current_task = Task(
            title="Current task",
            capability="reasoning",
            retry_count=1,
        )
        next_task = Task(title="Next task", capability="reasoning")
        project = Project(
            title="Complete project",
            tasks=[current_task, next_task],
        )
        executor = QueueExecutor(
            [TaskExecutionResult(success=False, error="Failed")],
        )
        engine = WorkflowEngine(executor=executor)

        result = await engine.execute_task_with_one_continue(
            project=project,
            task=current_task,
        )

        self.assertEqual(result.original.decision.decision, "retry")
        self.assertFalse(result.continue_applied)
        self.assertEqual(executor.calls, ["Current task"])
        self.assertEqual(current_task.retry_count, 1)
        self.assertEqual(next_task.status, "pending")

    async def test_replan_decision_is_not_applied_by_one_continue(self):
        current_task = Task(
            title="Current task",
            capability="reasoning",
            retry_count=2,
        )
        next_task = Task(title="Next task", capability="reasoning")
        project = Project(
            title="Complete project",
            tasks=[current_task, next_task],
        )
        executor = QueueExecutor(
            [TaskExecutionResult(success=False, error="Failed")],
        )
        engine = WorkflowEngine(executor=executor)

        with patch(
            "app.agents.planner_agent.PlannerAgent.run",
            new_callable=AsyncMock,
        ) as planner_run:
            result = await engine.execute_task_with_one_continue(
                project=project,
                task=current_task,
            )

        self.assertEqual(result.original.decision.decision, "replan")
        self.assertFalse(result.continue_applied)
        self.assertEqual(executor.calls, ["Current task"])
        self.assertEqual(next_task.status, "pending")
        planner_run.assert_not_called()

    async def test_request_authority_decision_is_not_applied_by_one_continue(self):
        current_task = Task(title="Current task", capability="reasoning")
        next_task = Task(title="Next task", capability="reasoning")
        project = Project(
            title="Complete project",
            tasks=[current_task, next_task],
        )
        executor = QueueExecutor(
            [
                TaskExecutionResult(
                    success=False,
                    error="Authority required.",
                    outcome="authority_required",
                ),
            ],
        )
        engine = WorkflowEngine(executor=executor)

        result = await engine.execute_task_with_one_continue(
            project=project,
            task=current_task,
        )

        self.assertEqual(result.original.decision.decision, "request_authority")
        self.assertFalse(result.continue_applied)
        self.assertEqual(executor.calls, ["Current task"])
        self.assertEqual(next_task.status, "pending")

    async def test_stop_decision_is_not_applied_by_one_continue(self):
        current_task = Task(title="Current task", capability="reasoning")
        project = Project(title="Complete project", tasks=[current_task])
        executor = QueueExecutor(
            [TaskExecutionResult(success=True, output="Done")],
        )
        engine = WorkflowEngine(executor=executor)

        result = await engine.execute_task_with_one_continue(
            project=project,
            task=current_task,
        )

        self.assertEqual(result.original.decision.decision, "stop")
        self.assertFalse(result.continue_applied)
        self.assertEqual(executor.calls, ["Current task"])


class StartupImportTests(unittest.TestCase):
    def test_app_startup_import(self):
        from app.main import app

        self.assertIsNotNone(app)
