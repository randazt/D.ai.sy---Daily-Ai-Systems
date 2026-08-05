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
