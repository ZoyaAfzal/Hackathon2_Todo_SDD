<!--
  SYNC IMPACT REPORT
  ==================
  Version change: 1.0.0 → 1.1.0
  Bump rationale: MINOR — material expansion of Phase III definition
  with concrete technology stack, constraints, and success criteria.

  Modified Principles:
    - V. Conversational Interface Determinism (expanded with MCP tool
      governance and stateless API rules)

  Added Sections:
    - Phase III Technology Stack (under Phase Definitions)
    - Phase III Success Criteria (under Phase Definitions)
    - Phase III State Rules (under State and Data Rules)

  Removed Sections: None

  Templates requiring updates:
    - .specify/templates/plan-template.md: ✅ no update needed
    - .specify/templates/spec-template.md: ✅ no update needed
    - .specify/templates/tasks-template.md: ✅ no update needed

  Follow-up TODOs: None
-->

# The Evolution of Todo Constitution

This Constitution governs the development of a 5-Phase evolutionary
system that begins as an In-Memory Python Console App and evolves into
a Cloud-Native AI-Powered Todo Chatbot deployed on Kubernetes. All
agents, humans, and automated processes operating within this project
MUST adhere to every principle and rule defined herein.

## Core Principles

### I. Spec-First Development

Every feature, enhancement, or modification MUST begin with a complete
specification before any implementation occurs. Specifications MUST
include acceptance criteria, user scenarios, functional requirements,
and success metrics. No agent or human may write implementation code
without a ratified specification. Specifications MUST be stored in the
designated `specs/<feature>/spec.md` location and MUST be reviewed
before proceeding to planning.

Rationale: Spec-first ensures alignment, prevents scope creep, and
provides a verifiable contract for all stakeholders.

### II. Phase-Bound Evolution

The system evolves through exactly five phases, each with explicit
boundaries and deliverables:

- Phase I: In-Memory Python Console App with CLI-based todo management
- Phase II: Persistent Storage integration with database backend
- Phase III: AI-Powered Todo Chatbot with MCP tools and Agents SDK
- Phase IV: Containerized Deployment with Docker and local Kubernetes
- Phase V: Cloud-Native Production Deployment on managed Kubernetes

Each phase MUST be fully completed, tested, and validated before the
next phase begins. No phase may be skipped. No functionality from a
future phase may be implemented prematurely. Phase transitions require
explicit quality gate approval.

Rationale: Phased evolution ensures incremental complexity, reduces
risk, and maintains system integrity at each milestone.

### III. Test-First Discipline

All implementation MUST follow the Red-Green-Refactor cycle:

1. Tests MUST be written before implementation code
2. Tests MUST fail before implementation begins
3. Implementation MUST satisfy failing tests
4. Refactoring MUST maintain passing tests

No implementation code may be committed without corresponding tests.
Test coverage MUST be maintained at or above 80 percent for all new
code. Integration tests MUST validate phase-specific functionality.
Contract tests MUST verify API boundaries.

Rationale: Test-first prevents defects, ensures requirements are met,
and provides a safety net for refactoring.

### IV. State Transparency

All application state MUST be explicit, traceable, and owned by a
single component. Hidden or implicit state is forbidden.

Phase I Constraints:
- State MUST reside in memory as explicit data structures
- State MUST be initialized to a known empty state on startup
- State transitions MUST be triggered only by explicit user commands

Evolution of State:
- Phase II: State MUST transition to persistent storage with explicit
  migration
- Phase III: Conversational context and todo state MUST be stored in
  PostgreSQL. No in-memory sessions permitted. All state MUST survive
  process restarts.
- Phase IV: State MUST be containerized with volume mounts or external
  stores
- Phase V: State MUST use cloud-native persistence with backup and
  recovery

State ownership MUST be documented in the specification. No component
may mutate state owned by another component.

Rationale: Explicit state prevents bugs, simplifies debugging, and
ensures predictable behavior.

### V. Conversational Interface Determinism

When the conversational interface is introduced in Phase III, the
following rules apply:

- Natural language input MUST be parsed into a canonical intent
  representation via MCP tools
- Intent extraction MUST be deterministic for identical inputs
- Ambiguous inputs MUST trigger clarification requests, not assumptions
- All intents MUST map to exactly one MCP tool invocation or to a
  rejection with explanation
- The mapping from intent to action MUST be documented and testable
- Safety-critical actions MUST require explicit confirmation

MCP Tool Governance:
- All todo operations MUST be exposed as MCP tools: `add_task`,
  `list_tasks`, `update_task`, `complete_task`, `delete_task`
- Each MCP tool MUST have a valid JSON schema
- MCP tool invocations MUST be logged for traceability
- The AI agent MUST use MCP tools exclusively for state mutations;
  direct database access from the agent is forbidden

Stateless API Rules:
- The chat endpoint (`POST /api/{user_id}/chat`) MUST be stateless
- Conversation context MUST be loaded from the database per request
- No in-memory session storage is permitted
- Each response MUST include a `conversation_id` for resumption

Rationale: Deterministic language handling prevents unexpected behavior
and ensures user trust. MCP tool governance ensures auditable,
well-defined operations.

### VI. Context7 MCP Governance

Context7 MCP is the single source of truth for all project knowledge.
This is mandatory across all phases.

Context7 MCP MUST store:
- Project specifications and requirements
- Architectural decisions and rationale
- Phase history and transition records
- Agent execution logs and outcomes

All agents MUST:
- Read from Context7 MCP before executing any action
- Write decisions, summaries, and outcomes back to Context7 MCP
- Never rely solely on transient memory for decision-making
- Synchronize state with Context7 MCP after every significant operation

Context drift without Context7 MCP updates is forbidden. Any agent
operating without Context7 MCP synchronization is in violation of this
Constitution.

Rationale: Centralized knowledge governance ensures consistency,
enables audit trails, and prevents information silos.

### VII. Cloud-Native Parity

Local development, staging, and production environments MUST maintain
functional parity:

- Containerization MUST use Docker with multi-stage builds
- Container images MUST be immutable after build
- Kubernetes manifests MUST be identical for local and cloud deployment
- Environment-specific configuration MUST use ConfigMaps and Secrets,
  not code changes
- Local Kubernetes MUST use Kind, Minikube, or equivalent
- Cloud Kubernetes MUST use managed services with documented
  configuration

Deployment MUST be reproducible: identical inputs MUST produce
identical deployments. Environment immutability MUST be enforced
through infrastructure-as-code.

Rationale: Parity eliminates environment-specific bugs and ensures
deployment confidence.

### VIII. Quality Gate Enforcement

Phase advancement requires passing all quality gates:

Specification Gate:
- All placeholders resolved
- Acceptance criteria defined and testable
- User scenarios complete with edge cases
- Functional requirements enumerated

Planning Gate:
- Technical context documented
- Constitution compliance verified
- Project structure defined
- Complexity justified if exceeding limits

Implementation Gate:
- All tests passing
- Code coverage at or above threshold
- No security vulnerabilities in dependencies
- Documentation updated

Deployment Gate:
- Container builds successfully
- Kubernetes manifests validated
- Health checks passing
- Rollback procedure documented

Failure at any gate MUST halt progression. Rollback to the previous
stable state MUST be performed if a gate failure cannot be resolved.

Rationale: Quality gates prevent defective artifacts from advancing
and maintain system integrity.

### IX. Agent Autonomy Boundaries

AI agents operating within this project MUST:

- Execute only within the scope defined by specifications
- Request human input when encountering ambiguity
- Document all decisions in Context7 MCP
- Create Prompt History Records for every significant interaction
- Suggest Architectural Decision Records when significant design
  choices are made

Agents MUST NOT:

- Invent APIs, data structures, or contracts not in specifications
- Skip specification or planning phases
- Operate without Context7 MCP synchronization
- Make architectural decisions without human approval
- Commit code without corresponding tests

Rationale: Bounded autonomy ensures predictability and maintains human
oversight.

### X. Observability and Traceability

All system components MUST emit structured logs, metrics, and traces:

- Logs MUST use structured JSON format with correlation IDs
- Metrics MUST cover request counts, latencies, and error rates
- Traces MUST span across service boundaries
- All user actions MUST be auditable

Prompt History Records MUST be created for:
- Implementation work and code changes
- Planning and architecture discussions
- Debugging sessions
- Specification creation and updates

Rationale: Observability enables debugging, auditing, and continuous
improvement.

### XI. Prohibited Actions

The following actions are expressly forbidden:

- Writing implementation code without a ratified specification
- Skipping phases or implementing future-phase functionality prematurely
- Committing code without tests
- Operating agents without Context7 MCP synchronization
- Hardcoding secrets, tokens, or credentials in source code
- Creating hidden or implicit state
- Bypassing quality gates
- Making architectural decisions without documentation
- Modifying production systems without rollback capability
- Mixing responsibilities across phase boundaries
- Storing session state in memory in Phase III or later

Violation of any prohibition MUST halt work until remediated.

Rationale: Explicit prohibitions prevent common failure modes and
maintain project integrity.

## Phase Definitions

### Phase I: In-Memory Console Application

Scope: Python console application with in-memory todo storage
Deliverables: CLI interface, CRUD operations, in-memory state management
Success Criteria: All todo operations functional, tests passing,
no persistence

### Phase II: Persistent Storage

Scope: Add durable storage to Phase I application
Deliverables: Database backend, migration from in-memory, data integrity
Success Criteria: Todos persist across restarts, state recovery validated

### Phase III: AI-Powered Todo Chatbot

Scope: Natural language interface for todo operations via AI agent
with MCP tools

Technology Stack:
- Backend: FastAPI + OpenAI Agents SDK
- MCP: Official MCP Python SDK
- Database: Neon PostgreSQL + SQLModel
- Auth: Better Auth (JWT verification)
- Secrets: Environment variables only

Constraints:
- Endpoint: `POST /api/{user_id}/chat`
- No in-memory sessions; all state in database
- Code generated via Claude Code only
- Must run locally

Deliverables:
- Chat API returning `conversation_id` and reply
- MCP tools: `add_task`, `list_tasks`, `update_task`, `complete_task`,
  `delete_task`
- Conversation persistence in PostgreSQL
- Multi-turn chat frontend support

Success Criteria:
- Chat API responds within 3 seconds
- 95% or higher correct MCP tool usage
- Messages and conversations persist across restarts
- Resume via `conversation_id`
- Auth required; no cross-user data access
- Clear error messages; no crashes; errors logged
- Friendly confirmation after each action

### Phase IV: Containerized Deployment

Scope: Docker and local Kubernetes deployment
Deliverables: Dockerfile, Kubernetes manifests, local cluster deployment
Success Criteria: Application runs in container, Kubernetes deployment
succeeds

### Phase V: Cloud-Native Production

Scope: Production deployment on managed Kubernetes
Deliverables: Cloud infrastructure, production manifests, monitoring
Success Criteria: Application runs in cloud, observability operational

## State and Data Rules

### In-Memory Constraints (Phase I)

- State MUST be initialized to an empty collection on application start
- State MUST be a single, explicit data structure
- No background state modifications permitted
- State inspection MUST be available for debugging

### Persistence Evolution (Phase II onward)

- Persistence mechanism MUST be specified before implementation
- Migration from in-memory to persistent MUST preserve all data
- Schema changes MUST use explicit migrations
- Rollback capability MUST be maintained

### Phase III Data Rules

- All todo records MUST be stored in Neon PostgreSQL via SQLModel
- Conversation messages MUST be stored in the database with ordering
- Conversations MUST be resumable via `conversation_id`
- Each user's data MUST be isolated; cross-user access is forbidden
- MCP tool results MUST be persisted as part of conversation history

### State Ownership

- Each state element MUST have a single owning component
- Cross-component state access MUST use defined interfaces
- State mutations MUST be logged for traceability

## Quality Gates and Validation

### Pre-Implementation Validation

- Specification completeness check: all required sections present
- Acceptance criteria verification: all criteria are testable
- Constitution alignment: no principle violations

### Post-Implementation Validation

- Test execution: all tests pass
- Coverage verification: threshold met
- Security scan: no critical vulnerabilities
- Documentation review: all changes documented

### Phase Transition Validation

- All phase deliverables complete
- Quality gates passed
- Context7 MCP synchronized
- Stakeholder approval obtained

## Governance

### Amendment Procedure

1. Proposed amendments MUST be documented with rationale
2. Amendments MUST be reviewed for impact on existing artifacts
3. Approval requires explicit stakeholder consent
4. Amendments MUST be versioned according to semantic versioning:
   - MAJOR: Backward incompatible principle changes or removals
   - MINOR: New principles or sections added
   - PATCH: Clarifications and non-semantic refinements

### Compliance Review

- All pull requests MUST verify Constitution compliance
- Violations MUST be remediated before merge
- Repeated violations require process review

### Precedence

This Constitution supersedes all other project practices. In case of
conflict between this Constitution and any other document, this
Constitution prevails.

**Version**: 1.1.0 | **Ratified**: 2026-01-02 | **Last Amended**: 2026-02-02
