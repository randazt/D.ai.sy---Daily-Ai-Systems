import type {
  AgentStatusMessageResponse,
  ChatResponse,
  ClarificationResponse,
  ExecutionResponse,
  MemoryResponse,
  PlannerResponse,
} from "./chatTypes";

export function isClarificationResponse(
  response: ChatResponse,
): response is ClarificationResponse {
  return "agent" in response && response.agent === "clarification";
}

export function isExecutionResponse(
  response: ChatResponse,
): response is ExecutionResponse {
  return (
    "agent" in response &&
    response.agent === "execution" &&
    "current_task" in response
  );
}

export function isMemoryResponse(
  response: ChatResponse,
): response is MemoryResponse {
  return "agent" in response && response.agent === "memory";
}

export function isPlannerResponse(
  response: ChatResponse,
): response is PlannerResponse {
  return (
    "agent" in response &&
    response.agent === "planner" &&
    "project" in response &&
    "plan" in response
  );
}

export function isStatusResponse(
  response: ChatResponse,
): response is AgentStatusMessageResponse {
  return (
    "agent" in response &&
    "status" in response &&
    "message" in response &&
    response.agent !== "memory" &&
    !("project" in response)
  );
}