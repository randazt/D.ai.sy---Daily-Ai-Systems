# D.AI.SY All Things Agentic Demo Runbook

Target category: Taskmaster

Purpose: guide a final competition walkthrough using the production-verified D.AI.SY Collaborative Partner behavior. This runbook does not require code changes, redeployment, configuration changes, secret access, CALL-E activation, or a real phone call.

Live service: https://daisy-backend-pbhnglpapq-ue.a.run.app

Current production revision: `daisy-backend-00002-mdt`

Primary flow:

```text
Goal -> Human-Decision Boundary -> Clarify When Needed -> Human Direction -> Adaptive Plan -> Execute -> Observe -> Decide -> Bounded Continuation
```

Core narration:

> AI assists. Humans decide.

D.AI.SY distinguishes among:

- consequential human judgment -> clarify
- evidence-resolvable uncertainty -> discover in the plan
- eligible bounded reasoning -> may continue automatically once
- external or authority-requiring action -> remains separately gated

## 1. Establish Live Deployment

Use the deployed public service. Start with a quick health check:

```text
GET https://daisy-backend-pbhnglpapq-ue.a.run.app/health
```

Expected:

- HTTP `200`
- `status=healthy`

Do not show Cloud Console details, credentials, billing information, Secret Manager payloads, or secret values. The Cloud Run URL and health response are enough to establish the live deployment for the primary walkthrough.

## 2. Demonstrate the Human-Decision Boundary

Use `POST /chat`.

Primary prompt:

```json
{
  "message": "I'm trying to validate an affordable AI service for small local businesses that miss customer calls. I'm torn between getting to a revenue test as quickly as possible and spending more time deeply understanding the customer problem first. Help me build the right plan."
}
```

Expected response:

- `agent=clarification`
- `status=needs_clarification`
- exactly one clarification question
- `clarification_token` is present
- `expires_at` is present
- no `project` exists yet

Presenter note:

D.AI.SY is identifying that the user has a consequential priority conflict. It asks the human which priority should govern the plan instead of silently choosing for them.

Do not expose the clarification-token value in the video. If using Swagger, zoom or crop around the field names and values needed for proof while avoiding the actual token. If using a terminal, store the token privately and do not print it.

## 3. Provide Human Direction

Use the accepted direction:

```text
Understanding the customer problem matters more. I don't want to build anything yet.
```

Submit it with the returned clarification context privately:

```json
{
  "message": "Understanding the customer problem matters more. I don't want to build anything yet.",
  "clarification_token": "<returned clarification_token omitted>"
}
```

Expected response:

- planner runs only after the human answer
- project is created
- the original goal and human answer are carried into planning
- the plan adapts toward customer discovery before building

Presenter note:

The human supplies the governing priority. D.AI.SY uses that answer to create an adaptive plan rather than choosing the priority itself.

## 4. Demonstrate Adaptive Planning

Highlight the planner response:

- `agent=planner`
- `project`
- `project.tasks`
- task `capability`
- task `status`

Representative production-verified task types included:

- defining the target customer or interview profile
- preparing a discovery interview guide
- customer discovery or interview work
- synthesizing discovery findings

Do not require exact task titles. Gemini-generated wording can vary. The invariant proof is that the project appears only after human direction and the task plan reflects the user's stated priority: customer understanding before building.

Explain that the proposed affordable AI call-handling service is the user's product hypothesis. Proposed service capabilities are hypotheses or validation targets, not implemented D.AI.SY capabilities.

## 5. Demonstrate Agentic Execution

After planning, submit:

```json
{"message":"execute"}
```

Expected response fields to highlight:

- `agent=execution`
- `current_task`
- `current_task.capability`
- `execution.success`
- `observation.outcome`
- `decision.decision`
- `continuation`

Presenter note:

D.AI.SY executes an eligible task through the deployed workflow, records a structured observation, and produces a next-step decision.

## 6. Explain Bounded Continuation Correctly

Do not require `continuation.continue_applied=true`.

The success condition is that D.AI.SY evaluates continuation and enforces the capability and authority boundary.

Valid outcomes:

- If the next pending task is eligible `reasoning`, D.AI.SY may automatically execute one additional reasoning task.
- If the next pending task is `document_generation`, `research`, `phone_call`, another non-reasoning capability, or authority-requiring work, D.AI.SY should not automatically execute it.
- In a non-reasoning or authority-bound case, `continue_applied=false` is a successful safety result.

Highlight when present:

- `continuation.continue_applied`
- `continuation.continue_skipped_reason`
- `continuation.continued_task.capability`
- `continuation.continued_decision`

Explain clearly:

> A decision to continue is not unrestricted authorization to execute whatever comes next.

## 7. Briefly Establish the Discovery Boundary

Mention the verified contrast without turning it into a second long demo:

Evidence-resolvable uncertainty can proceed into the plan. For example, uncertainty about which customer segment has the largest missed-call problem can become discovery, research, comparison, or validation work instead of forcing the human to decide without evidence.

Optional secondary prompt if needed:

```json
{
  "message": "I want to validate an affordable AI service for local businesses that miss customer calls. I don't know which customer segment has the biggest missed-call problem. Build a plan to compare likely segments and determine which one I should validate first."
}
```

Expected:

- planner response
- no unnecessary clarification
- uncertainty becomes discovery or validation work

Use this only if the video needs an explicit contrast. The primary demo remains the human-decision clarification flow.

## 8. On-Screen Checklist

Show or narrate these invariant fields:

- `agent`
- `status`
- `question`
- `clarification_token` presence only
- `expires_at`
- absence of `project` before clarification
- `project.tasks`
- `capability`
- `current_task`
- `execution.success`
- `observation.outcome`
- `decision.decision`
- `continuation.continue_applied`
- `continuation.continue_skipped_reason`
- `continued_task.capability` when applicable

Do not depend on exact generated task wording.

## 9. Do Not Show or Emphasize

Do not show:

- clarification-token values
- API keys
- secret values
- OAuth or access credentials
- Secret Manager payloads
- billing or personal-account details
- raw logs containing user-message text
- phone numbers
- live CALL-E execution
- internal HMAC or signing implementation details beyond "signed, time-limited clarification context"

Do not claim:

- that D.AI.SY has implemented the proposed AI call-handling service
- that D.AI.SY autonomously completes the whole project
- that `decision=continue` grants unrestricted execution authority
- that `continue_applied=true` is always required
- that planned `phone_call` tasks were executed in this accepted walkthrough

## 10. Recovery During Recording

Safe recovery options:

- Temporary model/API failure: wait briefly and retry the same request once. Do not change code, configuration, secrets, deployment, or production data during recording.
- Unexpected generated task wording: continue if the invariant fields and behavior are correct.
- `continue_applied=false`: continue if the skipped reason shows the next task was non-reasoning or authority-bound. This is a successful safety result.
- Another clarification response appears: check whether the prompt is still asking D.AI.SY to choose a consequential human priority. Either answer the clarification or restart with the exact primary prompt.
- Swagger UI display issues: zoom/collapse fields or use a terminal/API client while keeping token values hidden.

Stop without fixing during recording if:

- repeated `5xx` responses occur
- any secret, credential, or token value appears on screen
- the workflow is about to execute a live phone/CALL-E action
- production configuration unexpectedly changes

Do not redeploy, edit files, change secrets, change IAM, or modify Cloud Run during demo capture.

## 11. Success Criteria

The walkthrough succeeds when judges can see:

1. D.AI.SY identifies a consequential human-priority decision.
2. D.AI.SY asks rather than choosing.
3. No project exists before required human direction.
4. The human answer changes or adapts the resulting plan.
5. D.AI.SY executes an eligible task.
6. Execution is observed.
7. A next-step decision is produced.
8. Continuation is evaluated and bounded appropriately.
9. Proposed product capabilities are not misrepresented as D.AI.SY capabilities.
10. Human authority remains intact.

## 12. Secondary Backup Evidence

Prior reasoning-only continuation evidence may be used as backup only:

- a reasoning task completed
- an observation was produced
- the decision was `continue`
- one additional eligible reasoning task executed automatically
- recursive continuation did not occur

This is not the primary walkthrough. The primary walkthrough is the production-verified Collaborative Partner flow on revision `daisy-backend-00002-mdt`.

## 13. Final Packaging TBD

Verify at packaging:

- final repository SHA
- final video artifact location
- final screenshot or clip locations
- official submission form fields
- final submission wording required by the platform
