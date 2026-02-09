---
id: 002
title: Phase III Constitution Amendment
stage: constitution
date: 2026-02-02
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: 001-phase-2-persistent-auth
user: architect
command: /sp.constitution
labels: ["constitution", "phase-3", "mcp", "chatbot"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

# Phase III: AI-Powered Todo Chatbot (MCP + Agents SDK)

## Intent
Build an AI-powered Todo chatbot that lets authenticated users manage tasks using natural language. The system must use MCP tools, persist all data in PostgreSQL, and remain stateless.

## Target Audience
Students, developers, and hackathon evaluators.

## Primary Users
Registered users authenticated via Better Auth.

---

## Core Features
- Natural language task management (add, list, update, complete, delete)
- Conversation persistence
- AI agent reasoning via MCP tools
- Stateless chat API

---

## Constraints
- Backend: FastAPI + OpenAI Agents SDK
- MCP: Official MCP SDK
- Database: Neon PostgreSQL + SQLModel
- Auth: Better Auth
- No in-memory sessions
- All state stored in database
- Code generated via Claude Code only
- Endpoint: `POST /api/{user_id}/chat`
- Secrets via environment variables
- Must run locally

---

## Success Criteria

### 1. Chat API
- Responds within 3 seconds
- Returns `conversation_id` and reply

### 2. Task Management
- ≥95% correct MCP tool usage
- Supports add, list, update, complete, delete

### 3. MCP Tools
- `add_task` → creates record
- `list_tasks` → correct results
- `update_task` → updates fields
- `complete_task` → sets completed=true
- `delete_task` → removes record

### 4. Persistence
- Messages stored in database
- Conversations survive restarts
- Resume via `conversation_id`

### 5. Responses
- Friendly confirmation after actions

### 6. Error Handling
- Clear errors for invalid input
- No crashes
- Errors logged

### 7. Security
- Auth required
- No cross-user access

### 8. Frontend Support
- Multi-turn chat
- Correct message order
- Reliable send/receive

### 9. Documentation
- README with setup and env vars
- API documentation

---

## Timeline
- Completion within 3 weeks
- Demo before evaluation

---

## Non-Goals
- Voice input
- Multi-language (Urdu later)
- Analytics
- Mobile apps
- Offline mode
- Calendar/notifications
- Kubernetes (Phase IV/V)

---

## Out of Scope
- Payments
- Social features
- Team collaboration
- File/image support

---

## Evaluation Scenarios

1. **Add Task**
   "Add a task to buy groceries" → Creates task

2. **List Tasks**
   "Show pending tasks" → Lists incomplete

3. **Complete Task**
   "Mark task 3 as done" → Completes task

4. **Delete Task**
   "Delete my meeting task" → Finds and deletes

5. **Resume Chat**
   Continue after restart using `conversation_id`

---

## Acceptance Tests
- All commands pass tests
- Correct DB records
- Valid JSON responses
- No in-memory state
- Valid tool schemas

---

## Constitution Alignment
- Follows Spec-Driven Development
- No undocumented behavior
- No hidden state

## Response snapshot

Updated constitution from v1.0.0 to v1.1.0 (MINOR). Key changes: expanded Phase III definition with concrete technology stack (FastAPI, OpenAI Agents SDK, MCP SDK, Neon PostgreSQL, SQLModel, Better Auth), added MCP Tool Governance and Stateless API Rules to Principle V, added Phase III Data Rules section, added prohibition against in-memory session state. All templates verified compatible; no updates needed.

## Outcome

- ✅ Impact: Constitution amended to v1.1.0 with Phase III specifics
- 🧪 Tests: N/A (governance document)
- 📁 Files: .specify/memory/constitution.md
- 🔁 Next prompts: /sp.specify for Phase III feature spec
- 🧠 Reflection: Clean amendment; no principle conflicts detected

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
