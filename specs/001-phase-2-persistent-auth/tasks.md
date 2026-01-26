# Tasks: Phase II - Persistent Storage with Authentication

**Input**: Design documents from `/specs/001-phase-2-persistent-auth/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included per Constitution Principle III (Test-First Discipline)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Backend: Python 3.11+ with FastAPI, SQLModel
- Frontend: TypeScript with Next.js 16 (App Router), Better Auth

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for both backend and frontend

- [x] T001 Create backend project structure: `backend/src/{models,services,api/{routes,deps},core}/` and `backend/tests/{unit,contract,integration}/`
- [x] T002 Create frontend project structure: `frontend/src/{app,components,lib,types}/` and `frontend/tests/`
- [x] T003 [P] Initialize backend Python project with pyproject.toml and requirements.txt in `backend/`
- [x] T004 [P] Initialize frontend Next.js 16 project with package.json in `frontend/`
- [x] T005 [P] Create backend `.env.example` with DATABASE_URL and BETTER_AUTH_SECRET placeholders in `backend/`
- [x] T006 [P] Create frontend `.env.example` with NEXT_PUBLIC_APP_URL, NEXT_PUBLIC_API_URL, BETTER_AUTH_SECRET in `frontend/`
- [x] T007 [P] Configure backend linting (ruff) and formatting (black) in `backend/pyproject.toml`
- [x] T008 [P] Configure frontend ESLint and Prettier in `frontend/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T009 Create database connection module with Neon PostgreSQL pool_pre_ping in `backend/src/core/database.py`
- [x] T010 Create configuration module loading env vars in `backend/src/core/config.py`
- [x] T011 [P] Create User SQLModel entity in `backend/src/models/user.py`
- [x] T012 [P] Create Task SQLModel entity with user_id FK and version field in `backend/src/models/task.py`
- [x] T013 Create models __init__.py exporting User and Task in `backend/src/models/__init__.py`
- [x] T014 Initialize Alembic for database migrations in `backend/alembic/`
- [x] T015 Create initial migration for user and task tables in `backend/alembic/versions/001_initial_schema.py`
- [x] T016 Implement JWT verification dependency extracting user_id from token in `backend/src/api/deps/auth.py`
- [x] T017 Implement database session dependency in `backend/src/api/deps/database.py`
- [x] T018 Create deps __init__.py exporting get_current_user and get_session in `backend/src/api/deps/__init__.py`
- [x] T019 Create FastAPI application with CORS middleware in `backend/src/main.py`
- [x] T020 Create error response schemas (ErrorResponse, ValidationError) in `backend/src/api/schemas/error.py`
- [x] T021 Create global exception handlers for HTTP and validation errors in `backend/src/api/exceptions.py`
- [x] T022 [P] Configure Better Auth server with JWT plugin in `frontend/src/lib/auth.ts`
- [x] T023 [P] Create Better Auth client for frontend in `frontend/src/lib/auth-client.ts`
- [x] T024 [P] Create API client with JWT header injection in `frontend/src/lib/api-client.ts`
- [x] T025 Create pytest conftest.py with test fixtures (test client, valid/expired tokens) in `backend/tests/conftest.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - User Registration and Login (Priority: P1)

**Goal**: Enable users to create accounts and log in to receive JWT tokens

**Independent Test**: Create account, log in, verify valid JWT token is returned

**Depends on**: Phase 2 (Foundational)

### Tests for User Story 1

- [x] T026 [P] [US1] Contract test for registration endpoint in `backend/tests/contract/test_auth_registration.py`
- [x] T027 [P] [US1] Contract test for login endpoint in `backend/tests/contract/test_auth_login.py`
- [x] T028 [P] [US1] Contract test for JWT verification in `backend/tests/contract/test_jwt_verification.py`
- [x] T029 [P] [US1] Integration test for registration-login flow in `backend/tests/integration/test_auth_flow.py`

### Implementation for User Story 1

- [x] T030 [US1] Create Pydantic schemas for auth (UserCreate, UserLogin, AuthResponse) in `backend/src/api/schemas/auth.py`
- [x] T031 [US1] Implement auth service with register and authenticate methods in `backend/src/services/auth_service.py`
- [x] T032 [US1] Create auth router with /api/auth/register and /api/auth/login endpoints in `backend/src/api/routes/auth.py`
- [x] T033 [US1] Register auth router in main.py FastAPI app in `backend/src/main.py`
- [x] T034 [P] [US1] Create login page component in `frontend/src/app/login/page.tsx`
- [x] T035 [P] [US1] Create registration page component in `frontend/src/app/register/page.tsx`
- [x] T036 [US1] Create auth form component with email/password inputs in `frontend/src/components/auth-form.tsx`
- [x] T037 [US1] Add Better Auth API route handler in `frontend/src/app/api/auth/[...all]/route.ts`

**Checkpoint**: Users can register and log in. JWT tokens are issued correctly.

---

## Phase 4: User Story 2 - Persistent Task Creation (Priority: P1)

**Goal**: Enable authenticated users to create tasks that persist in the database

**Independent Test**: Create task, log out, log back in, verify task still exists

**Depends on**: Phase 2 (Foundational), US1 (authentication required)

### Tests for User Story 2

- [x] T038 [P] [US2] Contract test for create task endpoint in `backend/tests/contract/test_task_create.py`
- [x] T039 [P] [US2] Contract test for list tasks endpoint in `backend/tests/contract/test_task_list.py`
- [x] T040 [P] [US2] Contract test for get task by ID endpoint in `backend/tests/contract/test_task_get.py`
- [x] T041 [P] [US2] Integration test for task persistence across sessions in `backend/tests/integration/test_task_persistence.py`

### Implementation for User Story 2

- [x] T042 [US2] Create Pydantic schemas (TaskCreate, TaskResponse, TaskListResponse) in `backend/src/api/schemas/task.py`
- [x] T043 [US2] Implement task service with create, get_by_id, list_by_user methods in `backend/src/services/task_service.py`
- [x] T044 [US2] Create task router with POST /api/v1/tasks endpoint in `backend/src/api/routes/tasks.py`
- [x] T045 [US2] Add GET /api/v1/tasks endpoint with cursor-based pagination in `backend/src/api/routes/tasks.py`
- [x] T046 [US2] Add GET /api/v1/tasks/{task_id} endpoint in `backend/src/api/routes/tasks.py`
- [x] T047 [US2] Register task router in main.py FastAPI app in `backend/src/main.py`
- [x] T048 [P] [US2] Create task list page component in `frontend/src/app/tasks/page.tsx`
- [x] T049 [P] [US2] Create task card component in `frontend/src/components/task-card.tsx`
- [x] T050 [US2] Create add task form component in `frontend/src/components/add-task-form.tsx`
- [x] T051 [US2] Create TypeScript types for Task entity in `frontend/src/types/task.ts`

**Checkpoint**: Users can create tasks and view their task list. Tasks persist across sessions.

---

## Phase 5: User Story 3 - User Task Isolation (Priority: P1)

**Goal**: Ensure users can only see and access their own tasks

**Independent Test**: Create tasks as User A, log in as User B, verify User B cannot see User A's tasks

**Depends on**: US2 (tasks must exist to test isolation)

### Tests for User Story 3

- [x] T052 [P] [US3] Contract test for cross-user access returning 404 in `backend/tests/contract/test_task_isolation.py`
- [x] T053 [P] [US3] Integration test with two users verifying isolation in `backend/tests/integration/test_user_isolation.py`



### Implementation for User Story 3

- [x] T054 [US3] Add user_id filtering to all task queries in task_service in `backend/src/services/task_service.py`
- [x] T055 [US3] Ensure get_by_id returns None for tasks belonging to other users in `backend/src/services/task_service.py`
- [x] T056 [US3] Add 404 response for non-owned tasks in task router in `backend/src/api/routes/tasks.py`
- [x] T057 [US3] Add unit tests for task service user filtering in `backend/tests/unit/test_task_service_isolation.py`

**Checkpoint**: User isolation is enforced. User A cannot see or access User B's tasks.

---

## Phase 6: User Story 4 - Persistent Task Updates (Priority: P2)

**Goal**: Enable authenticated users to update their existing tasks

**Independent Test**: Create task, update title/description, verify changes persist across sessions

**Depends on**: US2 (tasks must exist), US3 (isolation must be enforced)

### Tests for User Story 4

- [x] T058 [P] [US4] Contract test for update task endpoint in `backend/tests/contract/test_task_update.py`
- [x] T059 [P] [US4] Contract test for optimistic locking (version conflict) in `backend/tests/contract/test_task_version_conflict.py`
- [x] T060 [P] [US4] Integration test for task updates persisting in `backend/tests/integration/test_task_update_persistence.py`

### Implementation for User Story 4

- [x] T061 [US4] Create TaskUpdate Pydantic schema with version field in `backend/src/api/schemas/task.py`
- [x] T062 [US4] Implement update method with optimistic locking in task_service in `backend/src/services/task_service.py`
- [x] T063 [US4] Add PUT /api/v1/tasks/{task_id} endpoint with version validation in `backend/src/api/routes/tasks.py`
- [x] T064 [US4] Add 409 Conflict response for version mismatch in `backend/src/api/routes/tasks.py`
- [x] T065 [P] [US4] Create edit task modal/form component in `frontend/src/components/edit-task-form.tsx`
- [x] T066 [US4] Add edit functionality to task card component in `frontend/src/components/task-card.tsx`

**Checkpoint**: Users can update tasks. Optimistic locking prevents data conflicts.

---

## Phase 7: User Story 5 - Persistent Task Completion (Priority: P2)

**Goal**: Enable authenticated users to mark tasks as complete/incomplete

**Independent Test**: Create task, mark complete, log out/in, verify completion status persisted

**Depends on**: US2 (tasks must exist), US3 (isolation must be enforced)

### Tests for User Story 5

- [x] T067 [P] [US5] Contract test for complete task endpoint in `backend/tests/contract/test_task_complete.py`
- [x] T068 [P] [US5] Contract test for uncomplete task endpoint in `backend/tests/contract/test_task_uncomplete.py`
- [x] T069 [P] [US5] Integration test for completion status persisting in `backend/tests/integration/test_task_completion_persistence.py`

### Implementation for User Story 5

- [x] T070 [US5] Create VersionRequest schema for complete/uncomplete in `backend/src/api/schemas/task.py`
- [x] T071 [US5] Implement complete and uncomplete methods in task_service in `backend/src/services/task_service.py`
- [x] T072 [US5] Add POST /api/v1/tasks/{task_id}/complete endpoint in `backend/src/api/routes/tasks.py`
- [x] T073 [US5] Add POST /api/v1/tasks/{task_id}/uncomplete endpoint in `backend/src/api/routes/tasks.py`
- [x] T074 [US5] Add complete/uncomplete toggle to task card component in `frontend/src/components/task-card.tsx`

**Checkpoint**: Users can mark tasks complete/incomplete. Status persists across sessions.

---

## Phase 8: User Story 6 - Persistent Task Deletion (Priority: P3)

**Goal**: Enable authenticated users to permanently delete their tasks

**Independent Test**: Create task, delete it, log out/in, verify task no longer exists

**Depends on**: US2 (tasks must exist), US3 (isolation must be enforced)

### Tests for User Story 6

- [x] T075 [P] [US6] Contract test for delete task endpoint in `backend/tests/contract/test_task_delete.py`
- [x] T076 [P] [US6] Integration test for task deletion being permanent in `backend/tests/integration/test_task_deletion.py`

### Implementation for User Story 6

- [x] T077 [US6] Implement hard delete method in task_service in `backend/src/services/task_service.py`
- [x] T078 [US6] Add DELETE /api/v1/tasks/{task_id} endpoint returning 204 in `backend/src/api/routes/tasks.py`
- [x] T079 [US6] Add delete button with confirmation to task card component in `frontend/src/components/task-card.tsx`

**Checkpoint**: Users can permanently delete tasks. Deleted tasks do not reappear.

---

## Phase 9: User Story 7 - User Logout (Priority: P3)

**Goal**: Enable authenticated users to log out and terminate their session

**Independent Test**: Log in, log out, verify subsequent requests with old token fail

**Depends on**: US1 (authentication must exist)

### Tests for User Story 7

- [x] T080 [P] [US7] Contract test for logout endpoint in `backend/tests/contract/test_auth_logout.py`
- [x] T081 [P] [US7] Integration test for session termination in `backend/tests/integration/test_logout_flow.py`

### Implementation for User Story 7

- [x] T082 [US7] Add logout method to auth service (token invalidation) in `backend/src/services/auth_service.py`
- [x] T083 [US7] Add POST /api/auth/logout endpoint in `backend/src/api/routes/auth.py`
- [x] T084 [US7] Add logout button to frontend navigation in `frontend/src/app/tasks/page.tsx`
- [x] T085 [US7] Implement logout handler clearing session in frontend in `frontend/src/lib/auth-client.ts`

**Checkpoint**: Users can log out. Old tokens are rejected after logout.

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T086 [P] Add OpenTelemetry tracing instrumentation to FastAPI in `backend/src/core/telemetry.py`
- [x] T087 [P] Add OpenTelemetry instrumentation for SQLAlchemy in `backend/src/core/telemetry.py`
- [x] T088 [P] Create custom metrics for auth events and request latency in `backend/src/core/metrics.py`
- [x] T089 [P] Add structured JSON logging configuration in `backend/src/core/logging.py`
- [x] T090 Create protected route wrapper for frontend pages in `frontend/src/components/protected-route.tsx`
- [x] T091 [P] Add loading states to frontend components in `frontend/src/components/`
- [x] T092 [P] Add error boundary component for frontend in `frontend/src/components/error-boundary.tsx`
- [x] T093 Run all backend tests and ensure 80%+ coverage in `backend/`
- [x] T094 Run quickstart.md validation - verify development setup works end-to-end
- [x] T095 Security hardening: review all endpoints for proper auth checks in `backend/src/api/routes/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational - Authentication foundation
- **US2 (Phase 4)**: Depends on Foundational + US1 (needs auth to create tasks)
- **US3 (Phase 5)**: Depends on US2 (needs tasks to test isolation)
- **US4 (Phase 6)**: Depends on US2 + US3 (needs tasks + isolation)
- **US5 (Phase 7)**: Depends on US2 + US3 (needs tasks + isolation)
- **US6 (Phase 8)**: Depends on US2 + US3 (needs tasks + isolation)
- **US7 (Phase 9)**: Depends on US1 (needs auth to test logout)
- **Polish (Phase 10)**: Depends on all user stories

### User Story Dependencies (Summary)

```
Phase 1: Setup
    ↓
Phase 2: Foundational (BLOCKS ALL)
    ↓
Phase 3: US1 (Auth) ←────────────────────┐
    ↓                                     │
Phase 4: US2 (Create Tasks)               │
    ↓                                     │
Phase 5: US3 (Isolation)                  │
    ↓                                     │
Phase 6: US4 (Update) ─────┐              │
Phase 7: US5 (Complete) ───┼─ Can run in parallel
Phase 8: US6 (Delete) ─────┘              │
                                          │
Phase 9: US7 (Logout) ────────────────────┘
    ↓
Phase 10: Polish
```

### Within Each User Story

1. Tests MUST be written and FAIL before implementation
2. Models before services
3. Services before endpoints
4. Backend before frontend integration
5. Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1**: T003-T008 can run in parallel (different files)
- **Phase 2**: T011-T012 (models), T022-T024 (frontend setup) can run in parallel
- **Each US Phase**: All test tasks can run in parallel
- **US4/US5/US6**: Can run in parallel after US3 completes
- **Phase 10**: T086-T092 can run in parallel

---

## Parallel Example: Phase 2 (Foundational)

```bash
# Launch backend models in parallel:
Task T011: "Create User SQLModel entity in backend/src/models/user.py"
Task T012: "Create Task SQLModel entity in backend/src/models/task.py"

# Launch frontend setup in parallel:
Task T022: "Configure Better Auth server in frontend/src/lib/auth.ts"
Task T023: "Create Better Auth client in frontend/src/lib/auth-client.ts"
Task T024: "Create API client in frontend/src/lib/api-client.ts"
```

## Parallel Example: User Story 2 (Tests)

```bash
# Launch all US2 tests in parallel:
Task T038: "Contract test for create task"
Task T039: "Contract test for list tasks"
Task T040: "Contract test for get task by ID"
Task T041: "Integration test for task persistence"
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: US1 - User Registration and Login
4. Complete Phase 4: US2 - Persistent Task Creation
5. Complete Phase 5: US3 - User Task Isolation
6. **STOP and VALIDATE**: Test US1-US3 independently
7. Deploy/demo MVP with auth + task creation + isolation

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 (Auth) → Test → First deliverable (users can register/login)
3. Add US2 (Create) → Test → Second deliverable (users can create tasks)
4. Add US3 (Isolation) → Test → **MVP Complete** (multi-user ready)
5. Add US4 (Update) → Test → Enhanced task management
6. Add US5 (Complete) → Test → Completion tracking
7. Add US6 (Delete) → Test → Full CRUD operations
8. Add US7 (Logout) → Test → Complete auth flow
9. Add Polish → Production ready

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: US1 (Auth) → US7 (Logout)
   - Developer B: US2 (Create) → US4 (Update)
   - Developer C: US3 (Isolation) → US5 (Complete) → US6 (Delete)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (Red-Green-Refactor)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Backend tests use pytest; frontend tests use Jest/Vitest
- All API endpoints require JWT auth per FR-015
- Return 404 (not 403) for non-owned resources per FR-013
