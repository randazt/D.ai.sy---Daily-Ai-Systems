# D.AI.SY — As-Built Architecture

> D.AI.SY (Daily AI Systems) is an adaptive cognitive accessibility and human-agency platform designed to help people turn overwhelm, uncertainty, and unclear goals into understandable, achievable action while preserving human decision authority.

**Submission architecture:** All Things Agentic Hackathon — Collaborative Partner
**Architecture status:** As built and verified for the competition submission
**Core principle:** AI assists. Humans decide.

---

## 1. Architecture Thesis

D.AI.SY is designed around a simple ordering:

**Human cognition and accessibility → clarity → agency → everyday workflows → authorized agentic action**

The system does not begin with autonomous execution.

It begins by helping the human understand what they want, where they are stuck, and what kind of support is useful. Persistent adaptation and agentic execution occur downstream of explicit human authority.

This produces two distinct authority boundaries:

1. **Cognitive authority** — the user decides whether D.AI.SY may remember and later use a strategy that works for them.
2. **Action authority** — the user decides whether a proposed task or workflow may actually be executed.

The architecture is therefore designed around:

**Human understanding → Human decision → Agentic action**

---

## 2. As-Built System Architecture

```text
┌──────────────────────────────────────────────────────────────────────┐
│                              HUMAN                                   │
│                                                                      │
│  expresses goal, uncertainty, barrier, strategy, or direction       │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    D.AI.SY REACT FRONTEND                            │
│                                                                      │
│  Conversation Workspace                                             │
│  • clarification                                                    │
│  • memory permission                                                │
│  • memory-use permission                                            │
│  • planning                                                         │
│  • execution authorization                                          │
│  • observable results                                               │
│                                                                      │
│  Production API base → Cloud Run                                    │
└───────────────────────────────┬──────────────────────────────────────┘
                                │ HTTPS /chat
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│               FASTAPI CONVERSATION / ORCHESTRATION LAYER            │
│                         Google Cloud Run                             │
│                                                                      │
│  Routes each interaction according to the user's current need       │
│  rather than forcing every request through one fixed pipeline.      │
│                                                                      │
│  ┌────────────────────┐       ┌───────────────────────────────────┐  │
│  │ Cognition-First    │       │ Human-Authorized Memory          │  │
│  │ Clarification      │       │                                   │  │
│  │                    │       │ propose → approve → persist       │  │
│  │ clarify before     │       │ retrieve → offer → user chooses  │  │
│  │ prescribing action │       │ whether to apply                 │  │
│  └─────────┬──────────┘       └───────────────┬───────────────────┘  │
│            │                                  │                      │
│            │                                  ▼                      │
│            │                         ┌───────────────────────┐       │
│            │                         │ Google Cloud          │       │
│            │                         │ Firestore             │       │
│            │                         │                       │       │
│            │                         │ user-approved         │       │
│            │                         │ strategy memory       │       │
│            │                         └───────────────────────┘       │
│            │                                                         │
│            ▼                                                         │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ Planning / Workflow Agency                                    │  │
│  │                                                               │  │
│  │ turns human direction into proposed, bounded work             │  │
│  └───────────────────────────────┬───────────────────────────────┘  │
│                                  │                                  │
│                     HUMAN AUTHORIZATION REQUIRED                    │
│                                  │                                  │
│                                  ▼                                  │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ Task Execution                                                │  │
│  │                                                               │  │
│  │ capability routing → executor → observation → decision        │  │
│  │ → at most one eligible bounded reasoning continuation         │  │
│  │ → control returned to human                                   │  │
│  └───────────────────────────────┬───────────────────────────────┘  │
└──────────────────────────────────┼──────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    GOOGLE ADK EXECUTION PATH                         │
│                                                                      │
│  AdkTaskExecutor                                                     │
│       ↓                                                              │
│  google.adk.Agent                                                    │
│       ↓                                                              │
│  google.adk.runners.InMemoryRunner                                   │
│       ↓                                                              │
│  Gemini 3.5 Flash-Lite                                               │
│       ↓                                                              │
│  concise execution result                                            │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     OBSERVABLE RESULT                                │
│                                                                      │
│  execution output → observation → bounded decision → frontend        │
│                                                                      │
│                    CONTROL RETURNS TO HUMAN                          │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 3. Google Technology Stack

The competition implementation uses the required Google agentic and cloud stack directly.

### Gemini

D.AI.SY uses:

**Gemini 3.5 Flash-Lite**

Gemini provides model reasoning and generation for the implemented reasoning paths.

The model is configurable through `GEMINI_MODEL`, with the competition implementation defaulting to `gemini-3.5-flash-lite`.

### Google Agent Development Kit (ADK)

Reasoning tasks can execute through the implemented `AdkTaskExecutor`.

The production code creates:

- `google.adk.Agent`
- `google.adk.runners.InMemoryRunner`
- an isolated ADK session for the task

The ADK agent executes the bounded reasoning task using the configured Gemini model.

ADK is therefore part of the implemented execution architecture rather than a documentation-only dependency.

### Google Cloud Run

The FastAPI backend is deployed on Google Cloud Run.

Cloud Run hosts the production conversation and execution API and provides the deployed backend used by the production frontend configuration.

### Google Cloud Firestore

Firestore provides persistent storage for explicitly approved user strategy memories.

Production selects this backend through:

`DAISY_MEMORY_STORE=firestore`

The storage implementation remains behind a `MemoryStore` boundary so local and automated tests can use an in-memory implementation without initializing cloud infrastructure.

---

## 4. Conversation Architecture

D.AI.SY presents one conversational interface to the human.

The backend does **not** require every message to pass through a fixed chain of agents. Instead, the conversation service routes the interaction according to the current state and the kind of help required.

Implemented behaviors include:

- cognition-first clarification
- general conversational reasoning
- explicit strategy-memory proposal
- explicit memory approval
- retrieval of previously approved strategies
- explicit permission before applying a retrieved strategy
- progressive-disclosure adaptation
- planning
- bounded task execution
- observation and execution-decision evaluation
- bounded reasoning continuation

This allows D.AI.SY to remain conversational while exposing explicit authority boundaries where persistence or action would otherwise occur.

---

## 5. Cognition-First Clarification

D.AI.SY is designed to clarify before prescribing when a cognitive bottleneck is detected.

For example, when a user is overwhelmed by competing priorities, the system can first determine whether the difficulty is:

- deciding what matters most,
- choosing between things that all feel important, or
- holding too many things in mind at once.

The purpose is not to diagnose the user.

The purpose is to identify the immediate interaction barrier so the system can provide useful structure without prematurely deciding what the human should do.

This supports the core design rule:

**Understand the human's difficulty before optimizing the workflow.**

---

## 6. Human-Authorized Memory

D.AI.SY implements persistent strategy memory around explicit human ownership and authorization.

A strategy is not treated as persistent memory merely because the model inferred it from conversation.

### Storage lifecycle

```text
Human states a strategy that works for them
        ↓
D.AI.SY proposes remembering it
        ↓
Human explicitly approves
        ↓
UserStrategyMemory created
        ↓
MemoryStore
        ↓
Firestore in production
```

`MemoryService` retrieves only memories satisfying both conditions:

- `approved == true`
- `source == "user_explicit"`

This creates a code-level boundary between conversational inference and persistent user-owned memory.

### Use lifecycle

Permission to store something does not automatically grant permission to apply it later.

```text
Approved strategy exists
        ↓
D.AI.SY retrieves it
        ↓
D.AI.SY offers the strategy to the human
        ↓
Human chooses whether to use it here
        ↓
Only then is the current response adapted
```

This separates:

**Storage authority** from **use authority**.

That distinction is central to D.AI.SY's Collaborative Partner architecture.

---

## 7. Adaptive Guidance

When the human elects to use a remembered strategy, D.AI.SY adapts the current interaction rather than silently changing future behavior.

For the demonstrated strategy:

> Seeing the overall system first helps me understand new material.

D.AI.SY uses progressive disclosure:

1. present the big picture,
2. identify the major components,
3. show how the components relate,
4. ask the human where they want to zoom in.

The system therefore adapts to a strategy the human explicitly taught it without inferring a diagnosis, fixed identity, or permanent learning classification.

---

## 8. Human-Authorized Agentic Action

Agentic execution occurs downstream of human direction.

The implemented execution lifecycle is:

```text
Human establishes intent
        ↓
D.AI.SY creates a plan / proposed task
        ↓
Human authorizes execution
        ↓
Capability-based executor routing
        ↓
Task execution
        ↓
Observation captured
        ↓
Decision policy evaluates result
        ↓
At most one eligible bounded reasoning continuation
        ↓
Control returns to human
```

Authorization to execute a task is **not** interpreted as unlimited authorization to continue acting.

The system explicitly bounds continuation.

This creates the second major authority boundary:

**A proposed action does not become an executed action until the human authorizes it.**

---

## 9. Google ADK Reasoning Execution

The implemented ADK execution path is:

```text
Task
  ↓
AdkTaskExecutor
  ↓
Build bounded execution prompt
  ↓
google.adk.Agent
  ↓
google.adk.runners.InMemoryRunner
  ↓
Gemini 3.5 Flash-Lite
  ↓
ADK event output
  ↓
TaskExecutionResult
```

Each execution receives a new session identifier.

The executor is designed around one D.AI.SY task at a time rather than an open-ended autonomous session.

---

## 10. Claim and Evidence Boundaries

The ADK execution path includes explicit claim and evidence constraints.

The execution agent is instructed to distinguish D.AI.SY's actual capabilities from hypothetical products, businesses, services, or concepts discussed by the user.

It is also instructed not to present unsupported external facts, statistics, prices, market behavior, performance claims, availability claims, or business outcomes as established facts.

Unsupported material must instead be framed as:

- assumptions,
- hypotheses,
- estimates,
- illustrative examples, or
- items requiring validation.

The system is also instructed not to fabricate citations or imply that external verification occurred when it did not.

These boundaries are implemented in the execution prompt itself.

---

## 11. Persistence Architecture

D.AI.SY separates memory behavior from the underlying persistence technology.

```text
MemoryService
     │
     ▼
MemoryStore protocol
     │
     ├──────────────► InMemoryMemoryStore
     │                 local / test
     │
     └──────────────► FirestoreMemoryStore
                       production
                            │
                            ▼
                    Google Cloud Firestore
```

This allows deterministic local testing while using persistent cloud storage in the deployed environment.

Production memory has been verified across separate requests:

**proposal → explicit approval → Firestore persistence → later retrieval**

---

## 12. Deployment Topology

```text
Browser
  │
  ▼
React / Vite production frontend
  │
  │ HTTPS
  ▼
Google Cloud Run
D.AI.SY FastAPI backend
  │
  ├────────────► Firestore
  │              approved persistent strategy memory
  │
  └────────────► Google ADK
                   │
                   ▼
             Gemini 3.5 Flash-Lite
```

The frontend uses `VITE_API_BASE_URL` for its production backend location.

The backend uses environment configuration and Google Cloud Secret Manager references for sensitive runtime credentials.

Secrets are not embedded in frontend production configuration.

---

## 13. Architectural Safety and Agency Boundaries

D.AI.SY's architecture intentionally distinguishes assistance from authority.

### The system may

- clarify uncertainty,
- organize information,
- help surface a cognitive bottleneck,
- explain options,
- structure goals,
- propose plans,
- remember explicitly approved user-owned strategies,
- offer those strategies in later interactions,
- adapt after the human elects to use a strategy,
- propose executable work,
- execute bounded work after authorization,
- observe results,
- perform bounded reasoning about those results.

### The system does not treat these as automatic authority

- inference is not permission to remember,
- permission to remember is not permission to apply,
- a plan is not permission to execute,
- permission for one action is not unlimited continuation authority,
- conversational context is not evidence of a diagnosis,
- generated reasoning is not external verification.

The governing principle is:

**AI assists. Humans decide.**

---

## 14. Implemented vs. Future Architecture

This document describes the competition implementation as built.

### Implemented

- React conversation interface
- FastAPI backend
- Gemini 3.5 Flash-Lite integration
- Google ADK reasoning executor
- Google Cloud Run deployment
- Google Cloud Firestore persistent memory
- explicit memory proposal and approval
- approved-strategy retrieval
- separate permission to apply retrieved memory
- adaptive progressive-disclosure guidance
- cognition-first clarification
- planning and task orchestration
- capability-based execution routing
- observation and decision evaluation
- bounded reasoning continuation
- human authority boundaries

### Future / not claimed as implemented

The broader D.AI.SY product vision includes additional concepts such as a comprehensive **Growth Passport**, richer long-term growth records, broader integrations, and additional workflow capabilities.

Those concepts are not presented here as completed competition functionality.

---

## 15. Architectural Discipline

The competition implementation follows five primary architectural rules:

1. **Human authority before persistence or action.**
2. **Route according to need rather than forcing every conversation through a fixed agent pipeline.**
3. **Keep cloud persistence behind a replaceable storage boundary.**
4. **Keep model execution bounded by explicit claim and evidence constraints.**
5. **Make agentic action observable and return control to the human.**

Together these rules support D.AI.SY's central product objective:

**Helping people become more capable—not more dependent.**
