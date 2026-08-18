import re

from app.agents.base_agent import BaseAgent
from app.models.project import Task
from app.knowledge.knowledge_service import knowledge_service
from app.knowledge.retriever import knowledge_retriever
from app.services.gemini_service import gemini_service
from app.services.project_service import project_service


PHONE_CALL_KEYWORDS = (
    "call",
    "call customers",
    "call customer",
    "phone call",
    "phone calls",
    "telephone call",
    "telephone calls",
    "calling customers",
    "calling customer",
    "calling",
    "dial",
    "interview by phone",
    "phone interview",
    "phone interviews",
)

DOCUMENT_GENERATION_KEYWORDS = (
    "report",
    "reports",
    "document",
    "documents",
    "summary",
    "summaries",
    "deliverable",
    "deliverables",
    "writeup",
)

RESEARCH_KEYWORDS = (
    "research",
    "investigate",
    "investigation",
    "gather",
    "collect",
    "market analysis",
    "market research",
    "discovery",
)


def classify_task_capability(task_text: str) -> str:
    normalized_text = " ".join(
        re.sub(r"[^a-z0-9]+", " ", task_text.lower()).split()
    )

    padded_text = f" {normalized_text} "

    if any(f" {keyword} " in padded_text for keyword in PHONE_CALL_KEYWORDS):
        return "phone_call"

    if any(
        f" {keyword} " in padded_text
        for keyword in DOCUMENT_GENERATION_KEYWORDS
    ):
        return "document_generation"

    if any(f" {keyword} " in padded_text for keyword in RESEARCH_KEYWORDS):
        return "research"

    return "reasoning"


class PlannerAgent(BaseAgent):
    """
    Converts a user's goal into a structured execution plan.

    Uses:
    - Local knowledge documents
    - Knowledge retrieval
    - Gemini (when available)
    - Safe fallback planning
    - ProjectService for project state
    """

    @property
    def name(self) -> str:
        return "planner"

    async def run(self, message: str):

        # ----------------------------------------
        # Parse the user goal
        # ----------------------------------------

        title = message.replace("/plan", "").strip()

        # ----------------------------------------
        # Retrieve relevant knowledge
        # ----------------------------------------

        retrieved = knowledge_retriever.search(title)

        knowledge_documents = [
            item["file"]
            for item in retrieved
        ]

        knowledge_text = ""

        if retrieved:
            best_document = retrieved[0]["file"]

            knowledge_text = (
                knowledge_service.read_document(best_document)
                or ""
            )

        # ----------------------------------------
        # Build Gemini prompt
        # ----------------------------------------

        prompt = f"""
You are D.A.I.S.Y.'s Planning Agent.

User Goal:
{title}

Relevant Knowledge:
{knowledge_text}

Create a concise execution plan.

Requirements:

- 4 to 6 numbered steps
- Each step should be actionable
- Do not include explanations
- Return only the numbered plan
"""

        # ----------------------------------------
        # Ask Gemini
        # ----------------------------------------

        ai_plan = []

        try:
            ai_response = gemini_service.generate(prompt)

            if isinstance(ai_response, dict):
                reply = ai_response.get("reply")

                if reply:
                    ai_plan = [
                        line.strip().lstrip("0123456789.- ")
                        for line in reply.splitlines()
                        if line.strip()
                    ]

        except Exception:
            ai_plan = []

        # ----------------------------------------
        # Fallback plan
        # ----------------------------------------

        if not ai_plan:
            ai_plan = [
                f"Understand the goal: {title}",
                "Break the goal into smaller tasks",
                "Identify required resources",
                "Implement the solution",
                "Test and validate the result",
            ]

        # ----------------------------------------
        # Convert plan to Task objects
        # ----------------------------------------

        tasks = [
            Task(
                title=item,
                capability=classify_task_capability(item),
            )
            for item in ai_plan
        ]

        # ----------------------------------------
        # Create and persist the Project
        # ----------------------------------------

        project_id = project_service.create_project(
            title=title
        )

        project = project_service.get_project(project_id)

        if project is None:
            return {
                "agent": "planner",
                "status": "error",
                "message": "Project could not be created.",
            }

        project.tasks.extend(tasks)

        # ----------------------------------------
        # Return structured response
        # ----------------------------------------

        return {
            "agent": "planner",
            "goal": title,
            "knowledge": knowledge_documents,
            "knowledge_preview": knowledge_text[:500],
            "project": {
                "id": project_id,
                "title": project.title,
                "description": project.description,
                "status": project.status,
                "tasks": [
                    {
                        "title": task.title,
                        "description": task.description,
                        "capability": task.capability,
                        "status": task.status,
                    }
                    for task in project.tasks
                ],
            },
            "plan": [
                task.title
                for task in project.tasks
            ],
        }