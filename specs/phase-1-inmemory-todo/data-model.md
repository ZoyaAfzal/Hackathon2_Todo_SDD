# Data Model: Phase I - In-Memory Todo Console Application

**Feature**: phase-1-inmemory-todo
**Date**: 2026-01-02
**Status**: Complete

## Overview

This document defines the data model for Phase I of the Evolution of Todo project. All entities are stored in-memory only and do not persist between application runs.

## Entities

### Task

The Task entity represents a single unit of work to be tracked.

#### Attributes

| Attribute | Type | Required | Mutable | Default | Description |
|-----------|------|----------|---------|---------|-------------|
| id | int | Yes | No | Auto-generated | Unique identifier, auto-incremented from 1 |
| title | str | Yes | Yes | N/A | Human-readable task name, non-empty |
| description | str | No | Yes | "" | Extended task details, may be empty |
| completed | bool | Yes | Yes | False | Completion status |
| created_at | datetime | Yes | No | Now | Creation timestamp, immutable |

#### Invariants

1. `id` MUST be a positive integer
2. `id` MUST be unique across all tasks in the system
3. `id` MUST NOT change after task creation
4. `title` MUST NOT be empty or contain only whitespace
5. `title` MUST be a non-empty string after stripping whitespace
6. `description` MAY be empty string but MUST NOT be None
7. `completed` MUST be exactly True or False
8. `created_at` MUST NOT change after task creation
9. `created_at` MUST be a valid datetime object

#### State Transitions

```
[Created] -> Task(id=N, title="X", description="", completed=False, created_at=now)
     |
     v
[Updated Title] -> Task.title = "Y" (title validation applies)
     |
     v
[Updated Description] -> Task.description = "Z"
     |
     v
[Marked Complete] -> Task.completed = True
     |
     v
[Unmarked] -> Task.completed = False
     |
     v
[Deleted] -> Task removed from TaskList
```

#### Validation Rules

| Rule ID | Attribute | Condition | Error |
|---------|-----------|-----------|-------|
| VR-001 | title | Empty string | EmptyTitleError: "Title cannot be empty" |
| VR-002 | title | Whitespace only | EmptyTitleError: "Title cannot be empty" |
| VR-003 | id | Not positive int | InvalidIdError: "Invalid task ID" |
| VR-004 | id | Not found | TaskNotFoundError: "Task not found: {id}" |

### TaskList

The TaskList entity represents the complete collection of tasks in the system.

#### Attributes

| Attribute | Type | Required | Mutable | Default | Description |
|-----------|------|----------|---------|---------|-------------|
| tasks | Dict[int, Task] | Yes | Yes | {} | Collection of tasks keyed by ID |
| next_id | int | Yes | Yes | 1 | Counter for next task ID |

#### Invariants

1. `tasks` keys MUST match the `id` attribute of their corresponding Task
2. `tasks` MUST NOT contain duplicate IDs
3. `next_id` MUST be greater than all existing task IDs
4. `tasks` MUST be empty on application start
5. `tasks` MUST NOT persist between application runs

#### Operations

| Operation | Input | Output | Side Effects |
|-----------|-------|--------|--------------|
| add_task | title, description? | Task | Increments next_id, adds to tasks |
| get_task | id | Task | None (read-only) |
| get_all_tasks | None | List[Task] | None (read-only) |
| update_task | id, title?, description? | Task | Modifies task in place |
| delete_task | id | bool | Removes task from tasks |
| complete_task | id | Task | Sets task.completed = True |
| uncomplete_task | id | Task | Sets task.completed = False |
| task_exists | id | bool | None (read-only) |

## Relationships

```
┌─────────────┐         ┌──────────┐
│  TaskList   │ 1 ──── * │   Task   │
└─────────────┘         └──────────┘
     │
     │ owns
     │
     ▼
┌─────────────────────┐
│ StateManagementAgent│
└─────────────────────┘
```

- TaskList contains zero or more Tasks
- StateManagementAgent exclusively owns TaskList
- No other component may directly access TaskList

## Data Flow

### Create Task Flow

```
User Input: add "Buy groceries" "Milk, eggs"
     │
     ▼
┌─────────────────────┐
│ ConversationToTodo  │  Parse command
│      Agent          │
└─────────────────────┘
     │
     ▼
┌─────────────────────┐
│  ValidationSkill    │  Validate title not empty
└─────────────────────┘
     │
     ▼
┌─────────────────────┐
│TaskManagementSkill  │  Create Task object
└─────────────────────┘
     │
     ▼
┌─────────────────────┐
│StateManagementAgent │  Assign ID, store Task
└─────────────────────┘
     │
     ▼
Output: [OK] Task 1 created: "Buy groceries"
```

### Query Tasks Flow

```
User Input: list
     │
     ▼
┌─────────────────────┐
│ ConversationToTodo  │  Parse command
│      Agent          │
└─────────────────────┘
     │
     ▼
┌─────────────────────┐
│   TaskQuerySkill    │  Request all tasks
└─────────────────────┘
     │
     ▼
┌─────────────────────┐
│StateManagementAgent │  Return tasks list
└─────────────────────┘
     │
     ▼
Output: Task list formatted display
```

### Update Task Flow

```
User Input: update 1 --title "Buy organic groceries"
     │
     ▼
┌─────────────────────┐
│ ConversationToTodo  │  Parse command
│      Agent          │
└─────────────────────┘
     │
     ▼
┌─────────────────────┐
│  ValidationSkill    │  Validate ID exists, title not empty
└─────────────────────┘
     │
     ▼
┌─────────────────────┐
│TaskManagementSkill  │  Request update
└─────────────────────┘
     │
     ▼
┌─────────────────────┐
│StateManagementAgent │  Apply update, return Task
└─────────────────────┘
     │
     ▼
Output: [OK] Task 1 updated
```

## Python Implementation Reference

### Task Dataclass

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Task:
    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not self.title or not self.title.strip():
            raise EmptyTitleError("Title cannot be empty")
        self.title = self.title.strip()
        if self.description:
            self.description = self.description.strip()
```

### TaskList Type

```python
from typing import Dict

TaskList = Dict[int, Task]
```

## Serialization (Future Phases)

Phase I does not require serialization. For future reference:

| Phase | Serialization Format |
|-------|---------------------|
| Phase I | None (in-memory only) |
| Phase II | JSON file or SQLite |
| Phase III | Same as Phase II |
| Phase IV | Container volume or external DB |
| Phase V | Cloud-native persistence |

## Constraints Summary

1. **No Persistence**: All data lost on application exit
2. **No Concurrency**: Single-threaded access only
3. **No External State**: No files, databases, or network
4. **Explicit State**: All state in TaskList, owned by StateManagementAgent
5. **Immutable IDs**: Task ID never changes after creation
6. **Immutable Timestamps**: created_at never changes after creation
