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
---

# Barrier

The Barrier section is owned by the Barrier Detection Agent.

It captures the primary obstacle preventing meaningful progress during the current session.

| Field | Type | Required | Owner | Description |
|------|------|----------|-------|-------------|
| primary_barrier | String | Yes | Barrier Detection Agent | The single most significant barrier identified during the session. |
| confidence | Enum | Yes | Barrier Detection Agent | High, Medium, or Low confidence in the identified barrier. |
| supporting_evidence | String | Yes | Barrier Detection Agent | Evidence from the conversation supporting the identified barrier. |
| alternative_barriers | List<String> | Optional | Barrier Detection Agent | Other plausible barriers considered but not selected. |

### Engineering Notes

- Only one primary barrier should be identified.
- Confidence reflects the quality of available evidence, not certainty.
- Evidence should reference observable conversation content rather than assumptions.
- Downstream agents should treat the primary barrier as the current working hypothesis.
---

# Translation

The Translation section is owned by the Cognitive Translation Agent.

It transforms the user's thoughts into a structured understanding that reduces cognitive load while preserving important meaning.

| Field | Type | Required | Owner | Description |
|------|------|----------|-------|-------------|
| structured_summary | String | Yes | Cognitive Translation Agent | Concise structured explanation of the user's situation. |
| key_concepts | List<String> | Yes | Cognitive Translation Agent | Primary concepts extracted from the conversation. |
| known_information | List<String> | Yes | Cognitive Translation Agent | Facts and information established during the session. |
| unknown_information | List<String> | Optional | Cognitive Translation Agent | Important missing information that may affect planning. |
| simplified_problem | String | Yes | Cognitive Translation Agent | Clear statement of the problem after cognitive translation. |

### Engineering Notes

- Preserve nuance while improving clarity.
- Never invent missing information.
- Unknown information should remain explicitly identified rather than assumed.
- The simplified problem becomes the primary planning input.
---

# Planning

The Planning section is owned by the Planning Agent.

It converts structured understanding into one achievable action that helps the user build momentum.

| Field | Type | Required | Owner | Description |
|------|------|----------|-------|-------------|
| micro_win | String | Yes | Planning Agent | The smallest meaningful action the user can take next. |
| next_step | String | Yes | Planning Agent | The immediate recommended action following the Micro-Win. |
| future_milestones | List<String> | Optional | Planning Agent | A short sequence of future milestones if appropriate. |
| planning_notes | String | Optional | Planning Agent | Additional reasoning that may help downstream agents but is not shown directly to the user. |

### Engineering Notes

- Generate one Micro-Win first.
- Avoid overwhelming users with long task lists.
- Future milestones should remain flexible rather than prescriptive.
- Planning should support agency by offering guidance, not making decisions for the user.
---

# Reflection

The Reflection section is owned by the Reflection Agent.

It captures meaningful progress made during the session and reinforces the user's awareness without creating dependency.

| Field | Type | Required | Owner | Description |
|------|------|----------|-------|-------------|
| reflection_summary | String | Yes | Reflection Agent | Concise summary of the user's progress during the session. |
| evidence_based_strength | String | Yes | Reflection Agent | A genuine strength demonstrated during the conversation, supported by evidence. |
| reflection_question | String | Optional | Reflection Agent | One optional question that encourages continued self-reflection. |
| awareness_notes | String | Optional | Reflection Agent | Internal observations that may support future Growth Passport updates. |

### Engineering Notes

- Reflection should be grounded in evidence from the current session.
- Avoid generic praise or exaggerated encouragement.
- The reflection should reinforce awareness rather than dependence.
- Awareness notes are intended for internal use and are not shown directly to the user.
