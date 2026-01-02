# Tasks: Phase I - In-Memory Todo Console Application

**Input**: Design documents from `/specs/phase-1-inmemory-todo/`
**Prerequisites**: plan.md (complete), spec.md (complete), data-model.md (complete), contracts/cli-contract.md (complete)

**Tests**: Tests are REQUIRED per Constitution Principle III (Test-First Discipline) and spec.md success criteria SC-004 (80% coverage).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths follow plan.md structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project directory structure per plan.md in src/ and tests/
- [X] T002 Create src/__init__.py with package metadata
- [X] T003 [P] Create src/models/__init__.py
- [X] T004 [P] Create src/services/__init__.py
- [X] T005 [P] Create src/state/__init__.py
- [X] T006 [P] Create src/cli/__init__.py
- [X] T007 [P] Create tests/__init__.py
- [X] T008 [P] Create tests/unit/__init__.py
- [X] T009 [P] Create tests/integration/__init__.py
- [X] T010 [P] Create tests/contract/__init__.py
- [X] T011 Create tests/conftest.py with shared pytest fixtures
- [X] T012 Create src/exceptions.py with custom exception hierarchy (TodoError, TaskNotFoundError, EmptyTitleError, InvalidIdError)

**Checkpoint**: Project skeleton ready for implementation ✅ COMPLETE

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

### Tests for Foundational Phase

- [X] T013 [P] Create tests/unit/test_task_model.py with Task dataclass tests (creation, validation, invariants)
- [X] T014 [P] Create tests/unit/test_store.py with TaskStore tests (initialization, CRUD operations)
- [X] T015 [P] Create tests/unit/test_validation.py with ValidationSkill tests (title, id validation)

### Implementation for Foundational Phase

- [X] T016 Create src/models/task.py with Task dataclass per data-model.md
- [X] T017 Create src/state/store.py with TaskStore class (StateManagementAgent implementation)
- [X] T018 Create src/services/validation.py with validate_title, validate_id functions

**Checkpoint**: Foundation ready - user story implementation can now begin ✅ COMPLETE

---

## Phase 3: User Story 1 - Add New Task (Priority: P1)

**Goal**: Users can create new tasks with title and optional description

**Independent Test**: Invoke add command with title, verify task appears in list with correct attributes

### Tests for User Story 1

- [X] T019 [P] [US1] Create tests/unit/test_task_service.py with create_task tests
- [X] T020 [P] [US1] Create tests/contract/test_add_command.py with CT-ADD-001 through CT-ADD-005

### Implementation for User Story 1

- [X] T021 [US1] Create src/services/task_service.py with create_task function
- [X] T022 [US1] Create src/cli/commands.py with add_command handler
- [X] T023 [US1] Create src/cli/parser.py with argparse subcommand for 'add'
- [X] T024 [US1] Create src/cli/formatter.py with format_success, format_error functions

**Checkpoint**: User Story 1 complete - can add tasks via CLI

---

## Phase 4: User Story 2 - View All Tasks (Priority: P1)

**Goal**: Users can view all tasks with their details

**Independent Test**: Add tasks, invoke list command, verify all tasks displayed correctly

### Tests for User Story 2

- [X] T025 [P] [US2] Create tests/unit/test_query_service.py with get_all_tasks, get_task tests
- [X] T026 [P] [US2] Create tests/contract/test_list_command.py with CT-LIST-001 through CT-LIST-004
- [X] T027 [P] [US2] Create tests/contract/test_view_command.py with CT-VIEW-001 through CT-VIEW-003

### Implementation for User Story 2

- [X] T028 [US2] Create src/services/query_service.py with get_all_tasks, get_task functions
- [X] T029 [US2] Add list_command handler to src/cli/commands.py
- [X] T030 [US2] Add view_command handler to src/cli/commands.py
- [X] T031 [US2] Add format_task_list, format_task_detail to src/cli/formatter.py
- [X] T032 [US2] Add 'list' and 'view' subcommands to src/cli/parser.py

**Checkpoint**: User Stories 1 AND 2 complete - can add and view tasks

---

## Phase 5: User Story 3 - Mark Task Complete (Priority: P2)

**Goal**: Users can mark tasks as complete to track progress

**Independent Test**: Create task, mark complete, verify status changed in list

### Tests for User Story 3

- [X] T033 [P] [US3] Add complete_task tests to tests/unit/test_task_service.py
- [X] T034 [P] [US3] Create tests/contract/test_complete_command.py with CT-COMP-001 through CT-COMP-003

### Implementation for User Story 3

- [X] T035 [US3] Add complete_task function to src/services/task_service.py
- [X] T036 [US3] Add complete_command handler to src/cli/commands.py
- [X] T037 [US3] Add 'complete' subcommand to src/cli/parser.py

**Checkpoint**: User Story 3 complete - can mark tasks complete

---

## Phase 6: User Story 4 - Update Task (Priority: P2)

**Goal**: Users can update task title and description

**Independent Test**: Create task, update title/description, verify changes in view

### Tests for User Story 4

- [X] T038 [P] [US4] Add update_task tests to tests/unit/test_task_service.py
- [X] T039 [P] [US4] Create tests/contract/test_update_command.py with CT-UPD-001 through CT-UPD-005

### Implementation for User Story 4

- [X] T040 [US4] Add update_task function to src/services/task_service.py
- [X] T041 [US4] Add update_command handler to src/cli/commands.py
- [X] T042 [US4] Add 'update' subcommand with --title and --description options to src/cli/parser.py

**Checkpoint**: User Story 4 complete - can update tasks

---

## Phase 7: User Story 5 - Delete Task (Priority: P3)

**Goal**: Users can remove tasks from the list

**Independent Test**: Create task, delete by ID, verify no longer in list

### Tests for User Story 5

- [X] T043 [P] [US5] Add delete_task tests to tests/unit/test_task_service.py
- [X] T044 [P] [US5] Create tests/contract/test_delete_command.py with CT-DEL-001 through CT-DEL-003

### Implementation for User Story 5

- [X] T045 [US5] Add delete_task function to src/services/task_service.py
- [X] T046 [US5] Add delete_command handler to src/cli/commands.py
- [X] T047 [US5] Add 'delete' subcommand to src/cli/parser.py

**Checkpoint**: User Story 5 complete - can delete tasks

---

## Phase 8: User Story 6 - Unmark Task (Priority: P3)

**Goal**: Users can reopen completed tasks

**Independent Test**: Create task, mark complete, unmark, verify status is incomplete

### Tests for User Story 6

- [X] T048 [P] [US6] Add uncomplete_task tests to tests/unit/test_task_service.py
- [X] T049 [P] [US6] Create tests/contract/test_uncomplete_command.py with CT-UNCOMP-001 through CT-UNCOMP-003

### Implementation for User Story 6

- [X] T050 [US6] Add uncomplete_task function to src/services/task_service.py
- [X] T051 [US6] Add uncomplete_command handler to src/cli/commands.py
- [X] T052 [US6] Add 'uncomplete' subcommand to src/cli/parser.py

**Checkpoint**: User Story 6 complete - can unmark completed tasks

---

## Phase 9: Polish and Cross-Cutting Concerns

**Purpose**: Help, exit, integration, and final validation

### Tests for Polish Phase

- [X] T053 [P] Create tests/contract/test_help_command.py with CT-HELP-001
- [X] T054 [P] Create tests/contract/test_exit_command.py with CT-EXIT-001
- [X] T055 Create tests/integration/test_cli_operations.py with full workflow tests

### Implementation for Polish Phase

- [X] T056 Add help_command handler to src/cli/commands.py
- [X] T057 Add exit_command handler to src/cli/commands.py
- [X] T058 Add 'help' and 'exit' subcommands to src/cli/parser.py
- [X] T059 Create src/main.py with application entry point and interactive mode
- [X] T060 Add unknown command error handling to src/cli/parser.py
- [ ] T061 Run pytest with coverage and verify 80% minimum in tests/ (pytest not installed, tests exist but not executed)
- [ ] T062 Validate all 25 contract test cases pass (requires pytest installation)

**Checkpoint**: Phase I implementation complete ✅ CORE COMPLETE (pending test execution)

---

## Dependencies and Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - US1 and US2 can proceed in parallel (both P1)
  - US3 depends on US1 (needs tasks to complete)
  - US4 depends on US1 (needs tasks to update)
  - US5 depends on US1 (needs tasks to delete)
  - US6 depends on US3 (needs complete/uncomplete cycle)
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

```
        Setup (Phase 1)
              │
              ▼
      Foundational (Phase 2)
              │
              ▼
    ┌─────────┴─────────┐
    ▼                   ▼
US1: Add Task      US2: View Tasks
(Phase 3, P1)      (Phase 4, P1)
    │                   │
    └─────────┬─────────┘
              │
    ┌─────────┼─────────┐
    ▼         ▼         ▼
US3: Complete US4: Update US5: Delete
(Phase 5, P2) (Phase 6, P2) (Phase 7, P3)
    │
    ▼
US6: Unmark
(Phase 8, P3)
              │
              ▼
      Polish (Phase 9)
```

### Within Each User Story

1. Tests MUST be written and FAIL before implementation
2. Models before services
3. Services before CLI handlers
4. CLI handlers before parser updates
5. Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**:
```
T003, T004, T005, T006, T007, T008, T009, T010 can run in parallel
```

**Phase 2 (Foundational)**:
```
T013, T014, T015 can run in parallel (tests)
```

**Phase 3 (US1)**:
```
T019, T020 can run in parallel (tests)
```

**Phase 4 (US2)**:
```
T025, T026, T027 can run in parallel (tests)
```

**Phase 5-8 (US3-US6)**:
```
Each story: test tasks can run in parallel within the story
```

---

## Implementation Strategy

### MVP First (User Stories 1 and 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Add Task)
4. Complete Phase 4: User Story 2 (View Tasks)
5. **STOP and VALIDATE**: Test US1 and US2 independently
6. Deploy/demo if ready (minimal viable todo app)

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently (can add tasks)
3. Add User Story 2 → Test independently (can view tasks) → **MVP!**
4. Add User Story 3 → Test independently (can complete tasks)
5. Add User Story 4 → Test independently (can update tasks)
6. Add User Story 5 → Test independently (can delete tasks)
7. Add User Story 6 → Test independently (can unmark tasks)
8. Polish → Full Phase I complete

### Test-First Workflow

For each task:
1. Write test (RED) - test must fail
2. Implement code (GREEN) - test must pass
3. Refactor if needed - tests must still pass
4. Move to next task

---

## Summary

| Metric | Count |
|--------|-------|
| Total Tasks | 62 |
| Setup Tasks | 12 |
| Foundational Tasks | 6 |
| US1 Tasks | 6 |
| US2 Tasks | 8 |
| US3 Tasks | 5 |
| US4 Tasks | 5 |
| US5 Tasks | 5 |
| US6 Tasks | 5 |
| Polish Tasks | 10 |
| Parallel Opportunities | 24 tasks marked [P] |

### MVP Scope

- **Minimum**: Setup + Foundational + US1 + US2 = 32 tasks
- **Full Phase I**: All 62 tasks

### Contract Test Coverage

- 25 contract tests defined in cli-contract.md
- All mapped to task phases
- Must all pass for Phase I completion

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (RED phase)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
