# Quickstart Guide: Phase I - In-Memory Todo Console Application

**Feature**: phase-1-inmemory-todo
**Date**: 2026-01-02
**Status**: Complete

## Prerequisites

- Python 3.11 or higher installed
- Terminal/command prompt access
- No additional packages required (Python standard library only)

## Installation

### 1. Verify Python Version

```bash
python --version
# Expected: Python 3.11.x or higher
```

### 2. Clone/Navigate to Project

```bash
cd /path/to/project
```

### 3. Verify Project Structure

```bash
ls src/
# Expected: __init__.py main.py models/ services/ state/ cli/
```

## Running the Application

### Interactive Mode (Recommended)

```bash
python -m src.main --interactive
```

This starts an interactive session where you can enter commands one at a time.

### Single Command Mode

```bash
python -m src.main add "Buy groceries"
```

This executes a single command and exits.

## Basic Usage

### Create a Task

```bash
todo> add "Buy groceries"
[OK] Task 1 created: "Buy groceries"
```

With description:
```bash
todo> add "Buy groceries" "Milk, eggs, bread"
[OK] Task 2 created: "Buy groceries"
```

### View All Tasks

```bash
todo> list
Tasks:
[1] [ ] Buy groceries
        Created: 2026-01-02 10:30:00

[2] [ ] Buy groceries
        Milk, eggs, bread
        Created: 2026-01-02 10:31:00
```

### View Single Task

```bash
todo> view 1
Task 1:
  Title: Buy groceries
  Description:
  Status: Incomplete
  Created: 2026-01-02 10:30:00
```

### Mark Task Complete

```bash
todo> complete 1
[OK] Task 1 marked as complete
```

### Mark Task Incomplete

```bash
todo> uncomplete 1
[OK] Task 1 marked as incomplete
```

### Update Task

Update title:
```bash
todo> update 1 --title "Buy organic groceries"
[OK] Task 1 updated
```

Update description:
```bash
todo> update 1 --description "From local farmer's market"
[OK] Task 1 updated
```

Update both:
```bash
todo> update 1 --title "New Title" --description "New description"
[OK] Task 1 updated
```

### Delete Task

```bash
todo> delete 1
[OK] Task 1 deleted
```

### Get Help

```bash
todo> help
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

### Exit Application

```bash
todo> exit
Goodbye!
```

## Example Session

```bash
$ python -m src.main --interactive
Todo Application - Phase I
Type 'help' for available commands.

todo> add "Complete project proposal"
[OK] Task 1 created: "Complete project proposal"

todo> add "Review meeting notes" "From Monday's standup"
[OK] Task 2 created: "Review meeting notes"

todo> list
Tasks:
[1] [ ] Complete project proposal
        Created: 2026-01-02 10:30:00

[2] [ ] Review meeting notes
        From Monday's standup
        Created: 2026-01-02 10:30:15

todo> complete 2
[OK] Task 2 marked as complete

todo> list
Tasks:
[1] [ ] Complete project proposal
        Created: 2026-01-02 10:30:00

[2] [x] Review meeting notes
        From Monday's standup
        Created: 2026-01-02 10:30:15

todo> update 1 --description "Due by end of week"
[OK] Task 1 updated

todo> view 1
Task 1:
  Title: Complete project proposal
  Description: Due by end of week
  Status: Incomplete
  Created: 2026-01-02 10:30:00

todo> delete 2
[OK] Task 2 deleted

todo> list
Tasks:
[1] [ ] Complete project proposal
        Due by end of week
        Created: 2026-01-02 10:30:00

todo> exit
Goodbye!
```

## Running Tests

### Run All Tests

```bash
python -m pytest tests/ -v
```

### Run with Coverage

```bash
python -m pytest tests/ --cov=src --cov-report=term-missing
```

### Run Specific Test Category

```bash
# Unit tests
python -m pytest tests/unit/ -v

# Integration tests
python -m pytest tests/integration/ -v

# Contract tests
python -m pytest tests/contract/ -v
```

## Troubleshooting

### "Command not found" or "Unknown command"

Ensure you're using the correct command syntax. Run `help` to see available commands.

### "Task not found" Error

The task ID you specified doesn't exist. Run `list` to see available task IDs.

### "Title cannot be empty" Error

You must provide a non-empty title when creating or updating tasks.

### Python Version Error

Ensure you're running Python 3.11 or higher:
```bash
python --version
```

### Module Not Found

Ensure you're running from the project root directory:
```bash
python -m src.main --interactive
```

## Phase I Limitations

Remember that in Phase I:

1. **No Persistence**: All tasks are lost when you exit the application
2. **No Filtering**: You can only view all tasks, not filter by status
3. **No Priorities**: Tasks have no priority or due date attributes
4. **No Search**: You cannot search tasks by text
5. **Single User**: The application is single-user only

These features will be added in later phases.

## Next Steps

After completing Phase I:

1. **Phase II**: Adds persistent storage (file or database)
2. **Phase III**: Adds natural language interface
3. **Phase IV**: Adds Docker containerization
4. **Phase V**: Adds cloud-native Kubernetes deployment

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify your Python version
3. Review the specification at `specs/phase-1-inmemory-todo/spec.md`
4. Check the CLI contract at `specs/phase-1-inmemory-todo/contracts/cli-contract.md`
