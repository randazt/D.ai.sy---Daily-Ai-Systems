export interface ChatRequest {
  message: string;
  clarification_token?: string | null;
  client_id?: string | null;
  memory_action?: string | null;
  memory_token?: string | null;
  memory_id?: string | null;
}

export interface PlannerTask {
  title: string;
  description: string;
  capability?: string | null;
  inputs: Record<string, unknown>;
  status: string;
  output: string;
}

export interface PlannerProject {
  id: string;
  title: string;
  description: string;
  status: string;
  tasks: PlannerTask[];
}

export interface PlannerResponse {
  agent: "planner";
  goal: string;
  knowledge: string[];
  knowledge_preview: string;
  project: PlannerProject;
  plan: string[];
}

export interface ClarificationResponse {
  agent: "clarification";
  status: "needs_clarification" | "invalid_context";
  question?: string | null;
  clarification_token?: string | null;
  expires_at?: string | null;
  message?: string | null;
}

export interface MemoryResponse {
  agent: "memory";
  status:
    | "approval_required"
    | "remembered"
    | "strategy_available"
    | "no_strategy"
    | "invalid_authorization";
  strategy?: string | null;
  memory_token?: string | null;
  memory_id?: string | null;
  expires_at?: string | null;
  original_message?: string | null;
  message?: string | null;
}

export interface AgentStatusMessageResponse {
  agent: "planner" | "execution";
  status: string;
  message: string;
}

export interface TaskObservation {
  task_title: string;
  capability: string;
  status: string;
  success: boolean;
  outcome: string;
  summary: string;
  error: string;
}

export interface ExecutionCurrentTask {
  title: string;
  description: string;
  capability?: string | null;
  inputs: Record<string, unknown>;
  status: string;
  output: string;
  observation?: TaskObservation | null;
}

export interface ExecutionResult {
  success: boolean;
  output: string;
  error: string;
}

export type Decision =
  | "continue"
  | "retry"
  | "replan"
  | "request_authority"
  | "stop";

export interface TaskDecision {
  decision: Decision;
  reason: string;
}

export interface ExecutionContinuation {
  continue_applied: boolean;
  continue_skipped_reason: string;
  continued_task?: ExecutionCurrentTask | null;
  continued_execution?: ExecutionResult | null;
  continued_observation?: TaskObservation | null;
  continued_decision?: TaskDecision | null;
}

export interface ExecutionResponse {
  agent: "execution";
  status: string;
  project: {
    title: string;
    description: string;
    status: string;
  };
  current_task: ExecutionCurrentTask;
  execution: ExecutionResult;
  decision?: TaskDecision | null;
  observation?: TaskObservation | null;
  continuation?: ExecutionContinuation | null;
}

export interface ConversationResponse {
  reply?: string | null;
  error?: string | null;
}

export type ChatResponse =
  | PlannerResponse
  | ClarificationResponse
  | MemoryResponse
  | AgentStatusMessageResponse
  | ExecutionResponse
  | ConversationResponse;