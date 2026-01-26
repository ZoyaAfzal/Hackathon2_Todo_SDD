# Implementation Plan: Phase II - Persistent Storage with Authentication

**Branch**: `001-phase-2-persistent-auth` | **Date**: 2026-01-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-phase-2-persistent-auth/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Phase II evolves the Phase I in-memory todo application into a persistent, multi-user system with secure JWT authentication. The implementation uses a full-stack web architecture with Next.js frontend, FastAPI backend, SQLModel ORM, Neon PostgreSQL database, and Better Auth for authentication with JWT token verification.

## Technical Context

**Language/Version**: Python 3.11+ (Backend), TypeScript 5.x (Frontend)
**Primary Dependencies**: FastAPI, SQLModel, Better Auth, Next.js 16 (App Router), OpenTelemetry
**Storage**: Neon PostgreSQL (serverless)
**Testing**: pytest (backend), Jest/Vitest (frontend)
**Target Platform**: Linux server (development), Cloud (production-ready)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: API responses < 500ms p95, 100 concurrent users
**Constraints**: JWT 24-hour expiration, cursor-based pagination, optimistic locking
**Scale/Scope**: Multi-user, persistent storage, user isolation enforced

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-First Development | ✅ PASS | Specification complete with 7 user stories, 24 FRs, 8 SCs |
| II. Phase-Bound Evolution | ✅ PASS | Phase II scope only; Phase III+ features explicitly forbidden |
| III. Test-First Discipline | ✅ PASS | Tests will precede implementation per TDD cycle |
| IV. State Transparency | ✅ PASS | State in PostgreSQL with explicit ownership (user_id FK) |
| V. Conversational Interface Determinism | ⏭️ N/A | Reserved for Phase III |
| VI. Context7 MCP Governance | ✅ PASS | Using Context7 for library documentation |
| VII. Cloud-Native Parity | ⏭️ N/A | Reserved for Phase IV+ |
| VIII. Quality Gate Enforcement | ✅ PASS | Gates defined in spec and checklist |
| IX. Agent Autonomy Boundaries | ✅ PASS | Agents follow spec, request human input on ambiguity |
| X. Observability and Traceability | ✅ PASS | NFR-005 requires OpenTelemetry tracing + metrics |
| XI. Prohibited Actions | ✅ PASS | No violations; no hardcoded secrets, tests required |

**Result**: All applicable principles pass. Ready for Phase 0 research.

## Project Structure

### Documentation (this feature)

```text
specs/001-phase-2-persistent-auth/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── api-contract.md  # REST API specification
│   └── auth-contract.md # Authentication flow specification
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Web application structure (frontend + backend)
backend/
├── src/
│   ├── models/          # SQLModel entities (User, Task)
│   ├── services/        # Business logic (task_service, auth_service)
│   ├── api/             # FastAPI routes and dependencies
│   │   ├── routes/      # Endpoint handlers
│   │   └── deps/        # JWT verification, DB session
│   └── core/            # Config, security, database connection
└── tests/
    ├── unit/            # Unit tests for services, models
    ├── contract/        # API contract tests
    └── integration/     # Full flow integration tests

frontend/
├── src/
│   ├── app/             # Next.js App Router pages
│   ├── components/      # React components
│   ├── lib/             # Better Auth client, API client
│   └── types/           # TypeScript types
└── tests/               # Frontend tests
```

**Structure Decision**: Web application pattern selected. Backend (FastAPI) handles API and JWT verification. Frontend (Next.js) handles UI and Better Auth client. Both share JWT secret for token validation.

## Complexity Tracking

> **No violations requiring justification**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| *None* | *N/A* | *N/A* |

## Phase 0: Research Output

*To be generated in research.md*

Key research areas:
1. Better Auth JWT integration with FastAPI
2. SQLModel schema design for User and Task entities
3. Neon PostgreSQL connection pooling with serverless
4. OpenTelemetry instrumentation for FastAPI
5. Cursor-based pagination implementation
6. Optimistic locking patterns

## Phase 1: Design Output

*To be generated in data-model.md and contracts/*

Deliverables:
- Data model with User and Task entities
- API contract for all endpoints
- Authentication flow contract
- Quickstart guide for development setup
