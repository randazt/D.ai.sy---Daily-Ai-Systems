# D.AI.SY Version 1 — System Overview

## High-Level Architecture

```
                         USER
                           │
                           ▼
                Conversation Workspace
                           │
                           ▼
                Conversation Agent
                           │
     ┌──────────────┬──────────────┬──────────────┐
     ▼              ▼              ▼              ▼
Barrier Agent   Translation   Planning Agent   Reflection
                     Agent
                           │
                           ▼
                 Growth Passport Agent
                           │
                           ▼
                      Firestore DB
                           │
                           ▼
                    Google Cloud
```

---

## External Services

- Gemini
- Google ADK
- Firestore
- Cloud Run
- GitHub

---

## Internal Components

- Conversation Agent
- Barrier Detection Agent
- Cognitive Translation Agent
- Planning Agent
- Reflection Agent
- Growth Passport Agent

---

## User Experience

The user communicates only with the Conversation Agent.

All remaining agents operate behind the scenes through structured context packets.

---

## Core Design Principles

- One Conversation
- One Voice
- Many Specialized Agents
- Agency Before Automation
- Persistent Growth
- Human Decision Authority
---

# Agent Specifications

## Conversation Agent

### Purpose

Acts as the single entry and exit point for all user interactions.

### Responsibilities

1. Receive the user's message.
2. Load the user's Growth Passport.
3. Create the Agent Context Packet.
4. Initiate the multi-agent workflow by sending the packet to the Barrier Detection Agent.
5. Receive the completed Context Packet from the Growth Passport Agent.
6. Generate and deliver the final response to the user.

### Owns

- User session
- Conversation state
- Agent orchestration
- Final response generation

### Does Not Own

- Barrier identification
- Cognitive translation
- Planning
- Reflection
- Long-term memory
