# D.AI.S.Y. All Things Agentic Demo Runbook

Target category: Taskmaster

Purpose: produce a reproducible final competition video under four minutes using the currently deployed D.AI.S.Y. backend. This runbook does not require code changes, redeployment, UI work, persistence, CALL-E activation, or a real phone call.

Live service: https://daisy-backend-pbhnglpapq-ue.a.run.app

Approved deployed revision: `daisy-backend-00001-k9g`

## 1. Video Structure

Target duration: 3:35. Hard limit: 4:00.

| Time | Segment | Purpose |
|---|---|---|
| 0:00-0:25 | Opening problem and value proposition | State that D.A.I.S.Y. turns vague goals into structured, executable progress while preserving human authority. |
| 0:25-0:55 | Architecture and Google technology | Explain FastAPI `/chat`, PlannerAgent, ExecutionAgent, Gemini, Google ADK, WorkflowEngine, TaskObservation, DecisionPolicy, and bounded continuation. |
| 0:55-2:35 | Live application demonstration | Show live Cloud Run URL, send planning request, verify reasoning tasks, send execution request, verify execution, observation, decision, and continuation. |
| 2:35-3:15 | Autonomous-control and safety | Show that continuation is bounded, only reasoning auto-continues, `DAISY_ENABLE_REAL_CALLS=0`, and phone action remains behind authority. |
| 3:15-3:35 | Closing impact statement | Tie the demo to Taskmaster: decomposition, execution, observation, decision, bounded action, and human authority. |

## 2. Exact Live Demo Sequence

Use the deployed `/chat` endpoint only:

```text
POST https://daisy-backend-pbhnglpapq-ue.a.run.app/chat
Content-Type: application/json
```

Important routing note: the first planning prompt must avoid words that route directly to the ExecutionAgent, including `run`, `execute`, `start`, `launch`, `deploy`, `complete`, and `finish`.

### Request 1: Planning

```json
{"message":"Plan a reasoning-only D.A.I.S.Y. demo that helps a user clarify a vague product idea into one clear next step. Use only reasoning tasks. Avoid phone calls, internet research, file generation, email, purchases, credentials, or external real-world activity."}
```

Expected planning result:

- HTTP status `200`
- Response variant: `PlannerResponse`
- `agent` is `planner`
- `project.status` is `active`
- Planned tasks are reasoning-only
- No `phone_call` task appears
- No CALL-E action appears

Verified task list from the successful live run:

1. Analyze the Vague Product Idea
2. Deconstruct Value Proposition
3. Synthesize Constraints and Feasibility
4. Formulate Candidate Next Steps
5. Select the Single Clear Next Step

Acceptable recording variation: Gemini may change the wording of task titles. The take is still valid if the response contains 4 to 6 safe tasks, all capabilities are `reasoning`, and no external action is introduced.

### Request 2: Execution

Send immediately after the planning response:

```json
{"message":"execute"}
```

Expected execution result:

- HTTP status `200`
- Response variant: `ExecutionResponse`
- `agent` is `execution`
- `status` is `completed`
- `current_task.capability` is `reasoning`
- `execution.success` is `true`
- `observation.outcome` is `completed`
- `decision.decision` is `continue`
- `continuation.continue_applied` is `true`
- `continuation.continued_task.capability` is `reasoning`
- `continuation.continued_execution.success` is `true`
- `continuation.continued_observation.outcome` is `completed`
- `continuation.continued_decision.decision` is `continue`
- There is no nested continuation beyond the one visible continuation object

## 3. Expected Response Checkpoints

### Planning Checkpoints

Visibly verify:

- `agent: planner`
- `goal` matches the messy/vague user goal
- `knowledge` may include `welcome.txt`
- `project.tasks` exists
- Each visible task has `capability: reasoning`
- Each visible task starts as `status: pending`
- No `phone_call`, `research`, or `document_generation` capability appears

Do not depend on exact Gemini-generated prose. The structural fields are the evidence.

### Execution Checkpoints

Visibly verify:

- `agent: execution`
- `status: completed`
- `execution.success: true`
- `current_task.status: completed`
- `current_task.capability: reasoning`
- `observation.success: true`
- `observation.outcome: completed`
- `decision.decision: continue`
- `continuation.continue_applied: true`
- `continued_task.status: completed`
- `continued_task.capability: reasoning`
- `continued_observation.outcome: completed`
- `continued_decision.decision: continue`

Safety checkpoint: the response should not contain `phone_call`, CALL-E execution, confirmation tokens, phone numbers, or any real-world action result.

## 4. What Must Be Visible On Screen

Show enough evidence for a judge to see this is the live deployed system:

- The Cloud Run URL: `https://daisy-backend-pbhnglpapq-ue.a.run.app`
- Safe startup check, such as `GET /` or `GET /health`
- Cloud Run service metadata showing revision `daisy-backend-00001-k9g`, region `us-east1`, and service name `daisy-backend`
- The planning request body and live HTTP `200` response
- The planner response with reasoning tasks
- The execution request body and live HTTP `200` response
- The execution response fields for `execution`, `observation`, `decision`, and `continuation`
- Cloud Run log evidence for planner activity showing `Models.generate_content`
- Cloud Run log evidence for execution activity showing `AsyncModels.generate_content`
- `DAISY_ENABLE_REAL_CALLS=0`
- Gemini credential configured from Secret Manager without showing the secret value
- No CALL-E invocation and no phone call

Do not show API keys, secret payloads, personal credentials, billing details, OAuth tokens, or any CALL-E execution screen.

## 5. Architecture Talk Track

D.A.I.S.Y. exposes a FastAPI `/chat` endpoint on Cloud Run. A user sends a messy goal. The router sends planning language to the PlannerAgent, which uses Gemini to convert the goal into structured project tasks. The ExecutionAgent then selects the first pending task and passes it to the WorkflowEngine.

For reasoning tasks, the WorkflowEngine resolves the reasoning capability to the Google ADK-backed executor. The ADK executor uses the Google GenAI runtime to produce a concise execution result. The WorkflowEngine wraps that result in a `TaskObservation`, including success, task status, capability, outcome, and summary.

The observation is passed to the provider-neutral `DecisionPolicy`. If the task completed and pending work remains, the policy returns `continue`. D.A.I.S.Y. applies at most one automatic continuation, and only if the next pending task is also `reasoning`. That creates bounded autonomy: the system can take a safe follow-up step, but it does not enter an unbounded loop.

External phone action is a separate capability. It remains behind the CALL-E authority gate and is not part of this All Things Agentic demo. `DAISY_ENABLE_REAL_CALLS=0` confirms real calls are disabled.

## 6. Taskmaster Alignment

This is agentic, not just chatbot output:

- It decomposes a vague goal into structured tasks.
- It assigns explicit task capabilities.
- It executes a task through the reasoning capability.
- It observes the result as structured state.
- It makes an explicit next-step decision.
- It applies one bounded follow-up action autonomously.
- It preserves human authority for consequential external actions like phone calls.

For Taskmaster, the key proof is the loop:

```text
goal -> plan -> execute -> observe -> decide -> bounded continue -> stop
```

## 7. Recording Checklist

### Windows To Have Ready

- Browser or terminal showing `https://daisy-backend-pbhnglpapq-ue.a.run.app`
- API client or terminal for `POST /chat`
- Cloud Run console or read-only terminal output for service metadata
- Cloud Run logs filtered around the demo time
- `docs/submission/LIVE_AGENTIC_PROOF.md`
- `docs/submission/SUBMISSION_EVIDENCE_INDEX.md`

### Request Bodies To Paste

Planning:

```json
{"message":"Plan a reasoning-only D.A.I.S.Y. demo that helps a user clarify a vague product idea into one clear next step. Use only reasoning tasks. Avoid phone calls, internet research, file generation, email, purchases, credentials, or external real-world activity."}
```

Execution:

```json
{"message":"execute"}
```

### Optional PowerShell Shape

```powershell
$base = "https://daisy-backend-pbhnglpapq-ue.a.run.app"

$planBody = @{
  message = "Plan a reasoning-only D.A.I.S.Y. demo that helps a user clarify a vague product idea into one clear next step. Use only reasoning tasks. Avoid phone calls, internet research, file generation, email, purchases, credentials, or external real-world activity."
} | ConvertTo-Json

Invoke-RestMethod -Uri "$base/chat" -Method Post -ContentType "application/json" -Body $planBody |
  ConvertTo-Json -Depth 30

$executeBody = @{ message = "execute" } | ConvertTo-Json

Invoke-RestMethod -Uri "$base/chat" -Method Post -ContentType "application/json" -Body $executeBody |
  ConvertTo-Json -Depth 30
```

### Do Not Expose

- `GEMINI_API_KEY`
- Secret Manager payloads
- OAuth tokens
- personal credentials
- billing details
- CALL-E credentials
- phone numbers
- confirmation tokens

### Do Not Do During Recording

- Do not enable CALL-E.
- Do not set `DAISY_ENABLE_REAL_CALLS=1`.
- Do not execute a `phone_call` task.
- Do not redeploy.
- Do not modify code.
- Do not stage, commit, or push.

## 8. Failure Plan

Acceptable variations:

- Task title wording differs from the verified run.
- Gemini-generated prose differs.
- The plan has 4 to 6 tasks instead of exactly five.
- Execution wording differs while preserving the same structural fields.

Restart the take:

- The first request routes to `execution` instead of `planner`.
- The plan includes `phone_call`, `research`, `document_generation`, or an external action.
- The execution request returns `No project exists`.
- The execution response lacks `TaskObservation`.
- The execution response lacks `TaskDecision`.
- `continuation.continue_applied` is false.
- The response is too slow or visually unclear for the recording.

Stop without fixing during the recording:

- The service returns repeated `5xx` responses.
- ADK/Gemini execution repeatedly fails.
- Any workflow attempts to cross into `phone_call`.
- Any secret or credential accidentally appears on screen.

Do not propose or perform code changes during the demo capture session.

## 9. Evidence Capture

Save these separately from the final video:

- Screenshot of Cloud Run service URL, revision, and region.
- Screenshot of safe `/health` response.
- Screenshot or clipped terminal output of the planning request and response.
- Screenshot or clipped terminal output of the execution response.
- Screenshot showing `TaskObservation`.
- Screenshot showing `TaskDecision`.
- Screenshot showing `continuation.continue_applied=true`.
- Screenshot showing `DAISY_ENABLE_REAL_CALLS=0`.
- Screenshot showing Gemini secret mapping by name only, with no value.
- Cloud Run log clip showing `Models.generate_content`.
- Cloud Run log clip showing `AsyncModels.generate_content`.
- Repository SHA: `8240a5ceb57c8220b3d752505fb2c88fffd01301`.
- `docs/submission/LIVE_AGENTIC_PROOF.md`.
- `docs/submission/SUBMISSION_EVIDENCE_INDEX.md`.

## 10. Video Script

Use this as a compact spoken script. Adjust only for natural delivery.

### 0:00-0:25 Opening

"D.A.I.S.Y. is built for the Taskmaster category. The problem is simple: people often bring AI vague goals, and ordinary chat stops at advice. D.A.I.S.Y. turns a messy goal into structured work, executes safe reasoning steps, observes what happened, and decides what should happen next while preserving human authority."

### 0:25-0:55 Architecture

"This live backend is running on Google Cloud Run. The user enters the FastAPI `/chat` endpoint. Planning requests go to the PlannerAgent, which uses Gemini to create structured tasks. Execution requests go to the ExecutionAgent and WorkflowEngine. Reasoning tasks are handled through the Google ADK-backed executor using the Google GenAI runtime. Every execution result becomes a TaskObservation, and a provider-neutral DecisionPolicy chooses the next action."

### 0:55-1:45 Planning Demo

"Here is the live Cloud Run URL. I am sending a reasoning-only user goal. The response is not just a chat answer. D.A.I.S.Y. creates a project and returns multiple tasks. Each task has a capability, and in this demo every capability is reasoning. There is no phone call, no external action, and no CALL-E execution."

### 1:45-2:35 Execution Demo

"Now I send the existing `execute` command. D.A.I.S.Y. selects the first pending reasoning task and executes it through the deployed execution path. The response shows execution success, the completed task, and a structured TaskObservation with outcome completed."

### 2:35-3:15 Decision And Safety

"The observation is evaluated by the DecisionPolicy. Because the task completed and safe reasoning work remains, the decision is continue. D.A.I.S.Y. applies exactly one bounded continuation into the next reasoning task. The second task also completes, but the system does not recursively continue forever. Phone actions remain behind the CALL-E authority boundary, and `DAISY_ENABLE_REAL_CALLS` is zero."

### 3:15-3:35 Closing

"This demonstrates the agentic loop judges should care about: goal to plan, plan to execution, execution to observation, observation to decision, and one bounded autonomous follow-up. D.A.I.S.Y. is not replacing human authority; it is making safe progress while keeping consequential external actions under explicit control."

## 11. Final Success Criteria

The All Things Agentic demo is complete when the recording captures:

- Live Cloud Run service URL.
- Revision `daisy-backend-00001-k9g`.
- Planning request sent to deployed `/chat`.
- Planner response with reasoning-only tasks.
- Execution request sent to deployed `/chat`.
- Execution success for the first reasoning task.
- `TaskObservation.outcome=completed`.
- `TaskDecision.decision=continue`.
- `continuation.continue_applied=true`.
- Exactly one additional reasoning task completed.
- No recursive continuation shown.
- Cloud Run logs showing `Models.generate_content`.
- Cloud Run logs showing `AsyncModels.generate_content`.
- `DAISY_ENABLE_REAL_CALLS=0`.
- No CALL-E invocation.
- No real phone call.
- No secrets or credentials visible.

When all of those are visible or preserved as supporting evidence, the All Things Agentic demo recording can be marked complete.
