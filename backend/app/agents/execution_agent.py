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

        execution_result = await workflow_engine.execute_task(current_task)

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
            "observation": (
                asdict(execution_result.observation)
                if execution_result.observation is not None
                else None
            ),
        }

    @property
    def name(self) -> str:
        return "execution"