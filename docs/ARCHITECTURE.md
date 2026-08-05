# D.AI.SY System Architecture

> This document defines the technical architecture of D.AI.SY Version 1.

The purpose of this document is to describe how the internal agents cooperate to create a single, seamless experience for the user.

The user interacts with one conversational interface.

Behind the scenes, specialized agents collaborate to identify barriers, translate complexity, build plans, encourage reflection, and preserve meaningful progress through the Growth Passport.
---

# Architecture Decisions

## Decision A001 — Version 1 System Flow

**Status:** ✅ Approved

### Statement

D.AI.SY operates as a coordinated multi-agent system. Each user request passes through a structured sequence of specialized agents before a unified response is returned.

### System Flow

User

↓

Conversation Agent

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

Response to User

### Design Principle

The user interacts with one unified D.AI.SY experience. The internal agent orchestration remains invisible to the user.
---

## Decision A002 — Conversation Orchestration

**Status:** ✅ Approved

### Statement

The Conversation Agent is the only agent that communicates directly with the user.

All other agents operate internally and return structured information to the Conversation Agent.

### Why

Maintaining a single conversational interface provides a consistent personality, reduces cognitive load, and keeps the internal architecture hidden from the user.

### Design Principle

One conversation.

One voice.

Many specialized agents.
---

## Decision A003 — Agent Communication

**Status:** ✅ Approved

### Statement

Agents communicate using structured data rather than natural language.

### Why

Structured communication improves consistency, simplifies debugging, reduces ambiguity, and allows each agent to focus on its specific responsibility.

### Design Principle

Agents exchange structured outputs.

Only the Conversation Agent communicates in natural language with the user.
---

## Decision A004 — Agent Context Packet

**Status:** ✅ Approved

### Statement

All agents exchange information using a shared Agent Context Packet. Each agent may read existing fields and append new information before passing the packet to the next agent.

### Version 1 Fields

- Active Mode
- User Goal
- Conversation Summary
- Primary Barrier
- Barrier Confidence
- Cognitive Translation
- Suggested Micro-Win
- Reflection Prompt
- Growth Passport Update
- Timestamp

### Design Principle

Each agent contributes to a shared understanding of the conversation rather than maintaining separate, isolated context.
---

## Decision A005 — Platform Responsibility

**Status:** ✅ Approved

### Statement

Gemini serves as D.AI.SY's reasoning engine. D.AI.SY owns the user experience, workflow orchestration, cognitive methodology, agent coordination, and Growth Passport.

### Gemini Responsibilities

- Natural language understanding
- Reasoning
- Summarization
- Structured generation

### D.AI.SY Responsibilities

- User experience
- Agent orchestration
- Cognitive Translation methodology
- Barrier Detection workflow
- Planning workflow
- Reflection workflow
- Growth Passport management
- Long-term continuity

### Design Principle

AI models may evolve over time. The D.AI.SY methodology and architecture remain platform-owned and model-independent.
---

## Decision A006 — Human Decision Authority

**Status:** ✅ Approved

### Statement

D.AI.SY supports human decision-making but does not replace it. Final decisions always remain with the user.

### Design Principle

Agents may:

- organize information
- identify barriers
- generate options
- explain tradeoffs
- recommend next steps

Agents do not:

- make high-stakes decisions
- remove meaningful user choice
- optimize for dependence
- override user judgment

### User Experience Principle

Whenever appropriate, D.AI.SY should encourage the user to exercise their own judgment by asking questions such as:

- "Which option feels most doable?"
- "What do you think your next step is?"
- "Would you like to try first, then I'll help refine?"
