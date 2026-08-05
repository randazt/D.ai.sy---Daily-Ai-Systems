# D.AI.SY Firestore Data Model

## Purpose

This document defines the Firestore collections, documents, and relationships used by D.AI.SY.

The data model is derived directly from the Agent Context Packet and supports long-term user growth, session continuity, and multi-agent orchestration.

---

# Design Principles

- Separate session data from long-term memory.
- Store only information that improves future conversations.
- Avoid unnecessary duplication.
- Keep documents focused and extensible.
- Support efficient retrieval for Google ADK agents.

---

# Top-Level Collections

users/

workspaces/

sessions/

growth_passports/

system/

---

# Collection Responsibilities

| Collection | Purpose |
|------------|---------|
| users | User identity and profile information. |
| workspaces | Named workspaces such as "Launch D.AI.SY MVP". |
| sessions | Individual conversation sessions. |
| growth_passports | Long-term user memory and agency development. |
| system | Configuration and platform metadata. |

---

# Engineering Rule

Session data is temporary.

Growth Passport data is persistent.

Agents retrieve only the information required for the current workflow.
