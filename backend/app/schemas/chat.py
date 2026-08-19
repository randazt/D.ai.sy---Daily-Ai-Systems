from typing import Any, Literal, Optional, Union

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


# ----------------------------------------------------------------
# Typed public response contract for POST /chat
#
# These schemas document, for Swagger/OpenAPI, the externally
# observable response shapes already produced by ChatService today
# (conversation, planner, and execution agents). They are used ONLY
# to document the "responses" schema on the /chat route so that
# Swagger reflects the real public contract without changing the
# route's runtime behavior (the endpoint still returns the agent's
# raw dict; FastAPI does not re-validate/re-serialize through these
# models unless they are set as response_model).
#
# These schemas intentionally mirror only fields already returned
# today. They MUST NOT include provider/runtime internals such as
# CALL-E confirmation tokens, ADK runner/session identifiers,
# CapabilityRegistry internals, or environment configuration.
# ----------------------------------------------------------------


class PlannerTaskSchema(BaseModel):
    title: str
    description: str
    capability: Optional[str] = None
    inputs: dict[str, Any] = {}
    status: str
    output: str = ""


class PlannerProjectSchema(BaseModel):
    id: str
    title: str
    description: str
    status: str
    tasks: list[PlannerTaskSchema]


class PlannerResponse(BaseModel):
    agent: Literal["planner"]
    goal: str
    knowledge: list[str]
    knowledge_preview: str
    project: PlannerProjectSchema
    plan: list[str]


class AgentStatusMessageResponse(BaseModel):
    """
    Shared shape for planner/execution status-only responses, such as
    "No project exists." or "All tasks are complete."
    """

    agent: Literal["planner", "execution"]
    status: str
    message: str


class ExecutionProjectSchema(BaseModel):
    title: str
    description: str
    status: str


class TaskObservationSchema(BaseModel):
    """
    Mirrors app.models.project.TaskObservation. Deliberately excludes
    any provider/executor identity per the D.A.I.S.Y. observation
    contract (see execution observation milestone).
    """

    task_title: str
    capability: str
    status: str
    success: bool
    outcome: str
    summary: str
    error: str = ""


class ExecutionCurrentTaskSchema(BaseModel):
    title: str
    description: str
    capability: Optional[str] = None
    inputs: dict[str, Any] = {}
    status: str
    output: str
    observation: Optional[TaskObservationSchema] = None


class ExecutionResultSchema(BaseModel):
    success: bool
    output: str
    error: str


class ExecutionResponse(BaseModel):
    agent: Literal["execution"]
    status: str
    project: ExecutionProjectSchema
    current_task: ExecutionCurrentTaskSchema
    execution: ExecutionResultSchema
    observation: Optional[TaskObservationSchema] = None


class ConversationResponse(BaseModel):
    reply: Optional[str] = None
    error: Optional[str] = None


ChatEndpointResponse = Union[
    PlannerResponse,
    ExecutionResponse,
    AgentStatusMessageResponse,
    ConversationResponse,
]
