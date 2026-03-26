# Implementation Plan: AI-Powered Todo Chatbot

**Branch**: `002-phase-3-ai-chatbot` | **Date**: 2026-02-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-phase-3-ai-chatbot/spec.md`

## Summary

Build an AI-powered chat endpoint that accepts natural language messages
from authenticated users and manages their todos through MCP tools.
The system extends the existing Phase II FastAPI backend with new
Conversation/Message models, an MCP server exposing 5 task tools, and
an OpenAI Agents SDK integration that orchestrates intent-to-tool
mapping. The frontend gains a chat interface alongside the existing
task management UI.

## Technical Context

**Language/Version**: Python 3.11+, TypeScript/Node 20+
**Primary Dependencies**: FastAPI, OpenAI Agents SDK (`openai-agents`),
MCP Python SDK (`mcp`), SQLModel, PyJWT
**Storage**: Neon PostgreSQL (existing), SQLModel ORM
**Testing**: pytest, pytest-asyncio
**Target Platform**: Linux/macOS local development
**Project Type**: Web application (backend + frontend)
**Performance Goals**: Chat response <3s p95
**Constraints**: Stateless per request, no in-memory sessions,
MCP-only mutations from agent
**Scale/Scope**: Single-user concurrent, demo-scale

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] I. Spec-First: Spec ratified at `specs/002-phase-3-ai-chatbot/spec.md`
- [x] II. Phase-Bound: Building Phase III; Phases I+II complete
- [x] III. Test-First: Test tasks precede implementation tasks
- [x] IV. State Transparency: All state in PostgreSQL, no in-memory sessions
- [x] V. Conversational Determinism: MCP tools for all mutations, stateless API
- [x] VI. Context7 MCP Governance: PHRs created for all interactions
- [x] VII. Cloud-Native Parity: Deferred to Phase IV (non-goal)
- [x] VIII. Quality Gates: Spec gate passed, planning gate in progress
- [x] IX. Agent Autonomy: Human approval required for all decisions
- [x] X. Observability: Structured logging via existing `core/logging.py`
- [x] XI. Prohibited Actions: No violations

## Project Structure

### Documentation (this feature)

```text
specs/002-phase-3-ai-chatbot/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── chat-api.yaml    # Chat endpoint OpenAPI contract
└── tasks.md             # Phase 2 output (/sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── task.py          # Existing - reused by MCP tools
│   │   ├── user.py          # Existing - reused
│   │   ├── conversation.py  # NEW - Conversation model
│   │   └── message.py       # NEW - Message model
│   ├── services/
│   │   ├── task_service.py      # Existing - called by MCP tools
│   │   ├── auth_service.py      # Existing - reused
│   │   ├── conversation_service.py  # NEW
│   │   └── chat_service.py     # NEW - orchestrates agent
│   ├── mcp/
│   │   ├── __init__.py      # NEW
│   │   ├── server.py        # NEW - MCP server with tools
│   │   └── tools.py         # NEW - Tool definitions
│   ├── api/
│   │   ├── routes/
│   │   │   ├── chat.py      # NEW - POST /api/{user_id}/chat
│   │   │   └── ...          # Existing routes preserved
│   │   └── schemas/
│   │       └── chat.py      # NEW - Request/response schemas
│   ├── core/
│   │   └── config.py        # MODIFIED - add OPENAI_API_KEY
│   └── main.py              # MODIFIED - register chat router
└── tests/
    ├── test_mcp_tools.py        # NEW
    ├── test_chat_endpoint.py    # NEW
    ├── test_conversation.py     # NEW
    └── ...                      # Existing tests preserved

frontend/
├── src/
│   ├── app/
│   │   └── chat/
│   │       └── page.tsx     # NEW - Chat interface page
│   ├── components/
│   │   ├── chat-interface.tsx   # NEW - Chat UI component
│   │   ├── chat-message.tsx     # NEW - Message bubble
│   │   └── ...                  # Existing components preserved
│   └── lib/
│       └── chat-client.ts   # NEW - Chat API client
└── ...
```

**Structure Decision**: Web application structure (backend/ + frontend/)
matching the existing Phase II layout. New files added alongside
existing code; no restructuring needed.

## Complexity Tracking

No Constitution violations requiring justification.
