---
id: 001
title: Integrate Agents + Upgrade to ChatKit
stage: green
date: 2026-02-03
surface: agent
model: claude-opus-4-5-20251101
feature: 002-phase-3-ai-chatbot
branch: 002-phase-3-ai-chatbot
user: zoyaafzal
command: implement plan
labels: ["chatkit", "sse-streaming", "agent-pattern", "nlp"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/services/chat_service.py
  - backend/src/api/routes/chat.py
  - frontend/src/app/api/proxy/[...path]/route.ts
  - frontend/package.json
  - frontend/src/app/layout.tsx
  - frontend/src/components/chatkit-provider.tsx
  - frontend/src/app/chat/page.tsx
  - frontend/src/components/chat-interface.legacy.tsx
  - frontend/src/components/chat-message.legacy.tsx
  - frontend/src/lib/chat-client.legacy.ts
tests:
  - tests/contract/test_chat_contract.py (3 passed)
  - tests/integration/test_chat_*.py (15 passed)
---

## Prompt

Implement the following plan:

# Plan: Integrate Agents + Upgrade to ChatKit

## Summary

Two enhancements to the Phase III AI chatbot:
1. **Enhance SYSTEM_INSTRUCTIONS** with conversation-to-todo agent pattern (structured NLP)
2. **Replace custom chat UI with ChatKit** (SSE streaming, modern widget)

---

## Part 1: Conversation-to-Todo Agent Pattern

**Single file change**: `backend/src/services/chat_service.py`

Replace the 14-line `SYSTEM_INSTRUCTIONS` (lines 28-41) with a comprehensive prompt that embeds:

1. **Intent Classification** - Classify each message as CREATE/READ/UPDATE/DELETE/QUERY before acting
2. **Entity Extraction** - Extract title, description, priority, due date before calling tools
3. **Ambiguity Detection** - Ask clarifying questions when input is vague (e.g., "add a task" → "What should the task be called?")
4. **Confirmation for Deletes** - Always confirm before calling delete_task
5. **Batch Operations** - Handle multiple intents in one message (e.g., "add groceries and complete dentist")

**No code architecture changes** - the OpenAI Agents SDK already supports multi-turn clarification.

---

## Part 2: ChatKit UI Integration

### Phase A: Backend SSE Streaming

**T1. Add streaming endpoint** - `backend/src/api/routes/chat.py`
**T2. Add streaming agent runner** - `backend/src/services/chat_service.py`
**T3. Keep existing endpoint** - backward compatibility

### Phase B: Frontend Proxy SSE Support

**T4. Update proxy route** - `frontend/src/app/api/proxy/[...path]/route.ts`

### Phase C: Frontend ChatKit Integration

**T5. Add ChatKit dependency** - `frontend/package.json`
**T6. Add CDN script** - `frontend/src/app/layout.tsx`
**T7. Create ChatKit provider** - NEW: `frontend/src/components/chatkit-provider.tsx`
**T8. Create ChatKit chat page** - `frontend/src/app/chat/page.tsx`
**T9. Archive old components** (optional)

## Response snapshot

Successfully implemented both parts of the plan:

### Part 1: Enhanced SYSTEM_INSTRUCTIONS
- Added intent classification (CREATE/READ/UPDATE/DELETE/COMPLETE/QUERY)
- Added entity extraction for title, description, priority, due_date, task_identifier, filter
- Added ambiguity detection with clarifying questions
- Added required delete confirmation before executing deletes
- Added batch operations support for multiple intents in one message

### Part 2: ChatKit UI Integration
- Added `_run_agent_streamed()` async generator for SSE streaming
- Added `ChatService.process_message_stream()` yielding ChatKit-compatible SSE events
- Added `POST /api/{user_id}/chat/stream` endpoint with StreamingResponse
- Updated proxy to detect and passthrough SSE responses
- Added `@openai/chatkit-react@^1.4.3` dependency
- Added ChatKit CDN script to layout.tsx
- Created ChatKitProvider component with auth integration
- Updated chat page to use ChatKit widget
- Archived legacy chat components with `.legacy` suffix

## Outcome

- ✅ Impact: Major enhancement - structured NLP for todo agent + modern streaming chat UI
- 🧪 Tests: 18 tests passing (3 contract + 15 integration)
- 📁 Files: 10 files modified/created
- 🔁 Next prompts: Manual E2E testing with live backend, verify SSE streaming in browser
- 🧠 Reflection: Implementation followed plan closely. Package version needed correction (^1.4.3 instead of ^0.1.0). Existing tests remain compatible.

## Evaluation notes (flywheel)

- Failure modes observed: Initial ChatKit package version was incorrect (^0.1.0 doesn't exist)
- Graders run and results (PASS/FAIL): TypeScript: PASS, Pytest: PASS, Build: PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test streaming endpoint with curl, verify ChatKit widget renders correctly
