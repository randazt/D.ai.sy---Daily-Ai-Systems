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
