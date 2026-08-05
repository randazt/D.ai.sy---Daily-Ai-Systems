# D.AI.SY API Contracts

## Purpose

This document defines the public API between the D.AI.SY frontend and backend.

All AI orchestration occurs on the server. The frontend communicates only with these endpoints.

---

# Design Principles

- RESTful
- Workspace-centric
- Authenticated
- Stateless
- JSON request/response
- Server-side orchestration

---

# Endpoints

## POST /conversation

Primary endpoint for user interaction.

### Request

{
  "workspace_id": "workspace_id",
  "message": "I have an idea but don't know where to start."
}

### Server Responsibilities

- Authenticate user
- Load User Profile
- Load Growth Passport
- Load Workspace Memory
- Create Context Packet
- Execute ADK orchestration
- Persist memory updates
- Persist session
- Return final response

### Response

{
  "response": "...",
  "workspace_id": "...",
  "session_id": "...",
  "micro_win": "...",
  "next_step": "..."
}

---

## GET /workspaces

Returns all workspaces owned by the authenticated user.

---

## POST /workspaces

Creates a new workspace.

---

## GET /workspaces/{workspace_id}

Returns workspace metadata and current Workspace Memory.

---

## PATCH /workspaces/{workspace_id}

Updates workspace metadata.

---

## GET /growth-passport

Returns the authenticated user's Growth Passport.

---

## GET /session/{session_id}

Returns a completed session summary.

---

# Authentication

All endpoints require Firebase Authentication.

The backend validates the Firebase ID Token before processing requests.

---

# Versioning

Initial API Version:

v1
