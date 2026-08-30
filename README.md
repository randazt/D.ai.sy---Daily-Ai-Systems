# D.AI.SY — Daily AI Systems

> **Adaptive cognitive accessibility and human agency for everyday life**

D.AI.SY helps people turn overwhelm, uncertainty, learning barriers, unclear goals, and decision friction into understandable, achievable action—without taking important decisions away from them.

**Core principle:** AI assists. Humans decide.

**Mission:** Helping people become more capable—not more dependent.

---

## Why D.AI.SY

Most agentic systems begin with a task:

> What should the AI do?

D.AI.SY begins one step earlier:

> What does the human need in order to understand, decide, and move forward?

The system is designed around this progression:

**Human cognition & accessibility → clarity → agency → everyday workflows → authorized agentic action**

D.AI.SY can clarify a cognitive bottleneck, remember a strategy the user explicitly teaches it, adapt later interactions with permission, transform human direction into structured work, and execute bounded tasks after authorization.

Autonomy happens downstream of human authority.

---

## All Things Agentic Hackathon

**Submission category:** Collaborative Partner

The D.AI.SY concept predates the hackathon. The software implementation submitted to the All Things Agentic Hackathon was built during the competition period, with repository development beginning August 4, 2026.

The competition implementation uses:

- **Gemini 3.5 Flash-Lite**
- **Google Agent Development Kit (ADK)**
- **Google Cloud Run**
- **Google Cloud Firestore**
- **Google Secret Manager**
- **FastAPI**
- **React + Vite**

---

## Current Status

**Version:** 0.1.0
**Status:** Competition implementation operational
**Backend regression baseline:** 236 tests passing

The current implementation includes:

- React/Vite conversation interface
- FastAPI conversation and orchestration backend
- cognition-first clarification
- human-authorized strategy memory
- Firestore-backed persistent memory
- cross-request retrieval of approved strategies
- separate permission to apply retrieved strategies
- progressive-disclosure adaptive guidance
- goal and workflow planning
- capability-based task execution
- explicit human execution authority
- task observations and execution decisions
- bounded reasoning continuation
- Google ADK reasoning execution
- Gemini 3.5 Flash-Lite
- Google Cloud Run deployment
- claim and evidence boundaries
- production browser-to-Cloud-Run integration

---

# Product Architecture

D.AI.SY is built around two human-authority boundaries.

## 1. Cognitive Authority

D.AI.SY does not treat conversational inference as permission to create persistent personal memory.

```text
Human states a strategy that works for them
        ↓
D.AI.SY proposes remembering it
        ↓
Human explicitly approves
        ↓
Strategy is persisted
        ↓
D.AI.SY retrieves it later
        ↓
D.AI.SY asks whether to use it
        ↓
Human decides
        ↓
Guidance adapts
```

This deliberately separates:

**permission to store ≠ permission to use**

## 2. Action Authority

A plan is not permission to execute.

```text
Human establishes direction
        ↓
D.AI.SY proposes structured work
        ↓
Human authorizes execution
        ↓
Bounded task execution
        ↓
Observation
        ↓
Decision
        ↓
At most one eligible reasoning continuation
        ↓
Control returns to human
```

Together, these boundaries implement:

**Human understanding → Human decision → Agentic action**

For the full as-built architecture, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

# Collaborative Partner Behavior

D.AI.SY is designed to collaborate with the human rather than silently optimize around them.

## Cognition-First Clarification

When a request indicates a cognitive bottleneck, D.AI.SY can clarify where the user is stuck before prescribing a solution.

For example, it may distinguish between difficulty:

- deciding what matters most,
- choosing between things that all feel important,
- or holding too many things in mind at once.

This is interaction support, not diagnosis.

D.AI.SY does not infer a medical, psychological, or learning-disability diagnosis from conversational context.

## Human-Owned Strategy Memory

A user can explicitly teach D.AI.SY a strategy that works for them.

Example:

> Seeing the overall system first helps me understand new material.

D.AI.SY can propose remembering that strategy. Persistence occurs only after explicit approval.

Production memory uses Google Cloud Firestore.

`MemoryService` retrieves only memories that are:

- approved, and
- sourced as `user_explicit`.

## Adaptive Retrieval

A remembered strategy is not silently applied later.

D.AI.SY can instead offer it back to the user:

> You previously told me that seeing the overall system first helps you understand new material. Would you like me to use that approach here?

Only after the user chooses to use the strategy does D.AI.SY adapt the interaction.

For the demonstrated system-first strategy, adaptation uses progressive disclosure:

1. show the big picture,
2. identify the major components,
3. show how they relate,
4. ask where the user wants to zoom in.

---

# Agentic Execution

D.AI.SY can turn established human direction into proposed work and then execute bounded tasks after authorization.

Implemented execution components include:

- PlannerAgent
- ExecutionAgent
- WorkflowEngine
- CapabilityRegistry
- task executors
- TaskObservation
- TaskDecision
- DecisionPolicy
- bounded continuation

A `continue` decision does not create unrestricted autonomous authority.

The workflow engine permits at most one automatic continuation, and only when the next task satisfies the implemented eligibility boundary.

Control then returns to the human.

---

# Google Agent Development Kit

D.AI.SY includes an implemented Google ADK execution path.

```text
Task
  ↓
AdkTaskExecutor
  ↓
google.adk.Agent
  ↓
google.adk.runners.InMemoryRunner
  ↓
Gemini 3.5 Flash-Lite
  ↓
TaskExecutionResult
```

Each ADK task receives a fresh session identifier.

The executor handles one bounded D.AI.SY reasoning task at a time rather than creating an unrestricted autonomous session.

---

# Claim and Evidence Boundaries

The ADK reasoning path includes explicit instructions designed to prevent generated reasoning from overstating what D.AI.SY or external evidence can establish.

The executor distinguishes:

- implemented D.AI.SY capabilities,
- user-proposed products or services,
- hypotheses,
- assumptions,
- estimates,
- illustrative examples,
- and externally verified facts.

Unsupported statistics, prices, market claims, performance claims, availability claims, or business outcomes must not be represented as established facts.

The model is also instructed not to fabricate citations or imply external verification that did not occur.

---

# Google Cloud Architecture

```text
Browser
  │
  ▼
React / Vite frontend
  │
  │ HTTPS
  ▼
Google Cloud Run
D.AI.SY FastAPI backend
  │
  ├────────────► Google Cloud Firestore
  │              approved strategy memory
  │
  └────────────► Google ADK
                   │
                   ▼
             Gemini 3.5 Flash-Lite
```

## Verified Production Backend

Cloud Run service:

```text
daisy-backend
```

Region:

```text
us-east1
```

Verified production revision:

```text
daisy-backend-00008-mzv
```

Backend URL:

```text
https://daisy-backend-490172530660.us-east1.run.app
```

Swagger/OpenAPI:

```text
https://daisy-backend-490172530660.us-east1.run.app/docs
```

The production frontend is configured through `VITE_API_BASE_URL` to communicate with this Cloud Run service.

---

# Firestore Persistence

D.AI.SY uses a replaceable persistence boundary:

```text
MemoryService
     │
     ▼
MemoryStore
     │
     ├────────► InMemoryMemoryStore
     │           local / tests
     │
     └────────► FirestoreMemoryStore
                 production
                      │
                      ▼
              Google Cloud Firestore
```

Production selects Firestore using:

```env
DAISY_MEMORY_STORE=firestore
```

The production path has been verified across separate requests:

**memory proposal → explicit human approval → Firestore persistence → later retrieval**

---

# API

Implemented endpoints:

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | GET | API status |
| `/health` | GET | Health check |
| `/chat` | POST | Conversation, memory, planning, and execution |

Interactive API documentation is available through FastAPI Swagger UI at `/docs`.

---

# Repository Structure

```text
backend/
├── app/
│   ├── agents/
│   ├── api/
│   ├── knowledge/
│   ├── models/
│   ├── orchestration/
│   ├── schemas/
│   ├── services/
│   └── main.py
├── tests/
├── Dockerfile
├── requirements.txt
└── .env.example

frontend/
├── src/
├── package.json
└── vite.config.*

docs/
├── architecture/
├── product/
├── submission/
├── ui/
├── ARCHITECTURE.md
└── PRODUCT.md
```

---

# Local Spin-Up

These instructions run D.AI.SY from a fresh clone.

## Prerequisites

Install:

- Git
- Python 3.12
- Node.js / npm

You also need your own Gemini API key for live Gemini-backed behavior.

---

## 1. Clone the Repository

```powershell
git clone https://github.com/randazt/D.ai.sy---Daily-Ai-Systems.git
cd D.ai.sy---Daily-Ai-Systems
```

---

## 2. Create the Backend Environment

From the repository root:

### Windows PowerShell

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

### macOS / Linux

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

---

## 3. Configure Local Environment Variables

Edit `backend/.env`.

At minimum, configure the values required by the local conversation and authorization paths:

```env
GEMINI_API_KEY=<your Gemini API key>
GEMINI_MODEL=gemini-3.5-flash-lite

DAISY_CLARIFICATION_TOKEN_SECRET=<generate a private local secret>
DAISY_MEMORY_AUTHORIZATION_SECRET=<generate a different private local secret>

DAISY_MEMORY_STORE=in_memory
DAISY_ENABLE_REAL_CALLS=0
```

Use independent private values for the two authorization secrets.

Do not commit `.env`.

For ordinary local evaluation, keep:

```env
DAISY_MEMORY_STORE=in_memory
DAISY_ENABLE_REAL_CALLS=0
```

Firestore is the verified production memory backend; local Firestore configuration is not required to run the standard local evaluation path.

---

## 4. Start the Backend

From `backend`:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8010
```

Verify:

```text
http://127.0.0.1:8010/
http://127.0.0.1:8010/health
http://127.0.0.1:8010/docs
```

---

## 5. Start the Frontend

Open a second terminal at the repository root.

```powershell
cd frontend
npm install
npm run dev
```

The Vite development configuration proxies local `/chat` requests to the local backend.

Open the local URL printed by Vite in your browser.

---

# Production Frontend Build

The frontend supports a production API base through:

```env
VITE_API_BASE_URL=https://daisy-backend-490172530660.us-east1.run.app
```

Build the frontend with:

```powershell
cd frontend
npm install
npm run build
```

The competition production configuration points the frontend at the verified Cloud Run backend.

No Gemini credential or backend authorization secret belongs in frontend configuration.

---

# Automated Tests

From `backend` with the virtual environment active:

```powershell
python -m unittest discover -s tests -v
```

Final verified competition baseline:

```text
236 tests passed
```

The test suite covers, among other behaviors:

- conversation routing,
- cognition-first clarification,
- clarification authorization safety,
- memory proposal and approval,
- approved-memory retrieval,
- adaptive memory application,
- planning,
- execution,
- observations,
- decision evaluation,
- bounded continuation,
- capability routing,
- Google ADK execution boundaries,
- claim boundaries,
- evidence boundaries,
- API/OpenAPI behavior.

Generated model wording may vary where live Gemini calls are involved; authority and response contracts are the important invariants.

---

# Suggested Evaluation Flow

A useful starting prompt is:

> I have an idea for something I really want to build, but it’s still all over the place in my head. I know what I care about, but I don’t know how to turn it into something I can actually start.

D.AI.SY should begin by helping clarify the human's direction rather than immediately converting the request into autonomous work.

The broader Collaborative Partner flow demonstrates:

```text
uncertainty
    ↓
clarification
    ↓
human direction
    ↓
user-owned strategy
    ↓
permission to remember
    ↓
persistent memory
    ↓
later retrieval
    ↓
permission to use
    ↓
adaptive guidance
    ↓
workflow
    ↓
execution authorization
    ↓
bounded agentic action
    ↓
observable result
    ↓
control returned to human
```

Exact model-generated wording may vary.

---

# Security

The competition implementation uses these security boundaries:

- environment-based configuration
- `.env` excluded from the tracked working tree
- `.env.example` for non-secret configuration examples
- Google Secret Manager references for sensitive production runtime values
- dedicated authorization secrets
- signed/time-limited authorization context where applicable
- explicit human approval before persistent strategy storage
- explicit human authority before external real-world action
- raw chat request logging removed from the API endpoint
- bounded continuation rather than unrestricted recursive execution
- no backend secrets embedded in the frontend production configuration

Do not expose API keys, authorization secrets, token values, credential payloads, or private user-message bodies in screenshots, logs, issues, or submission artifacts.

Any credential that may previously have appeared in development history or external working material should be treated as potentially compromised and rotated or revoked where applicable.

---

# Implemented vs. Future

## Implemented in the Competition Build

- React conversation interface
- FastAPI backend
- Gemini 3.5 Flash-Lite
- Google ADK reasoning execution
- Cloud Run deployment
- Firestore strategy-memory persistence
- explicit memory proposal and approval
- cross-request approved-memory retrieval
- separate permission to apply retrieved memory
- progressive-disclosure adaptation
- cognition-first clarification
- planning and workflow orchestration
- capability-based execution
- observation and decision evaluation
- bounded reasoning continuation
- human authority boundaries

## Future / Not Claimed as Implemented

The broader D.AI.SY product vision includes:

- comprehensive Growth Passport functionality
- richer long-term growth records
- broader third-party integrations
- additional everyday workflow capabilities
- additional product-wide persistence beyond the verified strategy-memory path

These are product directions, not completed competition capabilities.

---

# Documentation

## Judge-Facing

- [As-Built Architecture](docs/ARCHITECTURE.md)
- [Submission Evidence Index](docs/submission/SUBMISSION_EVIDENCE_INDEX.md)
- [All Things Agentic Demo Runbook](docs/submission/ALL_THINGS_AGENTIC_DEMO_RUNBOOK.md)
- [Live Agentic Proof](docs/submission/LIVE_AGENTIC_PROOF.md)

## Engineering Reference

- [System Overview](docs/architecture/SYSTEM_OVERVIEW.md)
- [API Contracts](docs/architecture/API_CONTRACTS.md)
- [ADK Orchestration](docs/architecture/ADK_ORCHESTRATION.md)
- [Firestore Data Model](docs/architecture/FIRESTORE_DATA_MODEL.md)
- [Context Packet](docs/architecture/CONTEXT_PACKET.md)

Some deeper engineering documents originated earlier in development and may contain design-stage material. For competition claims, the **As-Built Architecture** and **Submission Evidence Index** are authoritative.

---

# Evidence

Major competition claims are mapped to implementation, automated, and production evidence in:

[docs/submission/SUBMISSION_EVIDENCE_INDEX.md](docs/submission/SUBMISSION_EVIDENCE_INDEX.md)

The verified production path includes:

```text
React production frontend
        ↓
Google Cloud Run
        ↓
D.AI.SY conversation/orchestration
        ├────────► Firestore persistent approved memory
        └────────► Google ADK → Gemini 3.5 Flash-Lite
```

Verified production behaviors include:

- browser-to-Cloud-Run conversation,
- cognition-first clarification,
- explicit memory proposal,
- explicit human approval,
- Firestore persistence,
- later strategy retrieval,
- bounded execution behavior,
- and return of control to the human.

---

# Design Principles

### Human Agency First

AI should strengthen human capability rather than replace human judgment.

### Human Authority Before Persistence

Conversational inference is not permission to create persistent personal memory.

### Human Authority Before Action

A proposed plan is not permission to execute it.

### Accessibility Without Diagnosis

D.AI.SY can adapt to barriers and strategies the human describes without assigning a diagnosis or fixed identity.

### Evidence Over Assumption

Unsupported claims remain hypotheses, assumptions, estimates, examples, or validation targets.

### Observable Agentic Action

Agentic behavior should produce visible results that can be evaluated rather than relying on claims of hidden autonomy.

### Bounded Autonomy

Authorization for one action is not interpreted as unlimited authorization to continue.

---

# Submission Positioning

D.AI.SY is not designed to automate a person's life instead of them.

It helps the person understand what they want, establish direction, build systems around that direction, and automate the parts they choose.

The competition implementation demonstrates that architecture through two explicit authority boundaries:

**May I remember this? May I use it here?**

and:

**Here is what I propose to do. You decide whether execution happens.**

That produces the central D.AI.SY architecture:

**Human understanding → Human decision → Agentic action**

---

**Helping people become more capable—not more dependent.**
