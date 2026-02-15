# Tasks: AI-Powered Todo Chatbot

**Input**: Design documents from `/specs/002-phase-3-ai-chatbot/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Test tasks included per user input requesting TDD alignment.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`

---

## Phase 1: Setup

**Purpose**: Add Phase III dependencies and configuration to existing project

- [x] T001 Add openai-agents and mcp dependencies to backend/requirements.txt
- [x] T002 [P] Add OPENAI_API_KEY and OPENAI_MODEL to backend/src/core/config.py Settings class
- [x] T003 [P] Create backend/src/mcp/__init__.py package directory
- [x] T004 [P] Create backend/src/api/schemas/chat.py with ChatRequest and ChatResponse Pydantic models per contracts/chat-api.yaml

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: New database models and services that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Create Conversation SQLModel in backend/src/models/conversation.py with fields: id (UUID PK), user_id (FK to user.id, indexed), title (VARCHAR 255 nullable), created_at, updated_at
- [x] T006 Create Message SQLModel in backend/src/models/message.py with fields: id (UUID PK), conversation_id (FK to conversation.id, indexed), role (VARCHAR, enum user/assistant), content (TEXT), tool_calls (JSON nullable), sequence_number (INTEGER), created_at. Add composite index on (conversation_id, sequence_number)
- [x] T007 Update backend/src/models/__init__.py to export Conversation and Message
- [x] T008 Create Alembic migration backend/alembic/versions/002_add_conversation_message.py adding conversation and message tables with indexes
- [x] T009 Implement ConversationService in backend/src/services/conversation_service.py with methods: create_conversation(user_id) -> Conversation, get_conversation(conversation_id, user_id) -> Optional[Conversation], add_message(conversation_id, role, content, tool_calls) -> Message, get_recent_messages(conversation_id, limit=50) -> list[Message], list_conversations(user_id) -> list[Conversation]
- [x] T010 Create MCP server script at backend/src/mcp/server.py using mcp Python SDK. Register 5 tools (add_task, list_tasks, update_task, complete_task, delete_task) that accept user_id and call existing TaskService methods. Each tool must have JSON schema, validate input, and return structured JSON output. The server runs as stdio process.
- [x] T011 Implement ChatService in backend/src/services/chat_service.py that: creates OpenAI Agent with MCPServerStdio pointing to backend/src/mcp/server.py, loads conversation history (last 50 messages), sends user message to agent, persists user + assistant messages, returns ChatResponse with conversation_id and reply. Include single retry with 3s timeout for AI model calls.

**Checkpoint**: Foundation ready — user story implementation can begin

---

## Phase 3: User Story 1 — Add Task via Natural Language (Priority: P1) MVP

**Goal**: User sends "Add a task to buy groceries" and a task is created in DB

**Independent Test**: Send chat message with task creation request, verify task record in DB

### Tests for User Story 1

- [x] T012 [P] [US1] Write integration test in backend/tests/integration/test_chat_add_task.py: POST /api/{user_id}/chat with message "Add a task to buy groceries", assert 200, assert response has conversation_id and reply, assert task exists in DB with title containing "groceries" and completed=false

### Implementation for User Story 1

- [x] T013 [US1] Create chat route in backend/src/api/routes/chat.py with POST /api/{user_id}/chat endpoint. Validate JWT user matches path user_id. Parse ChatRequest, call ChatService, return ChatResponse. Handle empty message (400), message too long (400), conversation not found (404), AI service failure (503)
- [x] T014 [US1] Register chat router in backend/src/main.py (add import and include_router)
- [x] T015 [US1] Verify T012 test passes end-to-end with "Add a task to buy groceries" producing a task record

**Checkpoint**: User Story 1 fully functional — can add tasks via chat

---

## Phase 4: User Story 2 — List Tasks (Priority: P1)

**Goal**: User sends "Show me pending tasks" and gets a filtered task list

**Independent Test**: Create tasks, send list request, verify correct filter results

### Tests for User Story 2

- [x] T016 [P] [US2] Write integration test in backend/tests/integration/test_chat_list_tasks.py: Create 3 pending + 2 completed tasks via TaskService, POST chat with "Show me pending tasks", assert reply references exactly 3 tasks

### Implementation for User Story 2

- [x] T017 [US2] Verify list_tasks MCP tool in backend/src/mcp/server.py correctly supports filter parameter (all/pending/completed) and returns filtered results. Adjust tool schema if needed to accept optional completed filter
- [x] T018 [US2] Verify T016 test passes with agent correctly invoking list_tasks tool

**Checkpoint**: User Stories 1 AND 2 work independently

---

## Phase 5: User Story 3 — Complete a Task (Priority: P1)

**Goal**: User sends "Mark task 3 as done" and the task is completed

**Independent Test**: Create a task, send completion command, verify completed=true in DB

### Tests for User Story 3

- [x] T019 [P] [US3] Write integration test in backend/tests/integration/test_chat_complete_task.py: Create a task, POST chat with "Mark task {id} as done", assert task completed=true in DB. Also test nonexistent task returns error message

### Implementation for User Story 3

- [x] T020 [US3] Verify complete_task MCP tool in backend/src/mcp/server.py handles task lookup, sets completed=true, and returns confirmation. Ensure error case (nonexistent task) returns descriptive error
- [x] T021 [US3] Verify T019 test passes

**Checkpoint**: User Stories 1, 2, AND 3 all work independently

---

## Phase 6: User Story 4 — Update a Task (Priority: P2)

**Goal**: User sends "Change task 1 title to Buy organic groceries" and the task updates

**Independent Test**: Create a task, send update command, verify title changed in DB

### Tests for User Story 4

- [x] T022 [P] [US4] Write integration test in backend/tests/integration/test_chat_update_task.py: Create a task, POST chat with "Change task {id} title to Buy organic groceries", assert title updated in DB

### Implementation for User Story 4

- [x] T023 [US4] Verify update_task MCP tool in backend/src/mcp/server.py accepts title and/or description parameters, updates the task, and returns confirmation
- [x] T024 [US4] Verify T022 test passes

**Checkpoint**: User Stories 1-4 all work

---

## Phase 7: User Story 5 — Delete a Task (Priority: P2)

**Goal**: User sends "Delete my groceries task" and it is removed

**Independent Test**: Create a task, send delete command, verify task gone from DB

### Tests for User Story 5

- [x] T025 [P] [US5] Write integration test in backend/tests/integration/test_chat_delete_task.py: Create a task titled "Buy groceries", POST chat with "Delete my groceries task", assert task no longer in DB. Also test ambiguous match prompts clarification

### Implementation for User Story 5

- [x] T026 [US5] Verify delete_task MCP tool in backend/src/mcp/server.py supports deletion by ID and by title search. When multiple matches found, return list for user to clarify
- [x] T027 [US5] Verify T025 test passes

**Checkpoint**: All 5 task management operations work via chat

---

## Phase 8: User Story 6 — Resume Conversation After Restart (Priority: P1)

**Goal**: Server restarts, user continues conversation with same conversation_id

**Independent Test**: Start conversation, restart server, send follow-up with same conversation_id

### Tests for User Story 6

- [x] T028 [P] [US6] Write integration test in backend/tests/integration/test_chat_resume.py: POST chat (no conversation_id) to create conversation, capture conversation_id, POST second message with conversation_id, assert assistant has context from first message. Also test: POST with nonexistent conversation_id returns 404

### Implementation for User Story 6

- [x] T029 [US6] Verify ChatService in backend/src/services/chat_service.py correctly loads conversation history when conversation_id is provided and creates new conversation when not provided
- [x] T030 [US6] Verify T028 test passes

**Checkpoint**: Conversations persist and resume correctly

---

## Phase 9: User Story 7 — Multi-Turn Chat in Frontend (Priority: P2)

**Goal**: Web chat interface for sending/receiving messages in correct order

**Independent Test**: Open chat UI, send 3 messages, verify all 6 messages display in order

### Tests for User Story 7

- [x] T031 [P] [US7] Write contract test in backend/tests/contract/test_chat_contract.py: Validate POST /api/{user_id}/chat request/response schemas match contracts/chat-api.yaml. Validate GET /api/{user_id}/conversations returns list. Validate GET /api/{user_id}/conversations/{id}/messages returns ordered messages

### Implementation for User Story 7

- [x] T032 [US7] Add GET /api/{user_id}/conversations and GET /api/{user_id}/conversations/{conversation_id}/messages endpoints to backend/src/api/routes/chat.py per contracts/chat-api.yaml
- [x] T033 [US7] Create chat API client in frontend/src/lib/chat-client.ts with functions: sendMessage(userId, message, conversationId?) -> ChatResponse, listConversations(userId) -> ConversationSummary[], getMessages(userId, conversationId, limit?) -> MessageList
- [x] T034 [US7] Create ChatMessage component in frontend/src/components/chat-message.tsx displaying user/assistant messages with role-based styling
- [x] T035 [US7] Create ChatInterface component in frontend/src/components/chat-interface.tsx with message list, input field, send button, auto-scroll, and loading state
- [x] T036 [US7] Create chat page at frontend/src/app/chat/page.tsx using ChatInterface component, wrapped in ProtectedRoute
- [x] T037 [US7] Verify T031 contract test passes and frontend renders messages in correct order

**Checkpoint**: Full-stack chat working with frontend

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Security hardening, documentation, and final validation

- [x] T038 [P] Add user_id path parameter validation in backend/src/api/routes/chat.py — assert path user_id matches JWT sub claim, return 403 on mismatch
- [x] T039 [P] Add cross-user isolation test in backend/tests/integration/test_chat_isolation.py: User A creates conversation, User B tries to access it, assert 403/404
- [x] T040 [P] Update backend README.md with Phase III setup: new env vars (OPENAI_API_KEY, OPENAI_MODEL), new dependencies, chat endpoint documentation
- [x] T041 [P] Add structured error logging for chat failures in backend/src/api/routes/chat.py using existing core/logging.py patterns
- [x] T042 Run full test suite and verify all tests pass with coverage >= 80%

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational — MVP target
- **US2 (Phase 4)**: Depends on Foundational — can run parallel with US1
- **US3 (Phase 5)**: Depends on Foundational — can run parallel with US1
- **US4 (Phase 6)**: Depends on Foundational — can run parallel
- **US5 (Phase 7)**: Depends on Foundational — can run parallel
- **US6 (Phase 8)**: Depends on US1 (needs at least one conversation)
- **US7 (Phase 9)**: Depends on US1 (needs working chat endpoint)
- **Polish (Phase 10)**: Depends on all user stories

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Verify test passes after implementation
- Story complete before moving to next priority

### Parallel Opportunities

- T001-T004 (Setup) all run in parallel
- T005-T006 (Models) run in parallel
- T012, T016, T019, T022, T025, T028, T031 (All test tasks) run in parallel once Phase 2 completes
- US1-US5 can all start after Phase 2 (if team capacity allows)
- T033-T036 (Frontend tasks) run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: User Story 1 (Add Task)
4. **STOP and VALIDATE**: Test add task via chat independently
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 (Add Task) → Test → Demo (MVP!)
3. Add US2 (List) + US3 (Complete) → Test → Demo
4. Add US4 (Update) + US5 (Delete) → Test → Demo
5. Add US6 (Resume) → Test → Demo
6. Add US7 (Frontend Chat) → Test → Demo
7. Polish → Final validation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story
- Existing Phase II code (TaskService, auth, models) is reused directly
- MCP tools wrap existing TaskService — no database logic duplication
- Each user story independently testable via chat endpoint
- Commit after each task or logical group
