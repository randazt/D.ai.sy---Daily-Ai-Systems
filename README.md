# D.AI.SY — Daily AI Systems

> **An Adaptive Cognitive Accessibility & Human Agency Platform**

---

## Mission

D.AI.SY exists to help people become more capable—not more dependent.

Rather than replacing human thinking, D.AI.SY is being designed to improve cognitive accessibility, increase decision confidence, and strengthen long-term personal agency.

The platform guides users through a progression of:

> **Confusion → Clarity → Action → Confidence → Agency**

---

# Vision

Artificial intelligence should augment human intelligence—not replace it.

D.AI.SY combines large language models, structured reasoning, agentic orchestration, and explicit human-decision boundaries into an adaptive system designed to help people organize thoughts, evaluate uncertainty, make better decisions, and turn those decisions into structured action.

A central design principle is simple:

> **AI assists. Humans decide.**

D.AI.SY distinguishes between uncertainty that the system can help investigate and consequential choices that belong to the human.

When missing information can be resolved through research, comparison, discovery, or validation, D.AI.SY can incorporate that work into a plan.

When progress would require D.AI.SY to choose an important human preference, priority, objective, audience, constraint, or direction, D.AI.SY asks the human rather than silently making that choice.

---

# Current Status

**Version:** 0.1.0

**Development Status:** Active — Competition Deployment Operational

D.AI.SY is deployed on Google Cloud Run with a working Collaborative Partner and agentic execution pipeline.

The current implementation supports:

- Human-decision clarification before planning when consequential human judgment is required
- Evidence-resolvable uncertainty handled through discovery and validation work
- Adaptive planning after human clarification
- Goal-to-project planning
- Google Gemini-powered planning and reasoning
- Google Agent Development Kit (ADK) task execution
- Capability-based task orchestration
- Task observation and decision evaluation
- Bounded automatic continuation for eligible reasoning work
- Human authority boundaries for external real-world actions
- Claim boundaries separating hypothetical product capabilities from D.AI.SY capabilities
- Evidence boundaries for unsupported external assertions
- Stateless, signed, time-limited clarification context
- CALL-E integration with real calls disabled by default
- Interactive Swagger/OpenAPI testing

The current competition deployment demonstrates a Collaborative Partner workflow:

> **Goal → Human-Decision Boundary → Clarify When Needed → Human Direction → Adaptive Plan → Execute → Observe → Decide → Bounded Continuation**

Not every unknown requires clarification.

When uncertainty can be resolved through evidence—such as customer discovery, research, comparison, or validation—D.AI.SY can incorporate that uncertainty into the plan rather than unnecessarily requiring the human to decide.

When the unresolved issue is a consequential human preference, D.AI.SY preserves human decision authority and asks before planning across that boundary.

Deployment proof, evidence, and the final demo workflow are tracked in:

- [Live Agentic Proof](docs/submission/LIVE_AGENTIC_PROOF.md)
- [Submission Evidence Index](docs/submission/SUBMISSION_EVIDENCE_INDEX.md)
- [All Things Agentic Demo Runbook](docs/submission/ALL_THINGS_AGENTIC_DEMO_RUNBOOK.md)

---

# Implemented Features

## Backend

- FastAPI backend
- REST API architecture
- Request/response validation using Pydantic
- Modular service architecture
- Cloud Run-compatible container packaging
- Environment-based configuration
- Secure secret management
- Swagger/OpenAPI documentation
- Health monitoring endpoint

---

## Collaborative Partner Behavior

D.AI.SY includes a pre-planning human-decision boundary designed to distinguish between two fundamentally different kinds of uncertainty.

### Consequential Human Judgment

When planning would require the system to choose an important human preference or governing priority, D.AI.SY can pause and ask one focused clarification question.

The project is not created until the required human direction is supplied.

Examples include conflicts such as:

- speed versus depth
- income versus predictability
- simplicity versus advanced customization

These are not treated as factual questions that AI should silently resolve for the user.

### Evidence-Resolvable Uncertainty

When the missing information can be investigated, compared, researched, or validated, D.AI.SY can incorporate that uncertainty into the plan.

Examples include:

- which customer segment experiences the strongest problem
- whether a proposed value proposition is worth testing
- what assumptions need validation
- what evidence should be collected before building

This allows D.AI.SY to remain useful without unnecessarily returning every unknown to the human.

### Adaptive Planning

After clarification, the human's answer is combined with the original goal and passed to the planner.

The resulting project can therefore reflect the user's actual governing priority rather than a priority selected implicitly by the AI.

---

## Agentic Execution

The current execution architecture includes:

- Agent registry and routing
- PlannerAgent for goal-to-project task planning
- ClarificationService for pre-planning human-decision evaluation
- ExecutionAgent for task execution requests
- WorkflowEngine for task lifecycle management
- CapabilityRegistry for executor selection
- Capability-based task routing
- TaskObservation output after execution
- TaskDecision for post-execution policy decisions
- DecisionPolicy for next-step evaluation
- Bounded automatic continuation for eligible reasoning tasks
- Human authority boundaries for external actions
- Claim-boundary instructions for reasoning output
- Evidence-boundary instructions for unsupported external assertions

D.AI.SY does **not** recursively execute an entire project simply because a task returns a decision of `continue`.

Automatic continuation is bounded separately by the workflow. The current system can automatically continue into **one additional eligible reasoning task** and then stops automatic continuation.

Non-reasoning and authority-requiring work is not automatically executed merely because pending work remains.

---

## Human Agency and Reasoning Boundaries

D.AI.SY's reasoning layer includes explicit boundaries intended to preserve useful reasoning without presenting unsupported claims as established facts.

### Claim Boundary

D.AI.SY distinguishes between itself as the agentic system and products, services, strategies, or capabilities proposed inside a user's project.

Hypothetical product capabilities should not be represented as capabilities currently implemented by D.AI.SY.

### Evidence Boundary

When reasoning introduces external facts, statistics, market behaviors, prices, performance claims, availability claims, or business outcomes that were not supplied by the task or context, they should be framed appropriately as:

- assumptions
- hypotheses
- estimates
- illustrative examples
- items requiring validation

The system is instructed not to fabricate citations or imply external verification that did not occur.

---

## AI and Google Integration

- Google Gemini integration
- Google GenAI SDK
- Google Agent Development Kit (ADK)
- ADK-backed reasoning executor
- Service abstraction layer around model access
- Structured model responses for clarification classification
- Google Cloud Run deployment
- Google Secret Manager-backed production credentials

### Collaborative Partner Example

**User**

> I want to validate an affordable AI service for small local businesses that miss customer calls. I'm torn between getting to a revenue test as quickly as possible and spending more time deeply understanding the customer problem first. Help me build a plan.

**D.AI.SY**

Rather than silently deciding which strategic priority should govern the project, D.AI.SY asks the human to choose between the competing priorities.

**Human**

> Understanding the customer problem matters more. I don't want to build anything yet.

**D.AI.SY**

The planner then creates a discovery-oriented project reflecting that direction—for example, identifying appropriate interview targets, preparing customer-discovery work, gathering evidence, and synthesizing findings before solution building.

Generated plans can vary between runs; the important behavior is that the governing human priority is established before the project is created.

---

## CALL-E Integration

- CALL-E task executor implemented
- Phone-call capability routed through explicit task capability metadata
- Real calls disabled by default unless explicitly enabled
- Destination authority boundaries for external phone actions
- Authority-required outcomes handled through decision policy
- Code and test coverage for CALL-E safety behavior
- Phone-call tasks excluded from automatic reasoning continuation

The presence of a `phone_call` task in a generated plan does not mean that D.AI.SY automatically performs that external action.

---

## API Endpoints

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/` | GET | API status |
| `/health` | GET | Health check |
| `/chat` | POST | Conversation, clarification, planning, and execution routing |

---

# Security

Implemented security controls include:

- Environment-based secrets
- `.env` excluded from Git
- `.env.example` included without secret values
- Runtime Gemini credentials supplied through Google Secret Manager
- Dedicated production clarification signing secret supplied through Google Secret Manager
- Stateless clarification context
- Time-limited clarification context
- HMAC integrity protection for clarification context
- Validation of clarification context before planner handoff
- Fail-closed behavior for malformed, tampered, or expired clarification context
- Protection against using clarification context to bypass directly into execution
- External real-world actions gated behind explicit safety controls
- Repository history previously cleaned following credential exposure
- GitHub Push Protection issue resolved and affected credential regenerated

Clarification tokens are integrity-protected rather than treated as persistent server-side conversation state.

Persistent cross-session memory is not part of the current competition implementation.

---

# Repository Structure

```text
backend/
│
├── app/
│   ├── agents/
│   ├── api/
│   ├── config/
│   ├── firestore/
│   ├── knowledge/
│   ├── memory/
│   ├── models/
│   ├── orchestration/
│   ├── prompts/
│   ├── schemas/
│   ├── services/
│   └── main.py
│
├── tests/
├── Dockerfile
├── requirements.txt
├── .env.example
└── .env (local only)

docs/
│
├── architecture/
├── product/
├── submission/
├── ui/
├── ARCHITECTURE.md
└── PRODUCT.md
```

---

# Technology Stack

## Backend

- Python 3.12 container runtime
- FastAPI
- Uvicorn
- Pydantic
- python-dotenv

## AI and Agent Execution

- Google Gemini
- Google GenAI SDK
- Google Agent Development Kit (ADK)

## Deployment

- Google Cloud Run
- Google Secret Manager
- Docker

## Development

- Git
- GitHub
- Swagger/OpenAPI

---

# Successfully Completed During This Development Phase

✅ Initialized backend architecture

✅ Established modular package structure

✅ Created FastAPI application

✅ Added health endpoint

✅ Added root endpoint

✅ Created request/response schemas

✅ Built chat service abstraction

✅ Connected Google Gemini API

✅ Verified live inference

✅ Generated interactive Swagger documentation

✅ Implemented secure environment variable loading

✅ Removed exposed API key from repository history

✅ Configured Git ignore rules

✅ Regenerated affected API credentials

✅ Successfully pushed cleaned repository to GitHub

✅ Added multi-agent routing

✅ Added goal-to-project planning

✅ Added task capability metadata

✅ Added workflow execution lifecycle

✅ Added Google ADK reasoning executor

✅ Added guarded CALL-E executor

✅ Added task observation and decision evaluation

✅ Added bounded automatic continuation

✅ Added human-decision clarification boundary

✅ Added distinction between human judgment and evidence-resolvable uncertainty

✅ Added discovery-in-plan behavior

✅ Added adaptive planning after human clarification

✅ Added stateless signed clarification context

✅ Added clarification-token validation and fail-closed behavior

✅ Added claim boundaries for reasoning output

✅ Added evidence boundaries for unsupported external assertions

✅ Packaged backend for Cloud Run

✅ Configured production secrets through Google Secret Manager

✅ Verified live Cloud Run competition deployment

✅ Production-verified Collaborative Partner behavior

---

# Documentation

## Architecture

- System Overview
- API Contracts
- ADK Orchestration
- Firestore Data Model
- Context Packet

## Product

- Vision
- Product Overview
- Competition Demonstration

## Submission

- [Live Agentic Proof](docs/submission/LIVE_AGENTIC_PROOF.md)
- [Submission Evidence Index](docs/submission/SUBMISSION_EVIDENCE_INDEX.md)
- [All Things Agentic Demo Runbook](docs/submission/ALL_THINGS_AGENTIC_DEMO_RUNBOOK.md)

## UI

- Conversation Workspace

---

# Current Development Roadmap

## Phase 1 — Foundation ✅

- Backend
- Gemini
- API
- Documentation
- Secure configuration

**Status:** Complete

---

## Phase 2 — Agentic Planning and Execution ✅

- Agent registry
- PlannerAgent
- ExecutionAgent
- Google ADK integration
- Capability-based orchestration
- WorkflowEngine
- Capability registry
- Observation and decision evaluation
- TaskObservation
- TaskDecision
- Bounded continuation
- Human authority boundary
- CALL-E task executor with safe-call controls

**Status:** Core agent framework operational

---

## Phase 3 — Collaborative Partner & Competition Deployment ✅

- Human-decision boundary
- Clarification before consequential human choices
- Discovery-in-plan behavior
- Adaptive planning after clarification
- Stateless clarification context
- Claim and evidence boundaries
- Cloud Run deployment
- Secret Manager configuration
- Live planning proof
- Live execution proof
- Production Collaborative Partner verification
- Demo runbook
- Submission evidence index

**Status:** Operational

---

## Phase 4 — Persistent Memory

Planned:

- Firestore-backed persistence
- Conversation history
- Project persistence
- Execution history
- Growth Passport storage

Persistent cross-session memory should be considered planned work rather than a capability of the current competition deployment.

---

## Phase 5 — Product Experience

Planned:

- Web interface
- Authentication
- Dashboard
- Growth Passport visualization
- Workspace continuity

---

# Guiding Principles

## Human Agency First

AI should strengthen independent thinking rather than replace it.

In the current implementation, consequential human preferences remain with the human rather than being silently selected by the system.

---

## Human Decision Authority

Final decisions belong to the user.

When D.AI.SY identifies an unresolved conflict between consequential human priorities, it can ask for direction before creating the project.

> **AI assists. Humans decide.**

---

## Documentation-Driven Development

Architecture decisions are documented alongside implementation.

---

## Modular Architecture

Components should be replaceable, testable, and independently maintainable.

---

## Security by Default

Secrets are never committed to source control.

Runtime secrets remain environment-based and production credentials are supplied through Google Secret Manager.

---

## Evidence Over Assumption

Features are documented as complete only after implementation and verification.

Reasoning should also distinguish between supplied evidence and unsupported external assertions. When external claims have not been established by the available context, D.AI.SY frames them as assumptions, hypotheses, estimates, illustrative examples, or validation targets rather than verified facts.

---

# Project Status

D.AI.SY has transitioned from concept to a deployed Collaborative Partner and agentic AI backend.

The current project includes:

- Working FastAPI backend
- Live Google Gemini integration
- Google ADK reasoning execution
- Modular agent architecture
- Human-decision boundary before planning
- Evidence-resolvable discovery behavior
- Adaptive planning after clarification
- Goal-to-project planning
- Capability-based task execution
- Structured task observation
- Decision evaluation
- Bounded automatic continuation
- Human authority boundaries
- Claim and evidence safeguards
- Stateless signed clarification context
- Secure Cloud Run deployment
- Production-verified Collaborative Partner behavior
- Competition evidence framework

Persistent memory and the full user-facing product experience remain future development milestones.

The immediate focus is final submission artifact capture and competition video production.

---

# Reproducible Testing

## Live Hosted Demo

D.AI.SY is deployed on Google Cloud Run.

**Swagger interface:**

https://daisy-backend-pbhnglpapq-ue.a.run.app/docs

**Health endpoint:**

https://daisy-backend-pbhnglpapq-ue.a.run.app/health

The following walkthrough demonstrates the production Collaborative Partner behavior.

---

## Step 1 — Give D.AI.SY a Consequential Priority Conflict

Open the Swagger interface.

Expand:

`POST /chat`

Click:

**Try it out**

Submit:

```json
{
  "message": "I want to validate an affordable AI service for small local businesses that miss customer calls. I'm torn between getting to a revenue test as quickly as possible and spending more time deeply understanding the customer problem first. Help me build a plan."
}
```

### Expected behavior

D.AI.SY should recognize that planning immediately would require choosing a consequential human priority.

The response should therefore contain:

```text
agent = clarification
status = needs_clarification
```

It should also contain:

- one clarification question
- `clarification_token`
- `expires_at`

A project should **not** yet be created.

This demonstrates the human-decision boundary:

> D.AI.SY can analyze the problem, but it does not silently decide which governing priority the human should value.

---

## Step 2 — Supply the Human Decision

Copy the returned `clarification_token`.

Submit another `POST /chat` request containing the human's answer and the returned token.

Example:

```json
{
  "message": "Understanding the customer problem matters more. I don't want to build anything yet.",
  "clarification_token": "<RETURNED_CLARIFICATION_TOKEN>"
}
```

Replace `<RETURNED_CLARIFICATION_TOKEN>` with the token returned by Step 1.

Do not use the example placeholder literally.

### Expected behavior

The planner should now run and create the project.

The resulting plan should reflect the human's stated priority by emphasizing customer understanding and discovery before solution building.

Generated task titles may vary.

Representative production behavior has included work such as:

- defining customer interview targets
- preparing customer-discovery material
- conducting or planning qualitative discovery
- synthesizing findings
- identifying assumptions requiring validation

The important evidence is not exact task wording.

The important evidence is that:

> **the project is created after the human supplies the governing direction, and the plan adapts to that direction.**

---

## Step 3 — Execute

After the project is created, submit:

```json
{
  "message": "execute"
}
```

### Expected behavior

The response should contain evidence of the execution lifecycle, including:

- selected/current task
- execution result
- observation
- decision
- continuation evaluation

For a successfully completed eligible task, the decision may be:

```text
continue
```

A `continue` decision does **not** mean D.AI.SY is authorized to recursively execute the entire project.

Automatic continuation is separately bounded by the workflow.

The current implementation can automatically continue into **one additional reasoning task** when eligible.

If the next task is a non-reasoning capability—such as document generation, research, or an authority-requiring external action—automatic reasoning continuation is not applied.

---

## Secondary Behavior — Discovery Without Unnecessary Clarification

D.AI.SY does not ask the human to decide every unknown.

For example, if a user knows the objective but does not know which customer segment experiences the largest missed-call problem, that uncertainty can be treated as evidence-resolvable discovery work.

D.AI.SY can plan research, comparison, customer discovery, or validation rather than asking the user to guess the answer.

This distinction is central to the Collaborative Partner design:

> **Human values and priorities remain with the human. Evidence-resolvable uncertainty becomes structured work.**

---

# Competition Architecture Summary

The competition deployment demonstrates several distinct layers of agentic behavior:

1. **Route** — determine the appropriate interaction path.
2. **Human-decision boundary** — determine whether planning would require an unresolved consequential human choice.
3. **Clarify when required** — ask one focused question without prematurely creating a project.
4. **Adapt** — incorporate the human answer into the original goal.
5. **Plan** — decompose the clarified goal into structured tasks and capabilities.
6. **Execute** — route an eligible task to the appropriate executor.
7. **Observe** — record what happened.
8. **Decide** — evaluate the result and remaining work.
9. **Bound continuation** — apply only the continuation behavior permitted by system policy.
10. **Preserve authority** — prevent external or authority-requiring actions from bypassing their controls.

This architecture is designed around a simple principle:

> **Useful agency should increase human capability without quietly replacing human authority.**

---

# Submission State

The competition backend has completed production behavioral verification for:

- human-decision clarification
- adaptive planner handoff
- discovery-in-plan behavior
- claim boundaries
- evidence boundaries
- execution
- observation
- decision evaluation
- bounded continuation
- clarification-context safety
- context isolation
- production configuration

The backend is being treated as frozen for final submission artifact capture.

---

# Next Immediate Milestones

- Preserve final competition demo evidence
- Finalize submission documentation
- Capture final screenshots and B-roll
- Record the final competition walkthrough
- Produce the submission video
- Complete final submission packaging

Post-submission development can then continue toward:

- Firestore-backed persistent memory
- User-facing conversation workspace
- Authentication
- Growth Passport
- Expanded agent capabilities

---

> *"Helping people become more capable—not more dependent."*
