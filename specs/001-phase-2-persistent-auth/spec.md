# Feature Specification: Phase II - Persistent Storage with Authentication

**Feature Branch**: `001-phase-2-persistent-auth`
**Created**: 2026-01-07
**Status**: Draft
**Phase**: II of V
**Constitution Reference**: `.specify/memory/constitution.md` v1.0.0
**Input**: User description: Phase II persistent storage with Better Auth JWT authentication, Neon PostgreSQL database, API security with user isolation

## Overview

Phase II evolves the in-memory todo application from Phase I into a persistent, multi-user system with secure authentication. This phase introduces:

- User authentication via Better Auth with JWT tokens
- Persistent task storage in Neon PostgreSQL
- User isolation ensuring each user only sees their own tasks
- RESTful API endpoints secured with JWT verification
- Forward-compatible design for Phase III AI integration

All Phase I functionality is preserved and enhanced with persistence and multi-user support.

## User Scenarios & Testing

### User Story 1 - User Registration and Login (Priority: P1)

As a new user, I want to create an account and log in so that my tasks are saved and accessible only to me.

**Why this priority**: Authentication is the foundation for multi-user support. Without user identity, task ownership and persistence have no meaning. This unlocks all subsequent user stories.

**Independent Test**: Can be fully tested by creating an account, logging in, and verifying a valid session/token is established. Delivers secure identity management.

**Acceptance Scenarios**:

1. **Given** no existing account, **When** user registers with email and password, **Then** account is created and user receives a valid JWT token.

2. **Given** an existing account, **When** user logs in with correct credentials, **Then** user receives a valid JWT token for subsequent requests.

3. **Given** an existing account, **When** user logs in with incorrect password, **Then** authentication fails with clear error message and no token is issued.

4. **Given** a valid JWT token, **When** user makes an authenticated request, **Then** the request succeeds with user identity verified.

5. **Given** an expired or invalid JWT token, **When** user makes a request, **Then** the request is rejected with 401 Unauthorized.

---

### User Story 2 - Persistent Task Creation (Priority: P1)

As an authenticated user, I want to create tasks that persist across sessions so that I can access them later.

**Why this priority**: Task persistence is the core value proposition of Phase II. Without this, the application remains ephemeral like Phase I.

**Independent Test**: Can be fully tested by creating a task, logging out, logging back in, and verifying the task still exists. Delivers data durability.

**Acceptance Scenarios**:

1. **Given** an authenticated user with no tasks, **When** user creates a task with title "Buy groceries", **Then** the task is stored in the database and associated with the user.

2. **Given** an authenticated user who created tasks, **When** user logs out and logs back in, **Then** all previously created tasks are still visible.

3. **Given** an authenticated user, **When** user creates a task, **Then** the task is assigned a unique persistent identifier.

4. **Given** an unauthenticated request, **When** attempting to create a task, **Then** the request is rejected with 401 Unauthorized.

---

### User Story 3 - User Task Isolation (Priority: P1)

As a user, I want to see only my own tasks so that my data remains private from other users.

**Why this priority**: User isolation is a security requirement. Users must trust that their data is private. This is foundational for multi-user support.

**Independent Test**: Can be fully tested by creating tasks as User A, logging in as User B, and verifying User B cannot see User A's tasks.

**Acceptance Scenarios**:

1. **Given** User A with tasks and User B with different tasks, **When** User A views their task list, **Then** only User A's tasks are displayed.

2. **Given** User A with tasks, **When** User B attempts to access User A's task by ID, **Then** the request returns 404 Not Found (not 403, to avoid information leakage).

3. **Given** User A with tasks, **When** User B attempts to update or delete User A's task, **Then** the request is rejected.

4. **Given** any user, **When** requesting tasks without authentication, **Then** no tasks are returned and request is rejected with 401.

---

### User Story 4 - Persistent Task Updates (Priority: P2)

As an authenticated user, I want to update my existing tasks so that I can correct mistakes or refine task details.

**Why this priority**: Task modification is essential for practical task management but depends on tasks existing first (US2) and being properly isolated (US3).

**Independent Test**: Can be fully tested by creating a task, updating it, and verifying changes persist across sessions.

**Acceptance Scenarios**:

1. **Given** an authenticated user with an existing task, **When** user updates the task title, **Then** the change is persisted to the database.

2. **Given** an authenticated user with an existing task, **When** user updates the task description, **Then** the change is persisted to the database.

3. **Given** an authenticated user, **When** user attempts to update with an empty title, **Then** the update is rejected with validation error.

4. **Given** an authenticated user, **When** user updates a non-existent task, **Then** 404 Not Found is returned.

---

### User Story 5 - Persistent Task Completion (Priority: P2)

As an authenticated user, I want to mark tasks as complete and have that status persist so that I can track my progress over time.

**Why this priority**: Completion tracking is a core todo feature that depends on persistent tasks existing.

**Independent Test**: Can be fully tested by creating a task, marking it complete, logging out/in, and verifying completion status persisted.

**Acceptance Scenarios**:

1. **Given** an authenticated user with an incomplete task, **When** user marks the task complete, **Then** completion status is persisted to the database.

2. **Given** an authenticated user with a complete task, **When** user marks the task incomplete, **Then** the status change is persisted.

3. **Given** task completion changes, **When** user logs out and back in, **Then** completion status reflects the last saved state.

---

### User Story 6 - Persistent Task Deletion (Priority: P3)

As an authenticated user, I want to delete tasks permanently so that I can remove items no longer relevant.

**Why this priority**: Deletion is less frequently used but necessary for list management.

**Independent Test**: Can be fully tested by creating a task, deleting it, and verifying it no longer exists even after re-login.

**Acceptance Scenarios**:

1. **Given** an authenticated user with a task, **When** user deletes the task, **Then** the task is permanently removed from the database.

2. **Given** a deleted task, **When** user logs out and back in, **Then** the deleted task does not reappear.

3. **Given** an authenticated user, **When** user attempts to delete another user's task, **Then** 404 Not Found is returned.

---

### User Story 7 - User Logout (Priority: P3)

As an authenticated user, I want to log out so that my session is terminated securely.

**Why this priority**: Logout is important for security but is a supplementary feature.

**Independent Test**: Can be fully tested by logging in, logging out, and verifying subsequent requests with the old token fail.

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** user logs out, **Then** the session is terminated.

2. **Given** a logged-out user, **When** attempting to use the previous token, **Then** requests are rejected.

---

### Edge Cases

- What happens when user registers with an already-used email? System rejects with clear error.
- What happens when JWT expires mid-session? User receives 401 and must re-authenticate.
- What happens when database is temporarily unavailable? User receives appropriate error without data corruption.
- What happens when user provides malformed JSON in API request? System returns 400 Bad Request with validation details.
- What happens when concurrent updates occur to the same task? Last write wins with optimistic locking (version field), no data corruption.

## Requirements

### Functional Requirements

#### Authentication
- **FR-001**: System MUST allow user registration with email and password
- **FR-002**: System MUST issue JWT token upon successful authentication
- **FR-003**: System MUST verify JWT token on every API request to protected endpoints
- **FR-004**: System MUST reject requests with invalid, expired, or missing JWT tokens with 401 Unauthorized
- **FR-005**: System MUST allow users to log out and invalidate their session
- **FR-006**: System MUST use a shared secret (`BETTER_AUTH_SECRET`) for JWT signing/verification
- **FR-006a**: JWT tokens MUST expire after 24 hours

#### Task Persistence
- **FR-007**: System MUST persist tasks to Neon PostgreSQL database
- **FR-008**: System MUST associate each task with its owner user
- **FR-009**: System MUST preserve all Phase I task attributes (id, title, description, completed, created_at) and add updated_at timestamp
- **FR-010**: System MUST add user_id foreign key to task records

#### User Isolation
- **FR-011**: System MUST filter all task queries by authenticated user ID
- **FR-012**: System MUST prevent users from accessing other users' tasks
- **FR-013**: System MUST return 404 (not 403) when accessing non-owned tasks to prevent enumeration
- **FR-022**: System MUST extract user_id exclusively from JWT payload (URL user_id parameters ignored)

#### API Endpoints
- **FR-014**: System MUST provide REST API endpoints for all task operations
- **FR-014a**: Task list endpoints MUST support cursor-based pagination with after_id parameter
- **FR-015**: All `/api/*` endpoints MUST require valid JWT authentication
- **FR-016**: System MUST return appropriate HTTP status codes (200, 201, 400, 401, 404, 500)
- **FR-017**: System MUST return JSON responses for all API endpoints

#### Data Integrity
- **FR-018**: System MUST validate all inputs before database operations
- **FR-019**: System MUST handle database errors gracefully without exposing internal details
- **FR-020**: System MUST maintain referential integrity between users and tasks
- **FR-020a**: System MUST use hard delete for task removal (permanent deletion, no soft delete)
- **FR-020b**: System MUST use optimistic locking with version field for concurrent edit detection

### Key Entities

- **User**: Represents an authenticated user with email, password hash, and unique identifier. Owns zero or more tasks.

- **Task**: Represents a todo item with id, title, description, completed status, created_at timestamp, updated_at timestamp, version (int for optimistic locking), and user_id foreign key. Belongs to exactly one user.

- **Session/Token**: Represents an authenticated session via JWT containing user identity and expiration.

## Non-Functional Requirements

### NFR-001: Security
All sensitive data (passwords) must be hashed. JWT tokens must be signed with shared secret. No sensitive data in logs or error messages.

### NFR-002: Performance
API responses must complete within 500ms under normal load. Database queries must be optimized with appropriate indexes.

### NFR-003: Reliability
System must handle database connection failures gracefully. Failed requests must not corrupt data.

### NFR-004: Forward Compatibility
All APIs and schemas must be agent-consumable for Phase III AI integration. Design must not block MCP tool exposure or Kubernetes deployment.

### NFR-005: Observability
System MUST emit full tracing via OpenTelemetry for all API requests and database operations. System MUST expose custom metrics for auth events, request latency, and error rates.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can register, log in, and receive JWT token within 3 seconds
- **SC-002**: Tasks persist across sessions with 100% reliability
- **SC-003**: User isolation is provably enforced - no cross-user data access possible
- **SC-004**: All API endpoints return responses within 500ms under normal conditions
- **SC-005**: System supports at least 100 concurrent authenticated users
- **SC-006**: JWT verification succeeds on every authenticated request
- **SC-007**: Zero security vulnerabilities in authentication flow (no token leakage, no SQL injection)
- **SC-008**: All Phase I acceptance tests continue to pass (with authentication added)

## Agent Responsibilities

### SpecExecutionAgent

- Validate all implementation against this specification
- Block any feature not defined in this spec
- Enforce Phase II boundaries (no Phase III+ features)
- Gate approval for task completion

### StateManagementAgent

- Manage database connections and transactions
- Ensure user isolation in all queries
- Handle state transitions through defined operations
- Maintain data integrity

## Constraints and Prohibitions

### Phase II Boundaries

1. **Required**: Better Auth for authentication
2. **Required**: JWT tokens for API authorization
3. **Required**: Neon PostgreSQL for persistence
4. **Required**: User isolation for all task operations

### Absolutely Forbidden in Phase II

1. **Natural Language Processing**: Reserved for Phase III
2. **AI/Chatbot Integration**: Reserved for Phase III
3. **Container Deployment**: Reserved for Phase IV
4. **Kubernetes/Cloud**: Reserved for Phase IV/V

### Non-Negotiable Rule

> If implementation output is incorrect, **update the spec — never the code.**

This rule governs the entire Evolution of Todo project.

## Out of Scope

- Natural language task parsing (Phase III)
- AI-powered task suggestions (Phase III)
- Docker containerization (Phase IV)
- Kubernetes deployment (Phase IV/V)
- Social login providers (future enhancement)
- Password reset functionality (future enhancement)
- Email verification (future enhancement)
- Rate limiting (future enhancement)

## Clarifications

### Session 2026-01-07

- Q: Should task deletion be hard delete or soft delete? → A: Hard delete - permanently remove task record from database
- Q: Should user_id be extracted from JWT only or allow URL parameters? → A: JWT only - user_id extracted exclusively from JWT payload, URL user_id parameters ignored
- Q: Should tasks include an updated_at timestamp? → A: Yes - add updated_at timestamp, automatically set on every task modification
- Q: How should JWT token expiration and refresh be handled? → A: 24-hour expiration with no refresh token
- Q: How should task list pagination be handled for users with many tasks? → A: Cursor-based pagination with after_id for efficient infinite scroll
- Q: What observability signals (logs/metrics) should the system emit for debugging and monitoring? → A: Full tracing with OpenTelemetry + custom metrics
- Q: For concurrent edits to the same task, what conflict resolution strategy should be used? → A: Last write wins with optimistic locking (version field)
- Q: What fields should the Task entity include beyond the currently specified attributes? → A: Add version (int) for optimistic locking + default page_size in API response

## Assumptions

- Better Auth library handles password hashing securely
- Neon PostgreSQL provides reliable managed database service
- JWT tokens expire after 24 hours (no refresh token in Phase II)
- Single shared secret is sufficient for Phase II (can evolve to key rotation in future)
- RESTful API is sufficient (no WebSocket/real-time requirements)
