import unittest
from unittest.mock import AsyncMock, patch

from app.agents.execution_agent import ExecutionAgent
from app.agents.planner_agent import PlannerAgent, classify_task_capability
from app.models.project import Task
from app.services.project_service import project_service
from app.services.task_executor import TaskExecutionResult


class TaskCapabilityClassifierTests(unittest.TestCase):
    def test_reasoning_example_classifies_as_reasoning(self):
        capability = classify_task_capability(
            "Analyze findings and decide next actions",
        )
        self.assertEqual(capability, "reasoning")

    def test_research_example_classifies_as_research(self):
        capability = classify_task_capability(
            "Research customer market needs",
        )
        self.assertEqual(capability, "research")

    def test_phone_call_example_classifies_as_phone_call(self):
        capability = classify_task_capability(
            "Call and interview customers by phone",
        )
        self.assertEqual(capability, "phone_call")

    def test_document_generation_example_classifies_as_document_generation(self):
        capability = classify_task_capability(
            "Create a final summary report deliverable",
        )
        self.assertEqual(capability, "document_generation")

    def test_phone_call_precedence_over_research_language(self):
        capability = classify_task_capability(
            "Research customers by calling them",
        )
        self.assertEqual(capability, "phone_call")

    def test_call_customers_for_interviews_classifies_as_phone_call(self):
        capability = classify_task_capability(
            "Call customers for interviews",
        )
        self.assertEqual(capability, "phone_call")

    def test_callback_handler_does_not_classify_as_phone_call(self):
        capability = classify_task_capability(
            "Create a callback handler",
        )
        self.assertEqual(capability, "reasoning")

    def test_recall_previous_findings_does_not_classify_as_phone_call(self):
        capability = classify_task_capability(
            "Recall previous findings",
        )
        self.assertEqual(capability, "reasoning")

    def test_unknown_task_defaults_to_reasoning(self):
        capability = classify_task_capability("Coordinate next step")
        self.assertEqual(capability, "reasoning")


class PlannerAndExecutionCapabilityTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        project_service._projects.clear()

    async def test_planner_created_tasks_receive_capability(self):
        planner = PlannerAgent()
        ai_reply = "\n".join(
            [
                "1. Research target segments",
                "2. Call and interview customers by phone",
                "3. Create final summary report",
                "4. Synthesize findings and decide priorities",
            ]
        )

        with patch(
            "app.agents.planner_agent.knowledge_retriever.search",
            return_value=[],
        ), patch(
            "app.agents.planner_agent.gemini_service.generate",
            return_value={"reply": ai_reply},
        ):
            result = await planner.run("Plan customer validation")

        task_capabilities = [
            task["capability"] for task in result["project"]["tasks"]
        ]
        self.assertEqual(
            task_capabilities,
            [
                "research",
                "phone_call",
                "document_generation",
                "reasoning",
            ],
        )

    async def test_execution_response_exposes_task_capability(self):
        project_id = project_service.create_project("Plan outreach")
        project = project_service.get_project(project_id)
        project.tasks.append(
            Task(
                title="Call interview candidates",
                capability="phone_call",
            )
        )

        async def fake_execute(task):
            task.status = "completed"
            task.output = "Executed capability task"
            return TaskExecutionResult(
                success=True,
                output="Executed capability task",
            )

        with patch(
            "app.agents.execution_agent.workflow_engine.execute_task",
            new=AsyncMock(side_effect=fake_execute),
        ):
            result = await ExecutionAgent().run("Execute the current project.")

        self.assertEqual(
            result["current_task"]["capability"],
            "phone_call",
        )
