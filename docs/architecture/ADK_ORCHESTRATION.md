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
