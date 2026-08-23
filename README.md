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

D.AI.SY combines modern large language models, persistent memory, structured reasoning, and multi-agent collaboration into an adaptive system that helps people organize thoughts, make better decisions, and continue growing over time.

---

# Current Status

**Version:** 0.1.0

**Development Status:** Active

The backend foundation has been successfully established and verified.

Core infrastructure is operational and ready for expansion into persistent memory, agent orchestration, and long-term user context.

---

# Implemented Features

## Backend

- FastAPI backend
- REST API architecture
- Request/Response validation using Pydantic
- Modular service architecture
- Environment variable configuration
- Secure API key management
- Swagger/OpenAPI documentation
- Health monitoring endpoint

---

## AI & Agentic Integration

- Google Gemini 3.5 Flash Lite
- Google GenAI SDK
- Google Agent Development Kit (ADK)
- PlannerAgent for structured project planning
- ExecutionAgent for task execution
- WorkflowEngine for agentic orchestration
- TaskObservation for execution-state capture
- TaskDecision for post-execution policy decisions
- Bounded one-step autonomous continuation
- Human authority boundary for external actions
- CALL-E capability integration with real calls disabled by default

Example:

```
User:
What is 17 multiplied by 43?

Gemini:
17 multiplied by 43 is 731.
```

---

## API Endpoints

Implemented:

| Endpoint | Method | Purpose |
|-----------|----------|-----------------------------|
| / | GET | API Status |
| /health | GET | Health Check |
| /chat | POST | Gemini Chat |

---

## Security

Implemented:

- Environment-based secrets
- `.env` excluded from Git
- `.env.example` included
- Repository history cleaned to remove exposed API key
- GitHub Push Protection resolved
- API key regenerated

---

# Repository Structure

```
backend/
│
├── app/
│   ├── agents/
│   ├── api/
│   ├── config/
│   ├── firestore/
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
├── ui/
├── ARCHITECTURE.md
└── PRODUCT.md
```

---

# Technology Stack

## Backend

- Python 3.14
- FastAPI
- Uvicorn
- Pydantic
- python-dotenv

## AI

- Google Gemini 3.5 Flash Lite
- Google GenAI SDK
- Google Agent Development Kit (ADK)

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

## UI

- Conversation Workspace

---

# Current Development Roadmap

## Phase 1 — Foundation ✅

- Backend
- Gemini
- API
- Documentation

Status:
**Complete**

---

## Phase 2 — Memory

Planned:

- Firestore
- Conversation Memory
- User Profiles
- Growth Passport persistence

Status:
**In Progress**

---

## Phase 3 — Agent Framework ✅

Implemented:

- Google ADK integration
- PlannerAgent
- ExecutionAgent
- WorkflowEngine
- Capability registry
- TaskObservation
- TaskDecision
- Bounded autonomous continuation
- Human authority boundary
- CALL-E task executor with safe-call controls

Status: **Core agent framework operational**

---

## Phase 4 — Cognitive Platform

Planned:

- Context Packet generation
- Multi-agent orchestration
- Long-term reasoning
- Decision support
- Personal growth tracking

---

## Phase 5 — User Experience

Planned:

- Web interface
- Authentication
- Dashboard
- Growth Passport visualization

---

# Guiding Principles

D.AI.SY is developed according to several core principles:

### Human Agency First

AI should strengthen independent thinking rather than replace it.

---

### Human Decision Authority

Final decisions always belong to the user.

AI assists.

Humans decide.

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

---

# Next Immediate Milestones

- Firestore integration
- Persistent conversation memory
- Growth Passport storage
- Google ADK integration
- Multi-agent orchestration

---

# Project Status

D.AI.SY has successfully transitioned from concept to a functioning AI platform.

The project now possesses:

- Working backend
- Live AI integration
- Modular architecture
- Secure configuration
- Public repository
- Documentation framework

# Next Immediate Milestones

- Persistent conversation memory
- Firestore integration
- Growth Passport storage
- User-facing web interface
- Expanded agent capabilities

---

*"Helping people become more capable—not more dependent."*
## Reproducible Testing

### Live hosted demo

D.A.I.S.Y. is deployed on Google Cloud Run.

Swagger interface:
https://daisy-backend-pbhnglpapq-ue.a.run.app/docs

1. Open the Swagger interface.
2. Expand `POST /chat`.
3. Click **Try it out**.
4. Submit:

{
  "message": "Plan a project to help me decide how to validate an affordable AI service for small local businesses that miss customer calls. I don't know who my first customer should be or what I should validate first. Break this goal into safe reasoning tasks that lead to one clear next step."
}

5. Confirm the response contains a structured project plan and tasks.
6. Submit:

{
  "message": "execute"
}

7. Confirm the execution response contains task execution evidence,
   `observation`, `decision`, and `continuation`.

Health endpoint:
https://daisy-backend-pbhnglpapq-ue.a.run.app/health

The competition deployment uses Google Cloud Run, the Google GenAI SDK,
and Google Agent Development Kit (ADK).

Real-world CALL-E phone actions are disabled in the competition deployment
unless explicitly authorized.
