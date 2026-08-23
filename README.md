D.AI.SY Submission Realignment — Phase 2A: README

The production backend is frozen and has passed Collaborative Partner production acceptance. Modify README.md only so the documentation accurately reflects the currently deployed and verified system.

Do not modify backend code, tests, deployment configuration, Cloud Run, Secret Manager, IAM, or any other documentation file. Do not commit, push, or deploy.

1. Naming

Use D.AI.SY consistently as the official submission-facing product name. Do not convert it to D.A.I.S.Y.

2. Current Status

Preserve existing supported capabilities, but add the production-verified Collaborative Partner behavior:

human-decision clarification before planning when consequential human judgment is required
distinction between consequential human preferences and evidence-resolvable uncertainty
adaptive planning after human clarification
stateless, signed, time-limited clarification context
claim/evidence boundaries in reasoning

Replace the old submission-level flow:

Goal → Plan → Execute → Observe → Decide → Bounded Continuation

with:

Goal → Human-Decision Boundary → Clarify When Needed → Human Direction → Adaptive Plan → Execute → Observe → Decide → Bounded Continuation

Explain immediately afterward that evidence-resolvable uncertainty is handled through discovery, research, comparison, or validation inside the plan rather than unnecessarily requiring a human decision.

3. Agentic Execution

Add concise bullets for:

ClarificationService
human-decision boundary
discovery-in-plan behavior
adaptive planner handoff after clarification
signed clarification context
claim boundary separating hypothetical product capabilities from D.AI.SY capabilities
evidence boundary for unsupported external factual assertions

Preserve the existing PlannerAgent, ExecutionAgent, WorkflowEngine, TaskObservation, TaskDecision, DecisionPolicy, capability routing, authority boundary, and bounded-continuation descriptions.

Do not imply D.AI.SY autonomously completes an entire project. Automatic continuation is limited to one additional reasoning task, subject to system boundaries.

4. AI and Google Integration Example

Replace the existing generic example with a short Collaborative Partner example:

User has a meaningful priority conflict between reaching a revenue test quickly and deeply understanding the customer problem first.

D.AI.SY asks which priority should govern the plan rather than silently choosing.

Human chooses customer understanding and says they do not want to build yet.

D.AI.SY then creates a discovery-oriented plan reflecting that direction.

Keep this concise and clearly illustrative.

5. Security

Preserve existing security claims and add that clarification context is:

stateless
time-limited
integrity-protected using HMAC signing
backed by a dedicated signing secret supplied through Google Secret Manager in production
rejected when malformed, tampered with, or expired

Do not expose secret values, tokens, credentials, internal security material, or unnecessary operational detail.

6. Completed Milestones

Add completed milestones for:

human-decision clarification boundary
discovery-vs-human-judgment behavior
adaptive planning after clarification
stateless clarification context
claim boundary
evidence boundary
production verification of Collaborative Partner behavior
7. Guiding Principles

Preserve the existing principles and wording wherever possible. Make the implementation connection clearer:

Human Agency First → consequential human preferences remain with the human
Human Decision Authority → D.AI.SY clarifies rather than silently selecting a governing priority
Evidence Over Assumption → unsupported external claims are framed as assumptions, hypotheses, estimates, illustrative examples, or items requiring validation
8. Project Status

Update the implemented-capability summary to include the Collaborative Partner behavior now verified in production.

9. Reproducible Testing

Substantially revise this section.

The primary walkthrough should demonstrate:

Step 1 — Human priority conflict

Submit a planning request in which the user wants help validating an affordable AI service for small local businesses that miss customer calls but is torn between getting to a revenue test quickly and spending more time deeply understanding the customer problem first.

Expected:

agent = clarification
status = needs_clarification
exactly one clarification question
clarification_token
expires_at
no project yet

Step 2 — Human direction

Submit the clarification answer with the returned clarification_token, expressing that understanding the customer problem matters more and that the user does not want to build yet.

Expected:

planner runs only after the answer
project is created
plan adapts toward customer discovery

Representative production-verified task types included customer interview targeting, interview-guide creation, qualitative interviews, and discovery synthesis. Do not guarantee exact generated task wording.

Step 3 — Execute

Submit {"message":"execute"} after planning.

Expected response should demonstrate:

execution
observation
decision
continuation evaluation

Explain that automatic continuation is limited to one additional reasoning task and that non-reasoning/authority-requiring work is not automatically executed merely because a decision says continue.

Include a short secondary note that uncertainty that can be resolved through evidence—such as determining which customer segment has the largest problem—can proceed directly into planning/discovery without unnecessary clarification.

10. Gemini model claim

Before retaining the exact phrase “Google Gemini 3.5 Flash Lite”, inspect the current source-code default actually used when GEMINI_MODEL is absent.

If the repository unambiguously supports the exact model name, retain/correct the wording to match the source.
If the exact deployed model cannot be established from the repository, replace the overly specific claim with Google Gemini rather than guessing.
Do not change application configuration or code.
11. Preserve roadmap boundaries

Persistent memory, Firestore-backed continuity, full web UI, authentication, dashboard, and Growth Passport remain planned/future work unless the repository explicitly proves otherwise. Do not promote them to implemented capabilities.

12. Cleanup

If literal [svg](...) artifacts actually exist in the source README and serve no intentional purpose, remove them. If they were only artifacts of copied GitHub-rendered content, make no change for this item.

Required output

After editing, stop before commit and report:

exact file modified
concise section-by-section change summary
exact Gemini model source/default found and resulting README wording
confirmation that D.AI.SY naming is consistent
confirmation that no backend/code/config/deployment files changed
git diff --check result
git diff --stat
git status --short
any remaining unsupported, ambiguous, or potentially misleading submission claim
recommendation: GO / MODIFY / BLOCK for README acceptance
