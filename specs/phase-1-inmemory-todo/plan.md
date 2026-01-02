# Implementation Plan: Phase I - In-Memory Todo Console Application

**Branch**: `phase-1-inmemory-todo` | **Date**: 2026-01-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/phase-1-inmemory-todo/spec.md`
**Constitution**: `.specify/memory/constitution.md` v1.0.0

## Summary

Phase I establishes the foundational in-memory Python console application for todo management. This phase implements a deterministic CLI with CRUD operations for tasks, enforcing strict in-memory state management with no persistence. The application serves as the evolutionary base for all subsequent phases.

Primary Requirements:
- Task CRUD operations (Create, Read, Update, Delete)
- Completion status toggling
- Structured CLI command interface
- In-memory state with explicit ownership

Technical Approach:
- Pure Python 3.11+ with standard library only
- Dataclass-based domain models
- Single-threaded, synchronous execution
- Command pattern for CLI operations

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: None (Python standard library only)
**Storage**: In-memory (list/dict data structures)
**Testing**: pytest with coverage reporting (or unittest as fallback)
**Target Platform**: Cross-platform console (Linux, macOS, Windows)
**Project Type**: Single project
**Performance Goals**: All operations complete in under 100ms
**Constraints**: No file I/O, no network, no external packages, no persistence
**Scale/Scope**: Single user, single session, ephemeral state

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-First Development
- [x] Specification exists at `specs/phase-1-inmemory-todo/spec.md`
- [x] Acceptance criteria defined for all 6 user stories
- [x] 25 functional requirements enumerated
- [x] Success metrics defined (SC-001 through SC-008)
- **Status**: PASS

### Principle II: Phase-Bound Evolution
- [x] This plan is for Phase I only
- [x] No Phase II+ features included (no persistence, no NLP, no containers)
- [x] Out of scope items explicitly listed
- **Status**: PASS

### Principle III: Test-First Discipline
- [x] Test strategy defined (pytest, 80% coverage minimum)
- [x] Acceptance scenarios provide test cases
- [x] Red-Green-Refactor cycle will be enforced during implementation
- **Status**: PASS (to be verified during implementation)

### Principle IV: State Transparency
- [x] StateManagementAgent owns TaskList
- [x] State initialization defined (empty on start)
- [x] No hidden state permitted
- [x] State transitions through explicit operations only
- **Status**: PASS

### Principle V: Conversational Interface Determinism
- [x] Not applicable in Phase I (NLP reserved for Phase III)
- [x] Structured CLI commands only
- **Status**: N/A (Phase III)

### Principle VI: Context7 MCP Governance
- [x] Specification stored and tracked
- [x] Design decisions documented in this plan
- [x] Agent responsibilities defined
- **Status**: PASS

### Principle VII: Cloud-Native Parity
- [x] Not applicable in Phase I (containers reserved for Phase IV)
- **Status**: N/A (Phase IV)

### Principle VIII: Quality Gate Enforcement
- [x] Specification gate passed (spec.md complete)
- [x] Planning gate in progress (this document)
- [x] Implementation gate criteria defined
- **Status**: PASS

### Principle IX: Agent Autonomy Boundaries
- [x] SpecExecutionAgent responsibilities defined
- [x] StateManagementAgent responsibilities defined
- [x] ConversationToTodoAgent responsibilities defined
- [x] Skill mappings documented
- **Status**: PASS

### Principle X: Observability and Traceability
- [x] PHR creation required for all significant operations
- [x] Structured output format defined
- **Status**: PASS

### Principle XI: Prohibited Actions
- [x] No manual coding (Claude Code generates all code)
- [x] No persistence mechanisms
- [x] No external dependencies
- [x] No NLP or fuzzy matching
- **Status**: PASS

**Overall Constitution Check**: PASS - All applicable principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/phase-1-inmemory-todo/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (complete)
├── research.md          # Phase 0 output (complete)
├── data-model.md        # Phase 1 output (complete)
├── quickstart.md        # Phase 1 output (complete)
├── contracts/           # Phase 1 output (complete)
│   └── cli-contract.md  # CLI command contracts
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── main.py              # Application entry point
├── models/
│   ├── __init__.py
│   └── task.py          # Task dataclass
├── services/
│   ├── __init__.py
│   ├── task_service.py  # TaskManagementSkill implementation
│   ├── query_service.py # TaskQuerySkill implementation
│   └── validation.py    # ValidationSkill implementation
├── state/
│   ├── __init__.py
│   └── store.py         # StateManagementAgent implementation
└── cli/
    ├── __init__.py
    ├── parser.py        # Command parsing
    ├── commands.py      # Command handlers
    └── formatter.py     # Output formatting

tests/
├── __init__.py
├── conftest.py          # pytest fixtures
├── unit/
│   ├── __init__.py
│   ├── test_task_model.py
│   ├── test_task_service.py
│   ├── test_query_service.py
│   ├── test_validation.py
│   └── test_store.py
├── integration/
│   ├── __init__.py
│   └── test_cli_operations.py
└── contract/
    ├── __init__.py
    └── test_command_contracts.py
```

**Structure Decision**: Single project structure selected. This is a standalone console application with no web, API, or mobile components. All code resides under `src/` with corresponding tests under `tests/`.

## Complexity Tracking

> No Constitution violations requiring justification. Design adheres to all principles.

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| No external deps | Python stdlib only | Constitution Principle XI prohibits external packages |
| No persistence | In-memory dict | Phase I constraint per Constitution Principle II |
| Synchronous only | No async/await | NFR-003 single-user, no concurrency needed |

## Design Decisions

### Decision 1: Task Identifier Strategy

**Decision**: Use auto-incrementing integer identifiers starting from 1
**Rationale**: Simple, deterministic, human-readable. Avoids UUID complexity not needed for in-memory single-session use.
**Alternatives Rejected**:
- UUID: Overkill for Phase I, harder for users to type
- String slugs: Collision risk, requires uniqueness validation

### Decision 2: State Storage Structure

**Decision**: Use Python dict with integer keys for O(1) lookup
**Rationale**: Fast lookups by ID, ordered iteration (Python 3.7+ dicts maintain insertion order)
**Alternatives Rejected**:
- List with linear search: O(n) lookup unacceptable
- External storage: Prohibited in Phase I

### Decision 3: Command Parser Implementation

**Decision**: Use argparse from Python standard library
**Rationale**: Built-in, well-tested, supports subcommands and help generation
**Alternatives Rejected**:
- Custom parser: Reinventing the wheel
- click/typer: External dependencies prohibited

### Decision 4: Timestamp Handling

**Decision**: Use datetime.datetime.now() at task creation
**Rationale**: Standard library, sufficient precision for Phase I
**Alternatives Rejected**:
- UTC only: Adds complexity not needed for local-only app
- Custom format: datetime is sufficient

### Decision 5: Error Handling Strategy

**Decision**: Custom exception hierarchy with formatted error output
**Rationale**: Enables testable error conditions, consistent error format
**Alternatives Rejected**:
- Generic exceptions: Lose specificity
- Error codes: Less Pythonic

## Agent Execution Flow

### SpecExecutionAgent

Acts as the governance layer validating all operations:

1. Before any implementation task:
   - Verify task exists in spec.md
   - Confirm no Phase II+ features requested
   - Check Context7 MCP for blocking conditions

2. During implementation:
   - Validate generated code matches specification
   - Reject code introducing prohibited patterns
   - Enforce test-first workflow

3. After task completion:
   - Verify acceptance criteria met
   - Update Context7 MCP with outcome
   - Gate approval for next task

### StateManagementAgent

Owns the TaskList and all state transitions:

1. Initialization:
   - Create empty TaskList on application start
   - Set ID counter to 1

2. State Operations:
   - `add_task(task)` -> Assigns ID, stores task, returns task
   - `get_task(id)` -> Returns task or raises NotFoundError
   - `get_all_tasks()` -> Returns list of all tasks
   - `update_task(id, changes)` -> Applies changes, returns updated task
   - `delete_task(id)` -> Removes task, returns confirmation
   - `task_exists(id)` -> Returns boolean

3. Invariants Enforced:
   - No duplicate IDs
   - No external state access
   - All mutations logged

### ConversationToTodoAgent (Phase I Mode)

Operates in structured command mode:

1. Parse CLI input using argparse
2. Validate command syntax
3. Route to appropriate skill
4. Format and return output

## Skill Implementation Mapping

| Skill | Implementation | Module |
|-------|----------------|--------|
| TaskManagementSkill | TaskService class | `src/services/task_service.py` |
| TaskQuerySkill | QueryService class | `src/services/query_service.py` |
| ValidationSkill | validation functions | `src/services/validation.py` |

## Implementation Phases

### Phase 0: Research (Complete)
See `research.md` for technology decisions.

### Phase 1: Design (Complete)
- Data model defined in `data-model.md`
- CLI contracts defined in `contracts/cli-contract.md`
- Quickstart guide in `quickstart.md`

### Phase 2: Tasks (Next Step)
Run `/sp.tasks` to generate implementation tasks based on this plan.

## Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| argparse limitations | Low | Low | Well-established library, fallback to manual parsing |
| Test coverage gaps | Medium | Medium | Enforce 80% minimum, review coverage reports |
| Scope creep | Medium | High | SpecExecutionAgent blocks non-spec features |

## Success Criteria Mapping

| Criterion | Verification Method |
|-----------|---------------------|
| SC-001: All user stories pass | Run acceptance test suite |
| SC-002: All 25 FRs implemented | Trace tests to requirements |
| SC-003: Edge cases handled | Edge case test suite |
| SC-004: 80%+ coverage | pytest-cov report |
| SC-005: No external deps | Check requirements.txt is empty or absent |
| SC-006: <100ms operations | Timing assertions in tests |
| SC-007: No manual edits | Git history shows Claude Code commits only |
| SC-008: Context7 MCP complete | Audit PHR records |

## Next Steps

1. Run `/sp.tasks` to generate implementation task list
2. Execute tasks following Red-Green-Refactor cycle
3. Validate against success criteria
4. Gate approval for Phase I completion
