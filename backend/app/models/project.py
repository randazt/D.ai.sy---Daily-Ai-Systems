from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class Task:
    """
    Represents a single task within a project.
    """

    title: str
    description: str = ""
    status: str = "pending"
    output: str = ""


@dataclass
class Project:
    """
    Represents a user project managed by D.AI.SY.
    """

    title: str
    description: str = ""
    status: str = "active"
    tasks: List[Task] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)