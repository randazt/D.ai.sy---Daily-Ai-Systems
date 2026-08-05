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
---

# growth_passports/

The growth_passports collection stores long-term, person-level memory that helps D.AI.SY provide continuity across all workspaces.

## Document ID

user_id

## Fields

| Field | Type | Description |
|------|------|-------------|
| goals | List<String> | Long-term user goals. |
| demonstrated_strengths | List<String> | Evidence-based strengths observed over time. |
| communication_preferences | List<String> | Preferred communication style. |
| learning_preferences | List<String> | Preferred methods of learning and understanding. |
| recurring_barriers | List<String> | Frequently observed cognitive barriers. |
| last_updated | Timestamp | Last successful Growth Passport update. |

### Engineering Notes

- Person-level only.
- Shared across every workspace.
- Updated only when evidence supports a meaningful change.
---

# workspace_memory/

The workspace_memory collection stores long-term, project-specific memory for each workspace.

Unlike the Growth Passport, which captures person-level growth, Workspace Memory preserves the evolving context of a single project over time.

## Document ID

workspace_id

## Fields

| Field | Type | Description |
|------|------|-------------|
| current_milestone | String | The active milestone for the workspace. |
| completed_milestones | List<String> | Milestones completed over the life of the workspace. |
| key_decisions | List<String> | Important project decisions that should persist across sessions. |
| open_questions | List<String> | Questions that remain unresolved. |
| next_agreed_step | String | The next agreed action for this workspace. |
| important_context | String | Persistent context that helps future conversations. |
| last_updated | Timestamp | Last Workspace Memory update. |

### Engineering Notes

- Workspace-specific only.
- Shared across every session within the workspace.
- Updated intentionally by the Growth Passport Agent.
- Stores evolving project knowledge rather than conversation history.
---

# sessions/

The sessions collection stores individual conversation sessions within a workspace.

Sessions preserve conversational history and the final Context Packet for auditing, continuity, and future reference. Sessions are distinct from long-term memory and should not be treated as the user's permanent knowledge.

## Document ID

session_id

## Fields

| Field | Type | Description |
|------|------|-------------|
| workspace_id | String | Reference to the parent workspace. |
| user_id | String | Reference to the owning user. |
| started_at | Timestamp | Session start time (UTC). |
| ended_at | Timestamp | Session end time (UTC). |
| status | Enum | Active, Completed, Paused, or Archived. |
| conversation_summary | String | Final summary of the conversation. |
| final_context_packet | Map | Snapshot of the completed Agent Context Packet. |

### Engineering Notes

- Sessions represent history, not memory.
- Multiple sessions may belong to the same workspace.
- The final Context Packet provides traceability and debugging support.
- Long-term learning is stored in Growth Passport or Workspace Memory instead of sessions.
---

# configuration/

The configuration collection stores application-wide settings, feature flags, prompts, and platform configuration that are not specific to any individual user.

This collection supports operational flexibility without requiring code changes for common configuration updates.

## Document ID

configuration_key

## Example Documents

- application_settings
- feature_flags
- supported_modes
- model_configuration
- prompt_templates

## Example Fields

| Field | Type | Description |
|------|------|-------------|
| enabled | Boolean | Whether the feature or configuration is active. |
| value | Any | Configuration value. |
| updated_at | Timestamp | Last configuration update. |
| updated_by | String | Administrative identifier responsible for the change. |

### Engineering Notes

- Contains platform-level configuration only.
- Never stores user-specific information.
- Supports gradual feature rollout and operational tuning.
- Changes should be versioned and auditable.
