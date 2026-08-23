# D.AI.SY (Daily AI Systems)

> **An Adaptive Cognitive Accessibility & Human Agency Platform**

---

## Mission

D.AI.SY exists to help people become more capable—not more dependent.

Rather than replacing human thinking, D.AI.SY is being designed to improve cognitive accessibility, increase decision confidence, and strengthen long-term personal agency.

The platform guides users through a progression of:

> **Confusion → Clarity → Action → Confidence → Agency**

---

# Vision

Artificial Intelligence should augment human intelligence—not replace it.

D.AI.SY combines modern large language models, structured reasoning, and multi-agent collaboration into an adaptive system that helps people organize thoughts, make better decisions, and continue growing over time. Persistent memory and long-term continuity are planned future components.

---

# Current Status

**Version:** 0.1.0

**Development Status:** Active — Competition Deployment Operational

D.AI.SY is deployed on Google Cloud Run with a working agentic execution pipeline.

The current implementation supports:

- Goal-to-project planning
- Google Gemini-powered reasoning
- Google Agent Development Kit (ADK) task execution
- Capability-based task orchestration
- Task observation and decision evaluation
- Bounded autonomous continuation for at most one additional eligible reasoning task
- Human-decision clarification before planning when consequential human judgment is required
- Distinction between consequential human preferences and evidence-resolvable uncertainty
- Adaptive planning after human clarification
- Stateless, signed, time-limited clarification context
- Claim and evidence boundaries in reasoning output
- Human authority boundaries for external real-world actions
- CALL-E integration with real calls disabled by default
- Interactive Swagger/OpenAPI testing

The current competition deployment demonstrates the core agentic loop:

> **Goal → Human-Decision Boundary → Clarify When Needed → Human Direction → Adaptive Plan → Execute → Observe → Decide → Bounded Continuation**

Evidence-resolvable uncertainty is handled through discovery, research, comparison, or validation inside the plan rather than unnecessarily requiring a human decision.

Deployment proof, evidence, and the final demo workflow are tracked in:

- [Live Agentic Proof](docs/submission/LIVE_AGENTIC_PROOF.md)
- [Submission Evidence Index](docs/submission/SUBMISSION_EVIDENCE_INDEX.md)
- [All Things Agentic Demo Runbook](docs/submission/ALL_THINGS_AGENTIC_DEMO_RUNBOOK.md)

---

# Implemented Features

## Backend

- FastAPI backend
- REST API architecture
- Request/Response validation using Pydantic
- Modular service architecture
- Cloud Run-compatible container packaging
- Environment variable configuration
- Secure API key management
- Swagger/OpenAPI documentation
- Health monitoring endpoint

---

## Agentic Execution

- Agent registry and routing
- PlannerAgent for goal-to-project task planning
- ExecutionAgent for task execution requests
- WorkflowEngine for task lifecycle management
- CapabilityRegistry for executor selection
- TaskObservation output after execution
- TaskDecision for post-execution policy decisions
- DecisionPolicy for next-step evaluation
- Bounded autonomous continuation for safe reasoning tasks
- Human authority boundary for external actions

---

## Collaborative Partner Behavior

- ClarificationService for pre-planning clarification when the user's request contains a consequential unresolved human priority
- Human-decision boundary that keeps governing preferences and trade-offs with the human
- Discovery-in-plan behavior for uncertainty that can be resolved through research, comparison, reasoning, or validation
- Adaptive planner handoff after clarification using the original goal plus the human's answer
- Signed clarification context that is stateless, time-limited, and rejected if malformed, tampered with, or expired
- Claim boundary separating hypothetical product capabilities from implemented D.AI.SY capabilities
- Evidence boundary requiring unsupported external factual assertions to be framed as assumptions, hypotheses, estimates, illustrative examples, or validation targets

---

## AI and Google Integration

- Google Gemini `gemini-3.5-flash-lite`-powered planning and reasoning
- Google GenAI SDK integration
- Google ADK-backed reasoning executor
- Service abstraction layer around model access
- Verified prompt/response pipeline
- Google Cloud Run deployment
- Secret Manager-based Gemini credential configuration in deployment

Example:

```
User:
I'm trying to validate an affordable AI service for small local businesses that miss customer calls. I'm torn between getting to a revenue test quickly and spending more time deeply understanding the customer problem first.

D.AI.SY:
Asks which priority should govern the plan rather than silently choosing. When the human chooses customer understanding and says they do not want to build yet, D.AI.SY creates a discovery-oriented plan reflecting that direction.
```

---

## CALL-E Integration

- CALL-E task executor implemented
- Phone-call capability routed through explicit task capability metadata
- Real calls disabled by default through `DAISY_ENABLE_REAL_CALLS=0`
- Destination authority boundaries for external phone actions
- Code and test coverage for CALL-E safety behavior

---

## API Endpoints

Implemented:

| Endpoint | Method | Purpose |
|-----------|----------|-----------------------------|
| / | GET | API Status |
| /health | GET | Health Check |
| /chat | POST | Conversation, planning, and execution routing |

---

## Security

Implemented:

- Environment-based secrets
- `.env` excluded from Git
- `.env.example` included
- Repository history cleaned to remove exposed API key
- GitHub Push Protection resolved
- API key regenerated
- Runtime Gemini credentials supplied through Google Secret Manager
- External real-world actions gated behind explicit safety controls
- Clarification context is stateless and time-limited
- Clarification context is integrity-protected using HMAC signing
- Clarification signing uses a dedicated production secret supplied through Google Secret Manager
- Malformed, tampered, or expired clarification context is rejected

---

# Repository Structure

```
backend/
│
├── app/
│   ├── agents/
│   ├── api/
│   ├── knowledge/
│   ├── models/
│   ├── orchestration/
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

- Google Gemini `gemini-3.5-flash-lite`
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

✅ Regenerated API credentials

✅ Successfully pushed cleaned repository to GitHub

✅ Added multi-agent routing

✅ Added goal-to-project planning

✅ Added task capability metadata

✅ Added workflow execution lifecycle

✅ Added Google ADK reasoning executor

✅ Added guarded CALL-E executor

✅ Added task observation and decision evaluation

✅ Added bounded autonomous continuation

✅ Added human-decision clarification boundary

✅ Added discovery-vs-human-judgment behavior

✅ Added adaptive planning after clarification

✅ Added stateless clarification context

✅ Added claim boundary

✅ Added evidence boundary

✅ Verified Collaborative Partner behavior in production

✅ Packaged backend for Cloud Run

✅ Verified live Cloud Run competition deployment

---

# Documentation

## Architecture

- System Overview
- API Contracts
- ADK Orchestration
- Planned Firestore Data Model
- Context Packet

## Product

- Vision
- Product Overview
- Competition Demonstration

## Submission

- Live Agentic Proof
- Submission Evidence Index
- All Things Agentic Demo Runbook

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

Status:
**Complete**

---

## Phase 2 — Agentic Planning and Execution

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
- Human-decision clarification boundary
- Discovery-in-plan behavior
- Adaptive planning after clarification
- Stateless signed clarification context
- Claim and evidence boundaries

Status:
**Core agent framework operational**

---

## Phase 3 — Competition Deployment

- Cloud Run deployment
- Gemini credential configuration through Secret Manager
- Live planning proof
- Live execution proof
- Demo runbook
- Submission evidence index

Status:
**Operational**

---

## Phase 4 — Persistent Memory

Planned:

- Firestore integration
- Conversation history
- Project persistence
- Execution history
- Growth Passport storage

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

D.AI.SY is developed according to several core principles:

### Human Agency First

AI should strengthen independent thinking rather than replace it. Consequential human preferences remain with the human.

---

### Human Decision Authority

Final decisions always belong to the user.

AI assists.

Humans decide.

D.AI.SY clarifies rather than silently selecting a governing priority when planning depends on a human value judgment.

---

### Documentation-Driven Development

Architecture decisions are documented alongside implementation.

---

### Modular Architecture

Components should be replaceable, testable, and independently maintainable.

---

### Security by Default

Secrets are never committed to source control.

Configuration remains environment-based.

---

### Evidence Over Assumption

Features are only documented as complete after successful implementation and verification.

Unsupported external claims are framed as assumptions, hypotheses, estimates, illustrative examples, or items requiring validation.

---

# Next Immediate Milestones

- Preserve final competition demo evidence
- Capture final video and screenshots
- Run a fresh final backend test pass before submission packaging
- Continue Firestore-backed persistent memory
- Build the user-facing conversation workspace
- Expand agent capabilities

---

# Project Status

D.AI.SY has successfully transitioned from concept to a deployed agentic AI backend.

The project now possesses:

- Working backend
- Live Gemini integration
- Modular agent architecture
- Capability-based execution
- Structured task observation
- Decision evaluation
- Bounded autonomous continuation
- Human-decision clarification before planning
- Discovery-vs-human-judgment behavior
- Adaptive planning from human clarification
- Stateless signed clarification context
- Claim and evidence boundaries for reasoning output
- Secure Cloud Run deployment
- Competition evidence framework

The next development milestone focuses on final submission artifact capture and persistent memory.

---

*"Helping people become more capable—not more dependent."*
## Reproducible Testing

### Live hosted demo

D.AI.SY is deployed on Google Cloud Run.

Swagger interface:
[https://daisy-backend-pbhnglpapq-ue.a.run.app/docs](https://daisy-backend-pbhnglpapq-ue.a.run.app/docs)

1. Open the Swagger interface.
2. Expand `POST /chat`.
3. Click **Try it out**.
4. Submit:

Step 1 — Human priority conflict

{
  "message": "I'm trying to validate an affordable AI service for small local businesses that miss customer calls. I'm torn between getting to a revenue test as quickly as possible and spending more time deeply understanding the customer problem first. Help me build the right plan."
}

Expected:

- `agent = clarification`
- `status = needs_clarification`
- exactly one clarification question
- `clarification_token`
- `expires_at`
- no project yet

Step 2 — Human direction

Submit the clarification answer with the returned `clarification_token`:

{
  "message": "Understanding the customer problem matters more. I don't want to build anything yet.",
  "clarification_token": "<returned clarification_token>"
}

Expected:

- planner runs only after the answer
- project is created
- plan adapts toward customer discovery

Representative production-verified task types included customer interview targeting, interview-guide creation, qualitative interviews, and discovery synthesis. Exact Gemini-generated task wording may vary.

Step 3 — Execute

Submit:

{
  "message": "execute"
}

Expected:

- `agent = execution`
- task execution evidence
- `observation`
- `decision`
- `continuation`

Automatic continuation is limited to one additional reasoning task. Non-reasoning or authority-requiring work is not automatically executed merely because a decision says `continue`.

Secondary check:

Evidence-resolvable uncertainty, such as determining which customer segment has the largest problem, can proceed directly into planning and discovery without unnecessary clarification.

Health endpoint:
https://daisy-backend-pbhnglpapq-ue.a.run.app/health

The competition deployment uses Google Cloud Run, the Google GenAI SDK,
and Google Agent Development Kit (ADK).

Real-world CALL-E phone actions are disabled in the competition deployment
unless explicitly authorized.
