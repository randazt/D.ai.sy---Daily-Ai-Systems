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
---

# users/

The users collection stores identity information required to authenticate and personalize the D.AI.SY experience.

Each authenticated user owns one or more workspaces and one Growth Passport.

## Document ID

user_id

## Fields

| Field | Type | Description |
|------|------|-------------|
| display_name | String | User's preferred display name. |
| email | String | Authentication email address. |
| created_at | Timestamp | Account creation date (UTC). |
| last_active | Timestamp | Last time the user interacted with D.AI.SY. |
| default_workspace | String | ID of the workspace opened by default. |
| preferences | Map | User-level application preferences. |

### Relationships

User

├── Workspaces

├── Sessions

└── Growth Passport
---

# workspaces/

The workspaces collection represents the user's ongoing projects, goals, or areas of focus.

Unlike traditional AI chat applications that organize information around conversations, D.AI.SY organizes work around persistent workspaces that accumulate progress over time.

## Document ID

workspace_id

## Fields

| Field | Type | Description |
|------|------|-------------|
| owner_id | String | References the owning user. |
| title | String | Human-readable workspace name. |
| description | String | Optional description of the workspace. |
| status | Enum | Active, Paused, Completed, or Archived. |
| created_at | Timestamp | Workspace creation date (UTC). |
| last_updated | Timestamp | Last modification timestamp. |
| active_session_id | String | Reference to the currently active session, if any. |
| tags | List<String> | User-defined organizational tags. |

### Relationships

Workspace

├── Sessions

├── Context Packets (current)

└── Growth Passport updates

### Engineering Notes

- A workspace may contain many sessions.
- A user may return to the same workspace over months or years.
- Sessions capture conversations.
- Workspaces capture long-term progress toward meaningful goals.
