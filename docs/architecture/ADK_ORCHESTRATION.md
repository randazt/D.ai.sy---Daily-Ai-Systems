# D.AI.SY ADK Orchestration

## Purpose

This document defines how D.AI.SY executes a conversation using Google ADK.

It specifies the order of agent execution, when memory is loaded and updated, and how the Agent Context Packet flows through the system.

The orchestration layer is responsible for coordinating specialized agents while presenting the user with a single, seamless conversation.

---

# Design Principles

- One conversation experience
- Specialized agents
- Shared Context Packet
- Explicit memory lifecycle
- Model-agnostic architecture
- Fail gracefully
- Preserve user agency

---

# High-Level Workflow

User Message

↓

Conversation Agent

↓

Load User Profile

↓

Load Growth Passport

↓

Load Workspace Memory

↓

Create Agent Context Packet

↓

Barrier Detection Agent

↓

Cognitive Translation Agent

↓

Planning Agent

↓

Reflection Agent

↓

Growth Passport Agent

↓

Persist Workspace Memory

↓

Persist Growth Passport

↓

Conversation Agent

↓

Generate Final Response

↓

Return Response to User
---

# Conversation Lifecycle

Each conversation follows the same execution pipeline.

## Phase 1 — Session Initialization

1. Receive user message.
2. Authenticate user.
3. Identify active workspace.
4. Load User Profile.
5. Load Growth Passport.
6. Load Workspace Memory.
7. Create Agent Context Packet.

---

## Phase 2 — Cognitive Processing

The Context Packet is processed sequentially by specialized agents.

1. Barrier Detection Agent
2. Cognitive Translation Agent
3. Planning Agent
4. Reflection Agent
5. Growth Passport Agent

Each agent:

- Reads the complete Context Packet.
- Updates only its owned section.
- Returns the updated packet.

---

## Phase 3 — Response Generation

The Conversation Agent:

- Reviews the completed Context Packet.
- Synthesizes agent outputs.
- Produces a single coherent response.
- Preserves D.AI.SY's voice and philosophy.

---

## Phase 4 — Persistence

After the response is generated:

- Update Workspace Memory.
- Update Growth Passport.
- Store completed Context Packet.
- Store Session summary.
- Update workspace metadata.

---

## Phase 5 — Completion

Return the response to the user.

Await the next interaction.
---

# Execution Rules

## Context Packet

- A single Agent Context Packet exists for each active session.
- The Conversation Agent creates and manages the packet.
- Every specialist agent receives the latest packet.
- Every specialist agent returns the updated packet.

---

## Agent Ownership

Each specialist agent:

- Reads the entire Context Packet.
- Updates only the section it owns.
- Must never modify another agent's section.

---

## Failure Handling

If an agent cannot produce a confident result:

- Record the uncertainty.
- Preserve previous context.
- Return control to the Conversation Agent.

The Conversation Agent may:

- ask a clarifying question,
- continue with reduced confidence,
- or bypass the uncertain result.

---

## Memory Lifecycle

Read

User Profile

↓

Growth Passport

↓

Workspace Memory

↓

Conversation

↓

Context Packet

↓

Specialist Agents

↓

Final Response

↓

Update Workspace Memory

↓

Update Growth Passport

↓

Archive Session

---

## Design Goals

- Preserve user agency.
- Reduce cognitive load.
- Avoid fabricated conclusions.
- Keep reasoning transparent.
- Fail gracefully.
- Maintain a single conversational experience.
