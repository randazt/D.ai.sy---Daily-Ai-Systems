from typing import Any, Literal, Optional, Union

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    clarification_token: Optional[str] = None
    client_id: Optional[str] = None
    memory_action: Optional[str] = None
    memory_token: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str


# ----------------------------------------------------------------
# Typed public response contract for POST /chat
#
# These schemas document, for Swagger/OpenAPI, the externally
# observable response shapes produced by ChatService.
#
# They are used ONLY to document the "responses" schema on the /chat
# route. The endpoint still returns ChatService's raw dict; FastAPI
# does not re-validate/re-serialize through these models unless they
# are configured as response_model.
#
# These schemas intentionally exclude provider/runtime internals such
# as CALL-E confirmation tokens, ADK runner/session identifiers,
# CapabilityRegistry internals, environment configuration, and signed
# authorization tokens that are not part of a documented response.
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


class ClarificationResponse(BaseModel):
    agent: Literal["clarification"]
    status: Literal["needs_clarification", "invalid_context"]
    question: Optional[str] = None
    clarification_token: Optional[str] = None
    expires_at: Optional[str] = None
    message: Optional[str] = None


class MemoryResponse(BaseModel):
    """
    Public result of an explicit memory approval attempt.

    The signed memory authorization token is request-side authority
    and is never echoed back in this response.
    """

    agent: Literal["memory"]
    status: Literal["remembered", "invalid_authorization"]
    strategy: Optional[str] = None
    message: Optional[str] = None


class ExecutionProjectSchema(BaseModel):
    title: str
    description: str
    status: str


class TaskObservationSchema(BaseModel):
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
    output: str = ""
    observation: Optional[TaskObservationSchema] = None


class ExecutionResultSchema(BaseModel):
    success: bool
    output: str
    error: str


class TaskDecisionSchema(BaseModel):
    decision: Literal[
        "continue",
        "retry",
        "replan",
        "request_authority",
        "stop",
    ]
    reason: str


class ExecutionContinuationSchema(BaseModel):
    continue_applied: bool
    continue_skipped_reason: str
    continued_task: Optional[ExecutionCurrentTaskSchema] = None
    continued_execution: Optional[ExecutionResultSchema] = None
    continued_observation: Optional[TaskObservationSchema] = None
    continued_decision: Optional[TaskDecisionSchema] = None


class ExecutionResponse(BaseModel):
    agent: Literal["execution"]
    status: str
    project: ExecutionProjectSchema
    current_task: ExecutionCurrentTaskSchema
    execution: ExecutionResultSchema
    decision: Optional[TaskDecisionSchema] = None
    observation: Optional[TaskObservationSchema] = None
    continuation: Optional[ExecutionContinuationSchema] = None


class ConversationResponse(BaseModel):
    reply: Optional[str] = None
    error: Optional[str] = None


ChatEndpointResponse = Union[
    PlannerResponse,
    ExecutionResponse,
    AgentStatusMessageResponse,
    ClarificationResponse,
    MemoryResponse,
    ConversationResponse,
]