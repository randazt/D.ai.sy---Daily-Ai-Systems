import unittest
import json
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
        for task in result["project"]["tasks"]:
            self.assertIsInstance(task["inputs"], dict)

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


class PlannerSemanticInputsTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        project_service._projects.clear()

    async def test_existing_planning_prompt_still_creates_project_and_tasks(self):
        planner = PlannerAgent()
        ai_reply = "\n".join(
            [
                "1. Research customer segments",
                "2. Synthesize findings",
                "3. Draft recommendations",
                "4. Present outcomes",
            ]
        )

        with patch(
            "app.agents.planner_agent.knowledge_retriever.search",
            return_value=[],
        ), patch(
            "app.agents.planner_agent.gemini_service.generate",
            return_value={"reply": ai_reply},
        ):
            result = await planner.run(
                "Plan a project to research three potential customer groups for D.AI.S.Y."
            )

        self.assertIn("project", result)
        self.assertGreaterEqual(len(result["project"]["tasks"]), 1)

    async def test_structured_reasoning_task_keeps_empty_inputs(self):
        planner = PlannerAgent()
        ai_reply = json.dumps(
            {
                "tasks": [
                    {
                        "title": "Analyze market signal patterns",
                        "description": "Review market notes",
                        "capability": "reasoning",
                        "inputs": {"plan_id": "blocked"},
                    }
                ]
            }
        )

        with patch(
            "app.agents.planner_agent.knowledge_retriever.search",
            return_value=[],
        ), patch(
            "app.agents.planner_agent.gemini_service.generate",
            return_value={"reply": ai_reply},
        ):
            result = await planner.run("Plan market analysis steps")

        task = result["project"]["tasks"][0]
        self.assertEqual(task["capability"], "reasoning")
        self.assertEqual(task["inputs"], {})

    async def test_phone_call_objective_is_generated_when_missing(self):
        planner = PlannerAgent()
        ai_reply = json.dumps(
            {
                "tasks": [
                    {
                        "title": "Call potential customer",
                        "description": "Interview about inbound lead-management problems",
                        "capability": "phone_call",
                        "inputs": {},
                    }
                ]
            }
        )

        with patch(
            "app.agents.planner_agent.knowledge_retriever.search",
            return_value=[],
        ), patch(
            "app.agents.planner_agent.gemini_service.generate",
            return_value={"reply": ai_reply},
        ):
            result = await planner.run("Plan customer discovery calls")

        inputs = result["project"]["tasks"][0]["inputs"]
        self.assertIn("objective", inputs)
        self.assertEqual(
            inputs["objective"],
            "Interview about inbound lead-management problems",
        )

    async def test_explicit_user_destination_is_propagated(self):
        planner = PlannerAgent()
        ai_reply = json.dumps(
            {
                "tasks": [
                    {
                        "title": "Call potential customer",
                        "description": "Run interview",
                        "capability": "phone_call",
                        "inputs": {"objective": "Run interview"},
                    }
                ]
            }
        )

        with patch(
            "app.agents.planner_agent.knowledge_retriever.search",
            return_value=[],
        ), patch(
            "app.agents.planner_agent.gemini_service.generate",
            return_value={"reply": ai_reply},
        ):
            result = await planner.run(
                "Plan a project that includes calling +15550000000 to interview a potential customer."
            )

        inputs = result["project"]["tasks"][0]["inputs"]
        self.assertEqual(inputs.get("destination"), "+15550000000")

    async def test_user_no_destination_model_invents_destination_it_is_ignored(self):
        planner = PlannerAgent()
        ai_reply = json.dumps(
            {
                "tasks": [
                    {
                        "title": "Call potential customer",
                        "description": "Run interview",
                        "capability": "phone_call",
                        "inputs": {
                            "destination": "+15551112222",
                            "objective": "Run interview",
                        },
                    }
                ]
            }
        )

        with patch(
            "app.agents.planner_agent.knowledge_retriever.search",
            return_value=[],
        ), patch(
            "app.agents.planner_agent.gemini_service.generate",
            return_value={"reply": ai_reply},
        ):
            result = await planner.run("Plan customer interview calls")

        inputs = result["project"]["tasks"][0]["inputs"]
        self.assertNotIn("destination", inputs)

    async def test_user_destination_overrides_model_destination(self):
        planner = PlannerAgent()
        ai_reply = json.dumps(
            {
                "tasks": [
                    {
                        "title": "Call potential customer",
                        "description": "Run interview",
                        "capability": "phone_call",
                        "inputs": {
                            "destination": "+15551112222",
                            "objective": "Run interview",
                        },
                    }
                ]
            }
        )

        with patch(
            "app.agents.planner_agent.knowledge_retriever.search",
            return_value=[],
        ), patch(
            "app.agents.planner_agent.gemini_service.generate",
            return_value={"reply": ai_reply},
        ):
            result = await planner.run(
                "Plan a project that includes calling +15550000000 to interview a potential customer."
            )

        inputs = result["project"]["tasks"][0]["inputs"]
        self.assertEqual(inputs.get("destination"), "+15550000000")

    async def test_user_destination_is_used_when_model_omits_destination(self):
        planner = PlannerAgent()
        ai_reply = json.dumps(
            {
                "tasks": [
                    {
                        "title": "Call potential customer",
                        "description": "Run interview",
                        "capability": "phone_call",
                        "inputs": {"objective": "Run interview"},
                    }
                ]
            }
        )

        with patch(
            "app.agents.planner_agent.knowledge_retriever.search",
            return_value=[],
        ), patch(
            "app.agents.planner_agent.gemini_service.generate",
            return_value={"reply": ai_reply},
        ):
            result = await planner.run(
                "Plan a project that includes calling +15550000000 to interview a potential customer."
            )

        inputs = result["project"]["tasks"][0]["inputs"]
        self.assertEqual(inputs.get("destination"), "+15550000000")

    async def test_model_phone_numbers_in_text_do_not_set_destination_without_user_number(self):
        planner = PlannerAgent()
        ai_reply = json.dumps(
            {
                "tasks": [
                    {
                        "title": "Call +15551112222 and ask about onboarding",
                        "description": "Interview +15553334444 for fit",
                        "capability": "phone_call",
                        "inputs": {
                            "questions": [
                                "What blocked your pipeline at +15556667777?"
                            ],
                        },
                    }
                ]
            }
        )

        with patch(
            "app.agents.planner_agent.knowledge_retriever.search",
            return_value=[],
        ), patch(
            "app.agents.planner_agent.gemini_service.generate",
            return_value={"reply": ai_reply},
        ):
            result = await planner.run("Plan customer interview calls")

        inputs = result["project"]["tasks"][0]["inputs"]
        self.assertNotIn("destination", inputs)

    async def test_missing_destination_is_not_fabricated(self):
        planner = PlannerAgent()
        ai_reply = json.dumps(
            {
                "tasks": [
                    {
                        "title": "Call potential customer",
                        "description": "Run interview",
                        "capability": "phone_call",
                        "inputs": {},
                    }
                ]
            }
        )

        with patch(
            "app.agents.planner_agent.knowledge_retriever.search",
            return_value=[],
        ), patch(
            "app.agents.planner_agent.gemini_service.generate",
            return_value={"reply": ai_reply},
        ):
            result = await planner.run("Plan customer interview calls")

        inputs = result["project"]["tasks"][0]["inputs"]
        self.assertNotIn("destination", inputs)

    async def test_phone_call_questions_language_region_are_sanitized(self):
        planner = PlannerAgent()
        ai_reply = json.dumps(
            {
                "tasks": [
                    {
                        "title": "Call customer",
                        "description": "Interview user",
                        "capability": "phone_call",
                        "inputs": {
                            "questions": ["What hurts most?", "  ", 42, "Desired outcomes?"],
                            "language": " English ",
                            "region": " US-East ",
                        },
                    }
                ]
            }
        )

        with patch(
            "app.agents.planner_agent.knowledge_retriever.search",
            return_value=[],
        ), patch(
            "app.agents.planner_agent.gemini_service.generate",
            return_value={"reply": ai_reply},
        ):
            result = await planner.run("Plan customer interview calls")

        inputs = result["project"]["tasks"][0]["inputs"]
        self.assertEqual(inputs["questions"], ["What hurts most?", "Desired outcomes?"])
        self.assertEqual(inputs["language"], "English")
        self.assertEqual(inputs["region"], "US-East")

    async def test_provider_specific_keys_are_stripped_from_phone_call_inputs(self):
        planner = PlannerAgent()
        ai_reply = json.dumps(
            {
                "tasks": [
                    {
                        "title": "Call customer",
                        "description": "Interview user",
                        "capability": "phone_call",
                        "inputs": {
                            "plan_id": "abc",
                            "confirm_token": "xyz",
                            "to_phones": ["+15551111111"],
                            "objective": "Interview user",
                        },
                    }
                ]
            }
        )

        with patch(
            "app.agents.planner_agent.knowledge_retriever.search",
            return_value=[],
        ), patch(
            "app.agents.planner_agent.gemini_service.generate",
            return_value={"reply": ai_reply},
        ):
            result = await planner.run("Plan customer interview calls")

        inputs = result["project"]["tasks"][0]["inputs"]
        self.assertNotIn("plan_id", inputs)
        self.assertNotIn("confirm_token", inputs)
        self.assertNotIn("to_phones", inputs)
        self.assertEqual(inputs["objective"], "Interview user")

    async def test_malformed_structured_output_falls_back_safely(self):
        planner = PlannerAgent()
        malformed = '{"tasks": [{"title": "Call customer", "capability": "phone_call",}'

        with patch(
            "app.agents.planner_agent.knowledge_retriever.search",
            return_value=[],
        ), patch(
            "app.agents.planner_agent.gemini_service.generate",
            return_value={"reply": malformed},
        ):
            result = await planner.run("Plan outreach work")

        self.assertGreaterEqual(len(result["project"]["tasks"]), 1)
        for task in result["project"]["tasks"]:
            self.assertIsInstance(task["inputs"], dict)

    async def test_unknown_capability_falls_back_to_existing_classifier_policy(self):
        planner = PlannerAgent()
        ai_reply = json.dumps(
            {
                "tasks": [
                    {
                        "title": "Call and interview customers by phone",
                        "description": "Collect discovery data",
                        "capability": "unknown_capability",
                        "inputs": {"objective": "Collect discovery data"},
                    }
                ]
            }
        )

        with patch(
            "app.agents.planner_agent.knowledge_retriever.search",
            return_value=[],
        ), patch(
            "app.agents.planner_agent.gemini_service.generate",
            return_value={"reply": ai_reply},
        ):
            result = await planner.run("Plan outreach work")

        task = result["project"]["tasks"][0]
        self.assertEqual(task["capability"], "phone_call")

    async def test_end_to_end_semantic_phone_call_inputs_without_provider_keys(self):
        planner = PlannerAgent()
        ai_reply = json.dumps(
            {
                "tasks": [
                    {
                        "title": "Call the potential customer",
                        "description": "Interview them about lead-management problems",
                        "capability": "phone_call",
                        "inputs": {
                            "plan_id": "provider-internal",
                            "confirm_token": "provider-token",
                            "to_phones": ["+15559999999"],
                        },
                    }
                ]
            }
        )

        with patch(
            "app.agents.planner_agent.knowledge_retriever.search",
            return_value=[],
        ), patch(
            "app.agents.planner_agent.gemini_service.generate",
            return_value={"reply": ai_reply},
        ):
            result = await planner.run(
                "Plan a project that includes calling +15550000000 to interview a potential customer about their lead-management problems."
            )

        task = result["project"]["tasks"][0]
        self.assertEqual(task["capability"], "phone_call")
        self.assertEqual(task["inputs"].get("destination"), "+15550000000")
        self.assertIn("objective", task["inputs"])
        self.assertNotIn("plan_id", task["inputs"])
        self.assertNotIn("confirm_token", task["inputs"])
        self.assertNotIn("to_phones", task["inputs"])
