# D.AI.SY Product Vision

## Product Positioning

D.AI.SY (Daily AI Systems) is an adaptive cognitive accessibility and human-agency platform.

It helps people turn overwhelm, uncertainty, learning barriers, complex goals, and difficult workflows into understandable and achievable action.

D.AI.SY is not solely a chatbot, wellness assistant, therapy assistant, business automation tool, or workflow automation product. Conversation is one interface into a broader agentic system that supports human agency first and workflow agency second.

---

## Mission

Helping people become more capable—not more dependent.

Every interaction should reduce cognitive friction, increase clarity, encourage meaningful action, and strengthen long-term agency without replacing human judgment.

---

## Governing Principle

AI assists. Humans decide.

D.AI.SY can help clarify, organize, plan, execute eligible tasks, observe outcomes, and recommend next steps. It must preserve human authority over consequential choices, real-world actions, personal priorities, and value judgments.

---

## Human Agency

D.AI.SY helps users:

- Think something through
- Accomplish a goal
- Learn something
- Organize thoughts or information
- Make decisions
- Break down overwhelming or complex work
- Identify what kind of support would help

D.AI.SY adapts to the user's expressed barriers, preferences, and demonstrated needs. It must not infer limitations from a disability, diagnosis, identity, or label.

D.AI.SY may support someone who describes anxiety, overwhelm, executive-function barriers, or learning barriers by organizing information, clarifying choices, planning, learning, and taking manageable action. It must not diagnose, treat, cure, or provide therapy for medical or mental-health conditions.

---

## Workflow Agency

After understanding the human's goal and direction, D.AI.SY can help turn that direction into structured systems and workflows.

Examples include:

- Decomposing goals into tasks
- Building repeatable workflows
- Creating plans
- Executing eligible tasks
- Observing outcomes
- Recommending next steps
- Adapting plans
- Eventually connecting authorized tools and external actions

Workflow automation remains governed by human authority boundaries.

The intended relationship is:

Human direction → understanding → planning → workflow → execution → observation → adaptation → greater human capability

---

## Product Progression

Confusion → Clarity → Action → Confidence → Agency

Every product surface, agent behavior, workflow, and design decision should help users move along this progression without hiding uncertainty or overstating capability.

---

## Current Agentic Loop

The current implementation demonstrates this loop:

Goal → Human-Decision Boundary → Clarify When Needed → Human Direction → Adaptive Plan → Execute → Observe → Decide → Bounded Continuation

The product experience should make this understandable to ordinary users without requiring them to understand agent architecture.

---

## Product Entry Points

The planned Home experience should support four primary starting points:

- Help me think something through
- Help me accomplish a goal
- Help me learn something
- Help me build a workflow

These are UX entry points into the same underlying D.AI.SY agent system, not separate products.

---

## Current Capability Boundary

Implemented current capabilities:

- Conversation through `/chat`
- Human-decision clarification
- Adaptive planning
- Structured projects and tasks
- Capability routing
- Reasoning execution
- Task observation
- Task decision
- Bounded autonomous continuation
- Human authority boundaries
- Claim and evidence boundaries
- Gemini integration
- Google ADK reasoning execution
- Cloud Run deployment
- CALL-E executor with real calls disabled by default

Planned capabilities that are not yet implemented as full product features:

- Persistent user accounts
- Authentication
- Persistent conversations
- Persistent goals or projects across sessions
- Durable activity history
- Firestore-backed memory
- Long-term preference memory
- Notifications
- Growth Passport storage and history
- Weekly metrics and wins
- Persistent personal dashboard
- Production integrations UI
- Full workflow builder UI

Planned capabilities must remain documented as planned until implementation and verification evidence exists.

---

## Growth Passport

The Growth Passport is planned as a user-owned record of strategies and growth the person can understand and control.

It may record:

- Strategies that helped
- Accomplishments
- Skills developed
- Decisions made
- Preferences explicitly expressed by the user
- Demonstrated progress and growth

It must not be framed as:

- A diagnostic profile
- A deficit profile
- An inferred disability profile
- An AI judgment of the person's limitations

The Growth Passport should preserve agency by making useful patterns visible to the user, not by defining the user.

---

## Planned Product Surfaces

- Home / Today
- Conversations
- Goals
- Workflows
- Tasks
- Decisions
- Growth Passport
- Activity
- Integrations
- Knowledge / Resources
- Settings

---

## Frontend Experience Direction

The approved visual direction is calm, capable, warm, structured, accessible, and trustworthy.

The interface should not feel like a generic chatbot, a generic enterprise dashboard, or an AI startup purple-gradient product. It should visually expose human direction, goals, workflows, decisions, tasks, progress, observations, and user authority.

The daisy identity may be used subtly as a visual metaphor: the human is central, and capabilities and growth surround and support them.

---

## Product Experience Roadmap

### Phase 5A — Product Shell

- Responsive frontend
- D.AI.SY visual system
- Navigation
- Home experience

### Phase 5B — Live Conversation

- Connect existing `/chat` API
- Render conversation
- Support clarification
- Render planning and execution responses

### Phase 5C — Project & Workflow Workspace

- Goals
- Plans
- Task states
- Workflow visualization
- Observations
- Decisions
- Bounded continuation

### Phase 5D — Human Agency UX

- Explicit decision cards
- Approval boundaries
- Evidence and hypothesis indicators
- Clear AI-vs-human authority states
- Accessible breakdown of complex work

### Phase 5E — Persistence

- Authentication
- Firestore
- Durable conversations
- Durable projects and goals
- Activity history

### Phase 5F — Personal D.AI.SY

- Today experience
- Continuity
- Growth Passport
- User-controlled preferences
- Progress and agency visualization

These phases are planned product work. They should not be marked complete until implemented and verified.

---

## Long-Term Vision

D.AI.SY should become a trusted platform for helping people think more clearly, make better decisions, build useful workflows, and become increasingly capable over time.
