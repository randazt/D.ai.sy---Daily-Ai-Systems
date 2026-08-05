# D.AI.SY Agent Context Packet

## Purpose

The Agent Context Packet is the shared data structure used by every D.AI.SY agent.

Each agent receives the current packet, updates only the section it owns, and returns the updated packet to the Conversation Agent.

The Context Packet is owned by D.A.I.SY—not by Gemini, Google ADK, or any individual AI model.

This allows the platform to evolve independently of the underlying reasoning engine.

---

# Design Principles

- Single shared context
- Clear ownership
- Minimal duplication
- Structured communication
- Extensible architecture
- Model-agnostic design

---

# Packet Structure

```yaml
AgentContext

Session
Conversation
Barrier
Translation
Planning
Reflection
GrowthPassport
```

---

# Ownership

| Section | Owning Agent |
|----------|--------------|
| Session | Conversation Agent |
| Conversation | Conversation Agent |
| Barrier | Barrier Detection Agent |
| Translation | Cognitive Translation Agent |
| Planning | Planning Agent |
| Reflection | Reflection Agent |
| GrowthPassport | Growth Passport Agent |

---

# Engineering Rule

Each agent may only modify the section(s) it owns.

Agents may read any section.

The Conversation Agent is responsible for coordinating the complete packet throughout the workflow.
---

# Session

The Session section is owned by the Conversation Agent.

It contains information required to identify the active conversation and user.

| Field | Type | Required | Owner | Description |
|------|------|----------|-------|-------------|
| session_id | UUID | Yes | Conversation Agent | Unique identifier for the current conversation session. |
| user_id | UUID | Yes | Conversation Agent | Authenticated user identifier. |
| timestamp | DateTime (UTC) | Yes | Conversation Agent | Time the packet was last updated. |
| active_mode | Enum | Yes | Conversation Agent | Current interaction mode (Default, Guided, Planning, Reflection, etc.). |
| workspace_name | String | Yes | Conversation Agent | Human-readable name for the current workspace or session. |

### Engineering Notes

- Created at the beginning of every session.
- Updated by the Conversation Agent.
- Read by every downstream agent.
- Never modified by specialist agents.
---

# Conversation

The Conversation section is owned by the Conversation Agent.

It contains the active conversational state that downstream agents use for reasoning.

| Field | Type | Required | Owner | Description |
|------|------|----------|-------|-------------|
| latest_user_message | String | Yes | Conversation Agent | The user's most recent message. |
| conversation_summary | String | Yes | Conversation Agent | Running summary of the current session. |
| session_goal | String | Optional | Conversation Agent | The primary objective for the current workspace. |
| conversation_status | Enum | Yes | Conversation Agent | Active, Completed, Paused, or Archived. |
| support_mode | Enum | Yes | Conversation Agent | Current support approach (Default, Guided, Planning, Reflection, Brainstorming). |

### Engineering Notes

- Updated after every user message.
- Serves as the primary context for all downstream agents.
- Conversation summaries should be concise and continuously refined rather than storing full transcripts.
- Full message history remains outside the Context Packet.
