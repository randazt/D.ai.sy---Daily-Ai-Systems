# D.AI.SY Submission Evidence Index

This index maps the major All Things Agentic submission claims to implementation evidence, automated test evidence, production behavioral evidence, and final submission artifacts.

It does not include secret values, clarification-token values, unverified repository SHAs, invented screenshots, fabricated timestamps, or unpublished artifact URLs.

## Current Production Baseline

- Production Cloud Run service: `daisy-backend`
- Production region: `us-east1`
- Accepted production revision: `daisy-backend-00002-mdt`
- Runtime service account: `daisy-runtime@daisy-agentic-2026.iam.gserviceaccount.com`
- Gemini credential reference only: `GEMINI_API_KEY -> daisy-gemini-api-key:1`
- Clarification signing-secret reference only: `DAISY_CLARIFICATION_TOKEN_SECRET -> daisy-clarification-token-secret:1`
- Accepted automated test baseline: 160 backend tests passed
- Final repository SHA: TBD / verify at packaging
- Final video and screenshot artifact locations: TBD / verify at packaging

## Evidence Matrix

| Area | Status | Implementation evidence | Automated test evidence | Production behavioral evidence | Submission artifact / remaining TBD |
|---|---|---|---|---|---|
| Production deployment and health | VERIFIED | Cloud Run-compatible backend and `/health` endpoint. | No separate health-specific automated test is claimed here. | Revision `daisy-backend-00002-mdt` was serving 100% traffic; `GET /health` returned HTTP `200` and `status=healthy`. | Final screenshot/video capture: TBD / verify at packaging. |
| Human-decision boundary | VERIFIED | `ClarificationService` evaluates consequential user-priority conflicts before planning. | Clarification decision tests cover human-value conflict detection and one-question behavior. | A revenue-speed vs customer-understanding conflict returned `agent=clarification`, `status=needs_clarification`, exactly one question, `clarification_token` present, `expires_at` present, and no project before the human answer. | Final demo capture should show fields, not token value. |
| Human direction and adaptive planning | VERIFIED | `ChatService` routes valid clarification answers to the planner with the original goal plus the human answer. | Flow tests cover valid-token answer reaching planner without requiring planner keywords. | The accepted walkthrough answer prioritized customer understanding and avoiding premature building; planning then created a discovery-oriented project reflecting that direction. | Final demo should show representative task types, not promise exact generated wording. |
| Discovery boundary | VERIFIED | Clarification decision logic distinguishes human judgment from evidence-resolvable uncertainty. | Decision tests cover discovery-in-plan and uncertainty-alone cases. | Segment uncertainty and value-proposition uncertainty proceeded directly to planner/discovery rather than unnecessary clarification. | Final demo may include a short secondary proof or narration. |
| Agentic execution | VERIFIED | `PlannerAgent`, `ExecutionAgent`, `WorkflowEngine`, `CapabilityRegistry`, `TaskObservation`, `TaskDecision`, and `DecisionPolicy` implement project/task execution. | Backend tests cover execution response structure, observations, decisions, and capability routing. | `{"message":"execute"}` returned `agent=execution`, selected a task, returned execution evidence, observation, decision, and continuation evaluation. | Final demo should highlight invariant response fields. |
| Bounded continuation | VERIFIED | `WorkflowEngine.execute_task_with_one_continue` applies at most one automatic continuation and only when the next task is eligible reasoning. | Workflow/decision tests cover one-step continuation, non-reasoning skip behavior, and no recursive continuation. | Accepted production run returned `decision=continue`, then skipped auto-continuation because the next task was `document_generation`; earlier reasoning-only evidence showed one eligible reasoning continuation can apply exactly once. | Do not require `continue_applied=true` universally; `continue_applied=false` can be the correct safe outcome. |
| Claim boundary | VERIFIED | ADK reasoning executor prompt and agent instruction separate D.AI.SY from user-proposed products/services. | ADK task executor regression tests verify claim-boundary instructions in model prompt and agent instruction. | Reviewed production output did not attribute proposed AI call-handling service capabilities to implemented D.AI.SY capabilities. | Final narration should say "proposed service" or "candidate capability" for user product ideas. |
| Evidence boundary | VERIFIED | ADK reasoning executor prompt and agent instruction require unsupported external assertions to be framed as assumptions, hypotheses, estimates, examples, or validation targets. | ADK task executor regression tests verify evidence-boundary instructions in prompt and agent instruction. | Reviewed production output did not present unsupported market facts, statistics, prices, performance claims, or business outcomes as verified facts. | Final narration should avoid unsupported market claims unless framed as hypotheses. |
| Clarification-context safety | VERIFIED | Clarification context is stateless, signed, time-limited, and validated without process-global pending state. | Flow tests cover malformed/tampered/expired context, missing secret fail-closed behavior, execute-with-token protection, and context isolation. | Invalid or tampered context returned `agent=clarification`, `status=invalid_context`; `execute` with clarification context failed closed; abandoned clarification did not contaminate an independent request. | Token presence may be shown; token values must not be shown. |
| External-action authority | VERIFIED / PARTIAL RUNTIME | CALL-E and external real-world actions remain separate capabilities behind authority controls; real calls remain disabled unless explicitly authorized. | CALL-E safety tests and execution boundary tests cover authority-gated behavior. | Accepted walkthrough did not execute any `phone_call` task. Planned `phone_call` work, when present, remained pending and was not automatically executed. | Separate intentionally authorized CALL-E runtime proof remains optional/future if required. |
| Production security/configuration | VERIFIED | Environment-based secret references and dedicated clarification signing-secret variable. | OpenAPI/schema and clarification tests cover request contract and fail-closed missing-secret behavior. | Production configuration showed `GEMINI_API_KEY -> daisy-gemini-api-key:1`, `DAISY_CLARIFICATION_TOKEN_SECRET -> daisy-clarification-token-secret:1`, and runtime service account `daisy-runtime@daisy-agentic-2026.iam.gserviceaccount.com`. | Do not capture secret payloads, token values, credentials, or billing details. |
| Log hygiene | VERIFIED WITH KNOWN ISSUE | Application currently logs ordinary user-message markers from the chat endpoint. | No automated log-hygiene test is claimed. | Inspected production logs did not expose clarification tokens, secret payloads, signing-secret values, or Gemini API key values. Ordinary user-message logging remains a known hygiene issue. | Final video should not show message bodies from logs; future cleanup should reduce request-body logging. |
| Automated test baseline | VERIFIED | Accepted implementation includes claim/evidence boundaries and stateless clarification behavior. | 160 backend tests passed for the accepted implementation baseline. | Production acceptance also passed after deployment. | Do not attach the 160-test count to an unverified final SHA; final SHA is TBD / verify at packaging. |
| Google Gemini and ADK | VERIFIED | Planning uses the Google GenAI SDK; reasoning execution uses the Google ADK-backed executor and Gemini model default `gemini-3.5-flash-lite` when no override is supplied. | Tests cover Gemini service per-call configuration and ADK executor prompt/instruction behavior. | Production planning and execution exercised the deployed Gemini/ADK-backed paths during acceptance. | Final demo can mention Gemini/ADK at architecture level without exposing credentials or internal traces. |
| Official submission naming | VERIFIED | README and realigned evidence docs use D.AI.SY as the official product name. | Not applicable. | Not applicable. | Continue using D.AI.SY in final-facing prose. |

## Secondary Evidence

Earlier reasoning-only validation remains useful as supporting evidence for the bounded-continuation mechanism:

- A reasoning task completed.
- A `TaskObservation` was produced.
- `TaskDecision.decision` returned `continue`.
- One additional eligible reasoning task executed automatically.
- A second `continue` decision could be exposed, but recursive automatic continuation did not occur.

This is secondary evidence only. The primary production proof is the Collaborative Partner behavior on revision `daisy-backend-00002-mdt`.

## Final Packaging TBD Items

- Final repository SHA for the submitted package.
- Final video artifact location.
- Final screenshot or clip locations.
- Official submission form fields and any final wording required by the platform.
- Optional separately authorized CALL-E runtime proof, if the final submission chooses to include it.

## Evidence Boundaries

- Do not include secret values.
- Do not include clarification-token values.
- Do not imply that `decision=continue` authorizes unrestricted execution.
- Do not imply `continue_applied=true` is always required.
- Do not imply planned `phone_call` tasks were executed during the accepted walkthrough.
- Do not promote persistent cross-session memory, Firestore-backed continuity, web UI, authentication, dashboard, or Growth Passport to implemented capabilities unless separately verified.
