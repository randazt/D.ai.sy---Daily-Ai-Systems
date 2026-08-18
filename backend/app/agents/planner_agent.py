import re
import json

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

SUPPORTED_CAPABILITIES = {
    "reasoning",
    "research",
    "phone_call",
    "document_generation",
}

PROVIDER_SPECIFIC_INPUT_KEYS = {
    "plan_id",
    "confirm_token",
    "to_phones",
    "tool_name",
    "tool",
    "call_e_tool",
    "call_e_command",
    "calle_command",
    "provider",
}

PHONE_CALL_ALLOWED_INPUT_KEYS = {
    "destination",
    "objective",
    "questions",
    "language",
    "region",
}

PHONE_NUMBER_PATTERN = re.compile(r"(\+?[0-9][0-9\-\s().]{8,}[0-9])")


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

Create a concise execution plan and return JSON only.

Requirements:

- Return a JSON object with this shape:
{{
  "tasks": [
    {{
      "title": "string",
      "description": "string",
      "capability": "reasoning|research|phone_call|document_generation",
      "inputs": {{
        "destination": "string (optional, only if user provided it)",
        "objective": "string (optional)",
        "questions": ["string", "..."],
        "language": "string (optional)",
        "region": "string (optional)"
      }}
    }}
  ]
}}
- Produce 4 to 6 tasks.
- Do not include provider-specific keys such as plan_id, confirm_token, to_phones, or CLI/SDK/tool names.
- Do not invent phone numbers, credentials, or secrets.
"""

        # ----------------------------------------
        # Ask Gemini
        # ----------------------------------------

        ai_reply = ""

        try:
            ai_response = gemini_service.generate(prompt)

            if isinstance(ai_response, dict):
                reply = ai_response.get("reply")

                if isinstance(reply, str):
                    ai_reply = reply

        except Exception:
            ai_reply = ""

        # ----------------------------------------
        # Fallback plan
        # ----------------------------------------

        user_destination = self._extract_user_destination(title)

        tasks = self._build_tasks_from_structured_reply(
            ai_reply,
            goal=title,
            user_destination=user_destination,
        )

        if not tasks:
            ai_plan = self._parse_numbered_plan(ai_reply)
            if not ai_plan:
                ai_plan = [
                f"Understand the goal: {title}",
                "Break the goal into smaller tasks",
                "Identify required resources",
                "Implement the solution",
                "Test and validate the result",
                ]

            tasks = [
                self._build_fallback_task(
                    plan_item=item,
                    goal=title,
                    user_destination=user_destination,
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
                        "inputs": task.inputs,
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

    @staticmethod
    def _parse_numbered_plan(reply: str) -> list[str]:
        if not reply:
            return []

        return [
            line.strip().lstrip("0123456789.- ")
            for line in reply.splitlines()
            if line.strip()
        ]

    @classmethod
    def _build_tasks_from_structured_reply(
        cls,
        reply: str,
        *,
        goal: str,
        user_destination: str | None,
    ) -> list[Task]:
        structured_tasks = cls._extract_structured_tasks(reply)
        if not structured_tasks:
            return []

        tasks: list[Task] = []
        for raw_task in structured_tasks:
            task = cls._build_task_from_structured_item(
                raw_task,
                goal=goal,
                user_destination=user_destination,
            )
            if task is not None:
                tasks.append(task)

        return tasks

    @classmethod
    def _build_task_from_structured_item(
        cls,
        raw_task: object,
        *,
        goal: str,
        user_destination: str | None,
    ) -> Task | None:
        if not isinstance(raw_task, dict):
            return None

        title = cls._clean_string(raw_task.get("title"))
        if not title:
            return None

        description = cls._clean_string(raw_task.get("description")) or ""
        capability = cls._normalize_task_capability(
            raw_task.get("capability"),
            title=title,
            description=description,
        )
        raw_inputs = raw_task.get("inputs")
        inputs = cls._sanitize_task_inputs(
            capability=capability,
            raw_inputs=raw_inputs,
            goal=goal,
            title=title,
            description=description,
            user_destination=user_destination,
        )

        return Task(
            title=title,
            description=description,
            capability=capability,
            inputs=inputs,
        )

    @classmethod
    def _build_fallback_task(
        cls,
        *,
        plan_item: str,
        goal: str,
        user_destination: str | None,
    ) -> Task:
        title = plan_item.strip()
        capability = classify_task_capability(title)
        inputs = cls._sanitize_task_inputs(
            capability=capability,
            raw_inputs={},
            goal=goal,
            title=title,
            description="",
            user_destination=user_destination,
        )
        return Task(
            title=title,
            capability=capability,
            inputs=inputs,
        )

    @classmethod
    def _extract_structured_tasks(cls, reply: str) -> list[object]:
        if not reply:
            return []

        payload = cls._parse_json_payload(reply)
        if payload is None:
            return []

        if isinstance(payload, dict):
            tasks = payload.get("tasks")
            return tasks if isinstance(tasks, list) else []

        if isinstance(payload, list):
            return payload

        return []

    @staticmethod
    def _parse_json_payload(reply: str) -> object | None:
        if not isinstance(reply, str):
            return None

        text = reply.strip()
        if not text:
            return None

        fenced_match = re.search(r"```(?:json)?\s*(.*?)```", text, re.IGNORECASE | re.DOTALL)
        candidates = [fenced_match.group(1).strip()] if fenced_match else []
        candidates.append(text)

        start_indices = [index for index in (text.find("{"), text.find("[")) if index != -1]
        if start_indices:
            start_index = min(start_indices)
            candidates.append(text[start_index:])

        for candidate in candidates:
            if not candidate:
                continue
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue

        return None

    @classmethod
    def _normalize_task_capability(
        cls,
        capability: object,
        *,
        title: str,
        description: str,
    ) -> str:
        normalized = cls._clean_string(capability)
        if normalized:
            normalized = normalized.lower()
            if normalized in SUPPORTED_CAPABILITIES:
                return normalized

        return classify_task_capability(f"{title} {description}".strip())

    @classmethod
    def _sanitize_task_inputs(
        cls,
        *,
        capability: str,
        raw_inputs: object,
        goal: str,
        title: str,
        description: str,
        user_destination: str | None,
    ) -> dict[str, object]:
        if capability != "phone_call":
            return {}

        input_map = raw_inputs if isinstance(raw_inputs, dict) else {}
        safe_inputs: dict[str, object] = {}

        normalized_keys = {
            str(key).strip().lower()
            for key in input_map.keys()
            if isinstance(key, str)
        }
        if any(key in PROVIDER_SPECIFIC_INPUT_KEYS for key in normalized_keys):
            input_map = {
                key: value
                for key, value in input_map.items()
                if isinstance(key, str)
                and key.strip().lower() not in PROVIDER_SPECIFIC_INPUT_KEYS
            }

        allowed_map = {
            key: value
            for key, value in input_map.items()
            if isinstance(key, str)
            and key.strip().lower() in PHONE_CALL_ALLOWED_INPUT_KEYS
        }

        if user_destination:
            safe_inputs["destination"] = user_destination

        objective = cls._clean_string(allowed_map.get("objective"))
        if objective:
            safe_inputs["objective"] = objective
        else:
            fallback_objective = cls._derive_phone_objective(
                goal=goal,
                title=title,
                description=description,
            )
            if fallback_objective:
                safe_inputs["objective"] = fallback_objective

        questions = cls._sanitize_questions(allowed_map.get("questions"))
        if questions:
            safe_inputs["questions"] = questions

        language = cls._clean_string(allowed_map.get("language"))
        if language:
            safe_inputs["language"] = language

        region = cls._clean_string(allowed_map.get("region"))
        if region:
            safe_inputs["region"] = region

        return safe_inputs

    @staticmethod
    def _derive_phone_objective(*, goal: str, title: str, description: str) -> str:
        for candidate in (description, title, goal):
            value = candidate.strip()
            if value:
                return value
        return ""

    @staticmethod
    def _sanitize_questions(value: object) -> list[str]:
        if not isinstance(value, list):
            return []

        sanitized: list[str] = []
        for item in value:
            if isinstance(item, str):
                question = item.strip()
                if question:
                    sanitized.append(question)

        return sanitized

    @staticmethod
    def _clean_string(value: object) -> str:
        if isinstance(value, str):
            cleaned = value.strip()
            if cleaned:
                return cleaned
        return ""

    @classmethod
    def _extract_user_destination(cls, goal: str) -> str | None:
        match = PHONE_NUMBER_PATTERN.search(goal)
        if not match:
            return None

        candidate = match.group(1).strip()
        digits = re.sub(r"[^0-9]", "", candidate)
        if len(digits) < 10 or len(digits) > 15:
            return None

        return f"+{digits}" if candidate.startswith("+") else digits