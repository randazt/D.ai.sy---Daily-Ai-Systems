# D.AI.SY Submission Evidence Index

This document maps the major claims for the D.AI.SY All Things Agentic Hackathon submission to implementation evidence, automated verification, production verification, and final submission artifacts.

It is an evidence index, not a roadmap. Claims listed as verified are limited to behavior or architecture demonstrated in code, automated tests, deployed infrastructure, or production acceptance checks.

It intentionally excludes secret values, authorization-token values, fabricated timestamps, unsupported external claims, and unpublished artifact URLs.

**Target category:** Collaborative Partner
**Core principle:** AI assists. Humans decide.

---

## 1. Verified Production Baseline

### Google Cloud

- GCP project: `daisy-agentic-2026`
- Cloud Run service: `daisy-backend`
- Region: `us-east1`
- Verified production revision: `daisy-backend-00008-mzv`
- Production backend URL: `https://daisy-backend-490172530660.us-east1.run.app`
- Runtime service account: `daisy-runtime@daisy-agentic-2026.iam.gserviceaccount.com`
- Firestore database: `(default)`
- Firestore mode: Native
- Production memory store configuration: `DAISY_MEMORY_STORE=firestore`

### Google AI Stack

- Gemini model configured for the competition implementation: `gemini-3.5-flash-lite`
- Google GenAI SDK dependency: `google-genai>=2.12,<3.0`
- Google ADK dependency: `google-adk>=2.7,<3.0`
- Firestore dependency: `google-cloud-firestore>=2.21,<3.0`
- Google ADK production path uses `google.adk.Agent`
- Google ADK production path uses `google.adk.runners.InMemoryRunner`

### Frontend

- React/Vite production frontend is configured to call the deployed Cloud Run backend through `VITE_API_BASE_URL`.
- Browser-to-Cloud-Run cross-origin operation has been verified.
- Production CORS configuration permits the verified frontend origin without embedding backend credentials in the frontend.

### Automated Regression Baseline

**236 backend tests passed.**

The final verified backend regression completed successfully after the production CORS and security changes.

Final repository SHA for the submitted package remains **TBD until packaging**.

---

## 2. Competition Stack Qualification

| Requirement | Status | Evidence |
|---|---|---|
| Gemini 3.5 or newer | VERIFIED | Competition configuration uses `gemini-3.5-flash-lite`. Gemini-backed production responses were exercised through the deployed backend. |
| Google Agent Framework | VERIFIED | Production code implements an ADK reasoning path using `google.adk.Agent` and `google.adk.runners.InMemoryRunner`. |
| Google Cloud infrastructure | VERIFIED | FastAPI backend is deployed on Google Cloud Run and approved strategy memory is persisted in Google Cloud Firestore. |
| Deployed backend | VERIFIED | `daisy-backend` is deployed in `us-east1`; production endpoint and browser-to-backend behavior were verified. |
| Persistent cloud state | VERIFIED | Explicitly approved strategy memory was persisted in Firestore and retrieved during a later request. |

---

## 3. Collaborative Partner Evidence

D.AI.SY's strongest Collaborative Partner evidence is the combination of stateful dialogue, explicit human-owned memory, later retrieval, adaptive guidance, and preservation of human decision authority.

### Verified memory lifecycle

```text
Human states a strategy that works for them
        ↓
D.AI.SY proposes remembering it
        ↓
Human explicitly approves
        ↓
Strategy is persisted in Firestore
        ↓
A later request retrieves the approved strategy
        ↓
D.AI.SY offers the strategy to the human
        ↓
Human decides whether to use it
        ↓
Current guidance adapts only after permission
```

This demonstrates persistent state while maintaining two distinct permissions:

**permission to store ≠ permission to use**

---

## 4. Evidence Matrix

| Area | Status | Implementation / automated evidence | Production behavioral evidence | Submission use |
|---|---|---|---|---|
| Cognition-first clarification | VERIFIED | `ChatService` evaluates a deterministic cognitive-bottleneck decision before ordinary routing. Dedicated clarification regressions cover the behavior. | A cognition-oriented prompt produced clarification before planning or execution. | Lead demo: show D.AI.SY understanding where the human is stuck before prescribing action. |
| Human-owned strategy memory | VERIFIED | Memory flow supports proposal, explicit approval, approved-memory filtering, retrieval, and application boundaries. | A user-owned strategy produced `approval_required`; explicit approval produced `remembered`. | Show visible `Remember this` / `Not now` authority boundary. |
| Firestore persistence | VERIFIED | `FirestoreMemoryStore` implements the production `MemoryStore` persistence boundary. | Approved `user_explicit` strategy was read directly from Firestore after Cloud Run approval. | Architecture/demo evidence for persistent state. |
| Cross-request memory retrieval | VERIFIED | `MemoryService` retrieves only approved memories with `source == "user_explicit"`. | A later Cloud Run request returned `strategy_available` with the previously approved strategy and matching memory identity. | Core Collaborative Partner evidence. |
| Separate memory-use authority | VERIFIED | Retrieval and application are separate actions in the memory/chat flow. | An approved strategy can be offered without automatically applying it. | Demonstrate “Would you like me to use that approach here?” |
| Adaptive guidance | VERIFIED | Approved strategy application routes into adaptive guidance using progressive disclosure. | Verified flow supports system-first adaptation after human permission. | Show big picture → components → relationships → human chooses where to zoom in. |
| Human-decision boundary | VERIFIED | Clarification logic pauses consequential interpretation when human direction is required. | Clarification is returned before downstream planning where the human must resolve the direction. | Reinforces “AI assists. Humans decide.” |
| Planning / workflow agency | VERIFIED | Planner and workflow components transform established human direction into structured proposed work. | Live execution flow demonstrated planning/task selection before bounded execution. | Transition from clarity into practical everyday workflow agency. |
| Explicit execution authority | VERIFIED | Execution is downstream of proposed work and human authorization rather than inferred from conversational intent alone. | Verified execution flow occurred through the explicit execution path. | Show the second authority boundary before agentic action. |
| Capability-based task execution | VERIFIED | `ExecutionAgent`, `CapabilityRegistry`, workflow engine, observations, and decisions implement bounded task execution. | Production execution returned execution evidence, observation, and decision information. | Proof of Action. |
| Bounded continuation | VERIFIED | Workflow engine permits at most one eligible reasoning continuation and prevents recursive autonomous continuation. | Live bounded execution demonstrated decision/continuation evaluation and return of control to the user. | Show that execution authority is bounded rather than open-ended. |
| Google ADK execution | VERIFIED | `AdkTaskExecutor` creates `google.adk.Agent` and executes it through `InMemoryRunner`. | Deployed reasoning/execution architecture uses the configured Gemini/ADK path. | Architecture and technical-stack proof. |
| Gemini 3.5+ | VERIFIED | Competition model configuration defaults to `gemini-3.5-flash-lite`. | Cloud Run `/chat` returned a substantive Gemini-generated response. | Mandatory stack evidence. |
| Claim boundary | VERIFIED | ADK execution instructions prevent hypothetical user products or concepts from being represented as implemented D.AI.SY capabilities. | Reviewed execution behavior preserved the product/candidate distinction. | Architectural-discipline evidence. |
| Evidence boundary | VERIFIED | ADK instructions require unsupported facts to be framed as assumptions, hypotheses, estimates, examples, or validation targets. | Reviewed behavior did not present unsupported external assertions as verified facts. | Safety and architectural-discipline evidence. |
| Production frontend | VERIFIED | `chatApi.ts` uses `VITE_API_BASE_URL`; production build contains the Cloud Run backend target. | Production frontend in a browser successfully sent the lead prompt to deployed Cloud Run and rendered D.AI.SY's response. | Demo can show the actual product UI rather than API-only interaction. |
| Cloud Run deployment | VERIFIED | FastAPI backend and Docker configuration support Cloud Run deployment. | Production service is live and served verified requests. | Required Google Cloud proof in demo. |
| CORS / browser integration | VERIFIED | Backend CORS middleware uses configured allowed origins and bounded methods/headers. | Browser preflight succeeded and cross-origin `/chat` request completed. | Supports hosted/deployed product proof. |
| Security / request logging | VERIFIED | Raw chat-request logging was removed from the API endpoint. | Full backend regression passed after the security change. | Do not expose user message bodies or secrets in Cloud logs during recording. |
| Secret handling | VERIFIED WITH OPERATIONAL CAUTION | Runtime secrets use environment/Secret Manager configuration rather than frontend embedding. `.env` is not currently tracked. | Cloud Run uses secret references for sensitive runtime configuration. | Never show secret payloads, API keys, token values, or credential material in the demo. |
| Automated regression | VERIFIED | Final backend regression: 236 tests passed. | Production verification followed deployment changes. | Repository/readiness evidence. |
| New-project implementation provenance | VERIFIED WITH DISCLOSURE | Git history shows repository implementation beginning during the competition period, with first repository commit August 4, 2026 and implementation commits thereafter. | Not applicable. | Disclose that the D.AI.SY concept predates the hackathon while the submitted software implementation was built during the competition period. |

---

## 5. Production Memory Proof

The production memory path has been verified end to end.

### Proposal

A strategy explicitly stated by the human was submitted to the deployed Cloud Run backend.

The response identified the memory flow and returned:

- `agent = memory`
- `status = approval_required`
- the proposed strategy
- an expiration boundary for the authorization context

No persistence was treated as authorized at proposal time.

### Approval

After explicit human approval, the deployed backend returned:

- `agent = memory`
- `status = remembered`
- the approved strategy

### Firestore persistence

The production Firestore record was then read through the Firestore-backed memory store.

The stored record was:

- approved,
- sourced as `user_explicit`,
- associated with the synthetic verification client,
- and contained the explicitly approved strategy.

### Later retrieval

A separate Cloud Run request subsequently retrieved the strategy.

The memory response returned:

- `status = strategy_available`
- the previously approved strategy
- the corresponding memory identity

This provides direct production evidence for:

**Cloud Run → explicit proposal → human approval → Firestore persistence → later retrieval**

---

## 6. Production Frontend Proof

The production frontend configuration was built with:

```text
VITE_API_BASE_URL=https://daisy-backend-490172530660.us-east1.run.app
```

The compiled production frontend was verified to contain the Cloud Run API base and to send conversation requests to the deployed `/chat` endpoint.

The deployed backend CORS configuration was verified for the production-preview browser origin.

A browser running the production frontend successfully submitted the lead D.AI.SY prompt and rendered the response returned by deployed Cloud Run.

This establishes the demonstrated path:

```text
Production React frontend
        ↓
cross-origin HTTPS request
        ↓
Google Cloud Run
        ↓
D.AI.SY conversation logic
        ↓
browser-rendered response
```

---

## 7. Agentic Action Proof

D.AI.SY's agentic behavior is intentionally downstream of human authority.

The implemented execution path includes:

```text
human direction
    ↓
proposed work
    ↓
human authorization
    ↓
capability routing
    ↓
task execution
    ↓
TaskObservation
    ↓
TaskDecision
    ↓
optional one-step eligible reasoning continuation
    ↓
control returned to human
```

A `continue` decision does not authorize unrestricted execution.

The workflow engine permits at most one automatic continuation, and that continuation must satisfy the implemented eligibility boundary.

This is a deliberate architectural constraint rather than an absence of agentic behavior.

---

## 8. Proof of Action

The submission should use observable behavior rather than relying only on architectural narration.

Available verified proof includes:

- browser UI changing in response to deployed backend behavior,
- explicit memory-approval state,
- Firestore persistence of an approved strategy,
- later retrieval of that persistent strategy,
- planning/task state,
- task execution output,
- `TaskObservation`,
- execution decision,
- bounded continuation or explicit continuation skip,
- return of control to the human,
- Cloud Run service/revision evidence.

The final demo should connect these into one understandable human story rather than presenting them as isolated infrastructure tests.

---

## 9. Human Authority Boundaries

D.AI.SY implements two primary authority boundaries.

### Cognitive authority

```text
May D.AI.SY remember this?
        ↓
human decides

May D.AI.SY use the remembered strategy here?
        ↓
human decides
```

### Action authority

```text
Here is the work D.AI.SY proposes.
        ↓
human decides whether execution occurs
        ↓
authorized bounded execution
        ↓
control returns to human
```

These boundaries support the product principle:

**AI assists. Humans decide.**

---

## 10. New Projects Only / Provenance Evidence

The D.AI.SY concept predates the hackathon.

The software implementation submitted to the All Things Agentic Hackathon was built during the competition period.

Repository history shows:

- first repository commit: **August 4, 2026**
- first backend scaffolding: **August 5, 2026**
- first working backend source implementation: **August 5, 2026**
- subsequent frontend, memory, Firestore, adaptive-guidance, agentic-execution, production, security, and documentation work occurring during the competition period

The repository history audit did not identify pre-August-3 implementation ancestry for the submitted software.

### Submission disclosure wording

Use:

> The D.AI.SY concept predates the hackathon. The software implementation submitted to the All Things Agentic Hackathon was built during the competition period, with repository development beginning August 4, 2026.

Do not claim that the D.AI.SY idea itself originated during the competition.

---

## 11. Security and Evidence Boundaries

Final submission materials must not expose:

- Gemini API key values,
- clarification authorization secrets,
- memory authorization secrets,
- authorization-token values,
- credential payloads,
- unnecessary billing information,
- private user-message bodies from logs.

Any credential that may previously have appeared in development history or external working material should be treated as potentially compromised and rotated/revoked where applicable.

The final demo should show Cloud Run service identity, revision, deployment status, or safe logs without exposing secret material.

---

## 12. Claims We Can Make

The verified implementation supports claims that D.AI.SY:

- uses Gemini 3.5 Flash-Lite,
- uses Google ADK for bounded reasoning execution,
- runs its backend on Google Cloud Run,
- persists explicitly approved strategy memory in Google Cloud Firestore,
- supports stateful multi-turn interaction,
- asks clarifying questions before certain consequential downstream actions,
- allows humans to explicitly approve persistent strategy memory,
- retrieves approved memory in later requests,
- separately asks whether retrieved strategy should be used,
- adapts guidance after human permission,
- turns human direction into structured proposed work,
- supports human-authorized bounded task execution,
- captures observable execution results,
- evaluates execution results,
- permits at most one eligible bounded reasoning continuation,
- returns control to the human.

---

## 13. Claims We Must Not Make

Do not claim that D.AI.SY:

- diagnoses anxiety, learning disabilities, cognitive conditions, or other medical/psychological conditions,
- automatically determines a user's permanent learning style,
- automatically stores inferred personal traits,
- applies remembered strategies without user authority,
- autonomously executes consequential work without authorization,
- has unrestricted recursive autonomy,
- verifies external facts when it has not done so,
- has implemented a comprehensive Growth Passport,
- has implemented broader integrations that were not completed and verified,
- has implemented RAG or external knowledge retrieval if the submitted build does not contain and demonstrate it,
- originated as a concept during the hackathon.

Do not represent future product concepts as completed competition functionality.

---

## 14. Demo Evidence Priority

The final demo should prioritize evidence in this order:

1. **Human understanding** — D.AI.SY clarifies the person's actual bottleneck.
2. **Human-owned adaptation** — the person teaches D.AI.SY a strategy and explicitly controls whether it is remembered and used.
3. **Persistent collaboration** — Firestore-backed memory is available in a later interaction.
4. **Workflow agency** — human direction becomes a practical plan or workflow.
5. **Human-authorized agentic action** — execution occurs only after authority is granted.
6. **Observable action** — result, observation, decision, bounded continuation, and return of control are visible.
7. **Google production architecture** — Cloud Run, Firestore, Google ADK, and Gemini are shown clearly enough for judges to verify the stack.

The narrative should demonstrate:

**D.AI.SY helps the human become more capable before D.AI.SY becomes more autonomous.**

---

## 15. Final Packaging TBD

The following remain intentionally unresolved until final packaging:

- final submitted repository SHA,
- final repository URL/state,
- final demo video URL,
- final screenshot/image selection,
- final hosted frontend URL if one is submitted,
- final Devpost description,
- final Devpost technology list,
- final findings/learnings copy,
- final architecture-diagram presentation format,
- final submission timestamp.

These items must be verified before submission rather than inferred in advance.

---

## 16. Final Evidence Rule

Every material submission claim should be supportable by at least one of:

1. implementation evidence,
2. automated test evidence,
3. production behavioral evidence,
4. visible demo evidence.

Where those forms of evidence do not exist, the capability should be described as future work, a product direction, or omitted.

The final submission should optimize for demonstrated capability rather than maximum claim count.

**Helping people become more capable—not more dependent.**
