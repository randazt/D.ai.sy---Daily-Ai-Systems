from typing import Dict, List
from uuid import uuid4

from app.models.project import Project


class ProjectService:
    """
    Manages D.AI.SY projects.

    This is currently an in-memory implementation.
    Later it will be backed by Firestore without changing
    the public interface.
    """

    def __init__(self):
        self._projects: Dict[str, Project] = {}

    def create_project(self, title: str, description: str = "") -> str:
        project_id = str(uuid4())

        project = Project(
            title=title,
            description=description,
        )

        self._projects[project_id] = project

        return project_id

    def get_project(self, project_id: str):
        return self._projects.get(project_id)

    def list_projects(self) -> List[Project]:
        return list(self._projects.values())

    def delete_project(self, project_id: str):
        if project_id in self._projects:
            del self._projects[project_id]

    def get_latest_project(self):
        if not self._projects:
            return None

        return list(self._projects.values())[-1]


# Singleton
project_service = ProjectService()