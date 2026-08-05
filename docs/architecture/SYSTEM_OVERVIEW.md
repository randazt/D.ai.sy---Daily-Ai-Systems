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
---

## Barrier Detection Agent

### Purpose

Identifies the user's primary cognitive barrier based on the current conversation.

### Responsibilities

1. Analyze the user's message.
2. Identify the most likely primary barrier.
3. Assign a confidence level (High / Medium / Low).
4. Record supporting evidence for the identified barrier.
5. Update the Agent Context Packet with the barrier analysis.

### Outputs

- Primary Barrier
- Confidence Level
- Supporting Evidence

### Owns

- Barrier identification
- Confidence assessment
- Evidence collection

### Does Not Own

- Cognitive translation
- Planning
- Reflection
- Growth Passport updates
- Final response generation

### Design Principle

Identify the single most significant barrier first. Avoid diagnoses, assumptions, or unnecessary complexity.
---

## Cognitive Translation Agent

### Purpose

Transforms complex thoughts into clear, structured understanding while preserving important meaning.

### Responsibilities

1. Read the Agent Context Packet.
2. Analyze the identified primary barrier.
3. Organize information into a clear structure.
4. Reduce unnecessary cognitive load.
5. Preserve important context and nuance.
6. Update the Agent Context Packet.

### Outputs

- Structured Summary
- Key Concepts
- Known Information
- Unknown Information
- Simplified Problem Statement

### Owns

- Cognitive translation
- Information organization
- Complexity reduction
- Structural clarity

### Does Not Own

- Barrier identification
- Planning
- Reflection
- Growth Passport updates
- Final response generation

### Design Principle

Translate complexity into understanding without removing important information or making decisions for the user.
---

## Planning Agent

### Purpose

Transforms understanding into action by recommending one meaningful, achievable next step that builds momentum without overwhelming the user.

### Responsibilities

1. Read the Agent Context Packet.
2. Review the identified barrier.
3. Review the translated problem.
4. Generate one recommended Micro-Win.
5. Generate the user's Next Step.
6. Optionally suggest 2–3 future milestones.
7. Update the Agent Context Packet.

### Outputs

- Recommended Micro-Win
- Suggested Next Step
- Optional Future Milestones

### Owns

- Action planning
- Micro-Win generation
- Milestone sequencing
- Momentum building

### Does Not Own

- Barrier identification
- Cognitive translation
- Reflection
- Growth Passport updates
- Final response generation

### Design Principle

Prefer one completed meaningful action over ten incomplete intentions.
---

## Reflection Agent

### Purpose

Helps users recognize meaningful progress by reinforcing awareness, identifying evidence-based strengths, and encouraging self-reflection.

### Responsibilities

1. Read the completed Agent Context Packet.
2. Review the identified barrier.
3. Review the Cognitive Translation.
4. Review the recommended Micro-Win.
5. Generate a concise Reflection Summary.
6. Identify one evidence-based strength.
7. Generate one optional Reflection Question.
8. Update the Agent Context Packet.

### Outputs

- Reflection Summary
- Evidence-Based Strength
- Optional Reflection Question

### Owns

- Reflection generation
- Strength recognition
- Self-awareness support
- Session closure

### Does Not Own

- Barrier identification
- Cognitive translation
- Planning
- Growth Passport updates
- Final response generation

### Design Principle

Reflection should reinforce awareness, not dependence.
