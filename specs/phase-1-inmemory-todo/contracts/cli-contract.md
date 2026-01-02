# CLI Contract: Phase I - In-Memory Todo Console Application

**Feature**: phase-1-inmemory-todo
**Date**: 2026-01-02
**Status**: Complete

## Overview

This document defines the command-line interface contract for Phase I. All commands follow a structured syntax with deterministic behavior.

## Command Syntax

All commands follow the pattern:
```
todo <command> [arguments] [options]
```

The application entry point is invoked as:
```
python -m src.main
```

Or in interactive mode:
```
python -m src.main --interactive
```

## Commands

### add

Creates a new task.

**Syntax**:
```
add <title> [description]
```

**Arguments**:

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| title | string | Yes | Task title (quote if contains spaces) |
| description | string | No | Task description (quote if contains spaces) |

**Success Output**:
```
[OK] Task {id} created: "{title}"
```

**Error Outputs**:
```
[ERROR] Title cannot be empty
```

**Examples**:
```
$ todo add "Buy groceries"
[OK] Task 1 created: "Buy groceries"

$ todo add "Buy groceries" "Milk, eggs, bread"
[OK] Task 2 created: "Buy groceries"

$ todo add ""
[ERROR] Title cannot be empty
```

**Acceptance Contract**:
- Input: Non-empty title string
- Output: New task with auto-generated ID
- Side Effect: Task added to TaskList
- Error: EmptyTitleError if title empty/whitespace

---

### list

Displays all tasks.

**Syntax**:
```
list
```

**Arguments**: None

**Success Output (with tasks)**:
```
Tasks:
[1] [ ] Buy groceries
        Milk, eggs, bread
        Created: 2026-01-02 10:30:00

[2] [x] Call dentist
        Created: 2026-01-02 10:31:00
```

**Success Output (empty)**:
```
No tasks found.
```

**Examples**:
```
$ todo list
Tasks:
[1] [ ] Buy groceries
        Created: 2026-01-02 10:30:00

$ todo list
No tasks found.
```

**Acceptance Contract**:
- Input: None
- Output: Formatted list of all tasks or empty message
- Side Effect: None (read-only)
- Status Indicator: `[ ]` incomplete, `[x]` complete

---

### view

Displays a single task by ID.

**Syntax**:
```
view <id>
```

**Arguments**:

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| id | integer | Yes | Task identifier |

**Success Output**:
```
Task {id}:
  Title: {title}
  Description: {description}
  Status: {Complete|Incomplete}
  Created: {timestamp}
```

**Error Outputs**:
```
[ERROR] Task not found: {id}
[ERROR] Invalid task ID: {id}
```

**Examples**:
```
$ todo view 1
Task 1:
  Title: Buy groceries
  Description: Milk, eggs, bread
  Status: Incomplete
  Created: 2026-01-02 10:30:00

$ todo view 999
[ERROR] Task not found: 999

$ todo view abc
[ERROR] Invalid task ID: abc
```

**Acceptance Contract**:
- Input: Valid task ID
- Output: Detailed task information
- Side Effect: None (read-only)
- Error: TaskNotFoundError if ID not found
- Error: InvalidIdError if ID not valid integer

---

### complete

Marks a task as complete.

**Syntax**:
```
complete <id>
```

**Arguments**:

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| id | integer | Yes | Task identifier |

**Success Output**:
```
[OK] Task {id} marked as complete
```

**Error Outputs**:
```
[ERROR] Task not found: {id}
[ERROR] Invalid task ID: {id}
```

**Examples**:
```
$ todo complete 1
[OK] Task 1 marked as complete

$ todo complete 999
[ERROR] Task not found: 999
```

**Acceptance Contract**:
- Input: Valid task ID
- Output: Confirmation message
- Side Effect: Task.completed = True
- Idempotent: Completing already-complete task succeeds silently
- Error: TaskNotFoundError if ID not found

---

### uncomplete

Marks a task as incomplete.

**Syntax**:
```
uncomplete <id>
```

**Arguments**:

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| id | integer | Yes | Task identifier |

**Success Output**:
```
[OK] Task {id} marked as incomplete
```

**Error Outputs**:
```
[ERROR] Task not found: {id}
[ERROR] Invalid task ID: {id}
```

**Examples**:
```
$ todo uncomplete 1
[OK] Task 1 marked as incomplete

$ todo uncomplete 999
[ERROR] Task not found: 999
```

**Acceptance Contract**:
- Input: Valid task ID
- Output: Confirmation message
- Side Effect: Task.completed = False
- Idempotent: Uncompleting already-incomplete task succeeds silently
- Error: TaskNotFoundError if ID not found

---

### update

Updates task attributes.

**Syntax**:
```
update <id> [--title <new_title>] [--description <new_description>]
```

**Arguments**:

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| id | integer | Yes | Task identifier |

**Options**:

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| --title | string | No | New task title |
| --description | string | No | New task description |

**Success Output**:
```
[OK] Task {id} updated
```

**Error Outputs**:
```
[ERROR] Task not found: {id}
[ERROR] Invalid task ID: {id}
[ERROR] Title cannot be empty
[ERROR] No updates specified
```

**Examples**:
```
$ todo update 1 --title "Buy organic groceries"
[OK] Task 1 updated

$ todo update 1 --description "From farmer's market"
[OK] Task 1 updated

$ todo update 1 --title "New title" --description "New description"
[OK] Task 1 updated

$ todo update 1 --title ""
[ERROR] Title cannot be empty

$ todo update 999 --title "New"
[ERROR] Task not found: 999
```

**Acceptance Contract**:
- Input: Valid task ID and at least one update option
- Output: Confirmation message
- Side Effect: Task attributes updated
- Error: TaskNotFoundError if ID not found
- Error: EmptyTitleError if title update is empty
- Error: NoUpdatesError if no options provided

---

### delete

Removes a task.

**Syntax**:
```
delete <id>
```

**Arguments**:

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| id | integer | Yes | Task identifier |

**Success Output**:
```
[OK] Task {id} deleted
```

**Error Outputs**:
```
[ERROR] Task not found: {id}
[ERROR] Invalid task ID: {id}
```

**Examples**:
```
$ todo delete 1
[OK] Task 1 deleted

$ todo delete 999
[ERROR] Task not found: 999
```

**Acceptance Contract**:
- Input: Valid task ID
- Output: Confirmation message
- Side Effect: Task removed from TaskList
- Error: TaskNotFoundError if ID not found

---

### help

Displays available commands.

**Syntax**:
```
help
```

**Arguments**: None

**Success Output**:
```
Todo Application - Phase I

Commands:
  add <title> [description]       Create a new task
  list                            View all tasks
  view <id>                       View a single task
  complete <id>                   Mark task as complete
  uncomplete <id>                 Mark task as incomplete
  update <id> [options]           Update task attributes
    --title <text>                New title
    --description <text>          New description
  delete <id>                     Remove a task
  help                            Show this help message
  exit                            Exit the application
```

**Acceptance Contract**:
- Input: None
- Output: Help text
- Side Effect: None

---

### exit

Terminates the application.

**Syntax**:
```
exit
```

**Arguments**: None

**Success Output**:
```
Goodbye!
```

**Acceptance Contract**:
- Input: None
- Output: Farewell message
- Side Effect: Application terminates
- Note: All tasks are lost (no persistence in Phase I)

---

## Error Handling Contract

### Error Message Format

All errors follow the format:
```
[ERROR] <message>
```

### Error Types

| Error Type | Condition | Message Template |
|------------|-----------|------------------|
| EmptyTitleError | Title is empty/whitespace | "Title cannot be empty" |
| InvalidIdError | ID is not valid integer | "Invalid task ID: {id}" |
| TaskNotFoundError | ID doesn't exist | "Task not found: {id}" |
| NoUpdatesError | Update without options | "No updates specified" |
| UnknownCommandError | Invalid command | "Unknown command: {cmd}" |

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error occurred |

## Output Format Contract

### Task Display (List View)

```
[{id}] [{status}] {title}
        {description}
        Created: {timestamp}
```

Where:
- `{id}`: Integer task ID
- `{status}`: `[ ]` for incomplete, `[x]` for complete
- `{title}`: Task title
- `{description}`: Task description (indented, only if non-empty)
- `{timestamp}`: Format `YYYY-MM-DD HH:MM:SS`

### Task Display (Detail View)

```
Task {id}:
  Title: {title}
  Description: {description}
  Status: {Complete|Incomplete}
  Created: {timestamp}
```

### Success Message

```
[OK] {action description}
```

## Interactive Mode Contract

When started with `--interactive` flag:

1. Display prompt: `todo> `
2. Accept command input
3. Execute command
4. Display output
5. Return to step 1 until `exit` command

**Example Session**:
```
$ python -m src.main --interactive
Todo Application - Phase I
Type 'help' for available commands.

todo> add "Buy groceries"
[OK] Task 1 created: "Buy groceries"

todo> list
Tasks:
[1] [ ] Buy groceries
        Created: 2026-01-02 10:30:00

todo> complete 1
[OK] Task 1 marked as complete

todo> exit
Goodbye!
```

## Contract Test Cases

Each command must pass the following contract tests:

### add
- [ ] CT-ADD-001: Valid title creates task
- [ ] CT-ADD-002: Valid title and description creates task
- [ ] CT-ADD-003: Empty title returns error
- [ ] CT-ADD-004: Whitespace-only title returns error
- [ ] CT-ADD-005: Assigned ID is unique and sequential

### list
- [ ] CT-LIST-001: Empty list shows "No tasks found"
- [ ] CT-LIST-002: Tasks display with correct format
- [ ] CT-LIST-003: Completed tasks show [x]
- [ ] CT-LIST-004: Incomplete tasks show [ ]

### view
- [ ] CT-VIEW-001: Valid ID shows task details
- [ ] CT-VIEW-002: Invalid ID returns error
- [ ] CT-VIEW-003: Non-existent ID returns not found

### complete
- [ ] CT-COMP-001: Valid ID marks task complete
- [ ] CT-COMP-002: Already complete task stays complete
- [ ] CT-COMP-003: Non-existent ID returns error

### uncomplete
- [ ] CT-UNCOMP-001: Valid ID marks task incomplete
- [ ] CT-UNCOMP-002: Already incomplete task stays incomplete
- [ ] CT-UNCOMP-003: Non-existent ID returns error

### update
- [ ] CT-UPD-001: Valid title update succeeds
- [ ] CT-UPD-002: Valid description update succeeds
- [ ] CT-UPD-003: Empty title update returns error
- [ ] CT-UPD-004: Non-existent ID returns error
- [ ] CT-UPD-005: No options returns error

### delete
- [ ] CT-DEL-001: Valid ID deletes task
- [ ] CT-DEL-002: Non-existent ID returns error
- [ ] CT-DEL-003: Deleted task not in list

### help
- [ ] CT-HELP-001: Displays all commands

### exit
- [ ] CT-EXIT-001: Terminates application
