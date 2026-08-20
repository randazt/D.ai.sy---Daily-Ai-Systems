from dataclasses import asdict

from app.agents.base_agent import BaseAgent
from app.services.project_service import project_service
from app.services.workflow_engine import workflow_engine


class ExecutionAgent(BaseAgent):
    """
    Executes the latest project created by the PlannerAgent.
    """

    async def run(self, message: str):

        project = project_service.get_latest_project()

        if project is None:
            return {
                "agent": "execution",
                "status": "error",
                "message": "No project exists."
            }

        # Find the first pending task
        current_task = None

        for task in project.tasks:
            if task.status == "pending":
                current_task = task
                break

        if current_task is None:
            return {
                "agent": "execution",
                "status": "completed",
                "message": "All tasks are complete."
            }

        workflow_result = await workflow_engine.execute_task_with_one_continue(
            project=project,
            task=current_task,
        )
        original_result = workflow_result.original
        execution_result = original_result.execution_result

        return {
            "agent": "execution",
            "status": "completed" if execution_result.success else "failed",
            "project": {
                "title": project.title,
                "description": project.description,
                "status": project.status,
            },
            "current_task": {
                "title": current_task.title,
                "description": current_task.description,
                "capability": current_task.capability,
                "status": current_task.status,
                "output": current_task.output,
            },
            "execution": {
                "success": execution_result.success,
                "output": execution_result.output,
                "error": execution_result.error,
            },
            "decision": asdict(original_result.decision),
            "observation": (
                asdict(execution_result.observation)
                if execution_result.observation is not None
                else None
            ),
            "continuation": self._build_continuation_response(workflow_result),
        }

    @property
    def name(self) -> str:
        return "execution"

    @classmethod
    def _build_continuation_response(cls, workflow_result):
        continued = workflow_result.continued
        continued_execution = (
            continued.execution_result if continued is not None else None
        )

        return {
            "continue_applied": workflow_result.continue_applied,
            "continue_skipped_reason": workflow_result.continue_skipped_reason,
            "continued_task": (
                cls._build_task_response(workflow_result.continued_task)
                if workflow_result.continued_task is not None
                else None
            ),
            "continued_execution": (
                {
                    "success": continued_execution.success,
                    "output": continued_execution.output,
                    "error": continued_execution.error,
                }
                if continued_execution is not None
                else None
            ),
            "continued_observation": (
                asdict(continued_execution.observation)
                if continued_execution is not None
                and continued_execution.observation is not None
                else None
            ),
            "continued_decision": (
                asdict(continued.decision) if continued is not None else None
            ),
        }

    @staticmethod
    def _build_task_response(task):
        return {
            "title": task.title,
            "description": task.description,
            "capability": task.capability,
            "status": task.status,
            "output": task.output,
        }
