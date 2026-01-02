# Research: Phase I - In-Memory Todo Console Application

**Feature**: phase-1-inmemory-todo
**Date**: 2026-01-02
**Status**: Complete

## Overview

This document captures research findings and technology decisions for Phase I implementation. All unknowns from the Technical Context have been resolved.

## Research Tasks Completed

### 1. Python Version Selection

**Research Question**: Which Python version to target?

**Decision**: Python 3.11+

**Rationale**:
- Python 3.11 offers significant performance improvements (10-60% faster)
- Improved error messages for debugging
- `dataclasses` fully mature and stable
- Type hints well-supported
- Wide platform availability

**Alternatives Considered**:
- Python 3.10: Slightly older, fewer performance gains
- Python 3.12: Too new, may have compatibility issues
- Python 3.9: Missing some newer typing features

### 2. Data Structure for Task Storage

**Research Question**: What data structure for in-memory task storage?

**Decision**: Python dict with integer keys

**Rationale**:
- O(1) lookup by task ID
- O(1) insertion and deletion
- Maintains insertion order (Python 3.7+)
- Native to Python, no dependencies
- Simple iteration for list operations

**Alternatives Considered**:
- List with linear search: O(n) lookup unacceptable for future scaling
- OrderedDict: Unnecessary since dict maintains order in Python 3.7+
- Custom class: Over-engineering for Phase I needs

### 3. Task Model Implementation

**Research Question**: How to implement the Task entity?

**Decision**: Python `dataclass` with frozen=False

**Rationale**:
- Built-in to Python 3.7+
- Automatic `__init__`, `__repr__`, `__eq__`
- Type hints integrated
- Mutable for update operations
- Clean, declarative syntax

**Alternatives Considered**:
- NamedTuple: Immutable, would require recreation for updates
- Plain class: More boilerplate
- TypedDict: Less structure, no methods

### 4. Command Line Parser

**Research Question**: Which CLI parsing approach?

**Decision**: argparse with subcommands

**Rationale**:
- Part of Python standard library
- Supports subcommand pattern (add, list, complete, etc.)
- Auto-generates help text
- Built-in type conversion and validation
- Well-documented and stable

**Alternatives Considered**:
- click: External dependency (prohibited)
- typer: External dependency (prohibited)
- sys.argv manual parsing: Error-prone, reinventing the wheel
- cmd module: Interactive mode not needed for Phase I

### 5. Identifier Generation Strategy

**Research Question**: How to generate unique task identifiers?

**Decision**: Auto-incrementing integer starting from 1

**Rationale**:
- Simple and deterministic
- Human-readable and easy to type
- No collision risk in single-session
- Easy to track "next ID" counter
- Matches user mental model

**Alternatives Considered**:
- UUID: Overkill, hard to type manually
- Timestamp-based: Potential collisions in fast operations
- Hash-based: Unnecessary complexity

### 6. Timestamp Implementation

**Research Question**: How to handle creation timestamps?

**Decision**: `datetime.datetime.now()` returning local time

**Rationale**:
- Standard library, no dependencies
- Sufficient precision (microseconds)
- Local time appropriate for single-user console app
- Easy formatting for display

**Alternatives Considered**:
- UTC with timezone: Adds complexity not needed in Phase I
- Unix timestamp: Less human-readable
- Custom format string: datetime object more flexible

### 7. Error Handling Approach

**Research Question**: How to structure error handling?

**Decision**: Custom exception hierarchy with specific exception types

**Rationale**:
- Testable error conditions
- Specific exception types for different failures
- Consistent error message formatting
- Pythonic approach

**Exception Hierarchy**:
```
TodoError (base)
├── TaskNotFoundError
├── ValidationError
│   ├── EmptyTitleError
│   └── InvalidIdError
└── DuplicateTaskError (future-proofing)
```

**Alternatives Considered**:
- Generic ValueError/KeyError: Lose specificity
- Error codes: Less Pythonic
- Result types: Over-engineering for Phase I

### 8. Output Formatting

**Research Question**: How to format CLI output?

**Decision**: String formatting with consistent prefix patterns

**Rationale**:
- Matches specification output format (`[OK]`, `[ERROR]`)
- Easy to parse programmatically
- Human-readable
- Testable via string matching

**Format Patterns**:
- Success: `[OK] <message>`
- Error: `[ERROR] <message>`
- Task display: `[id] [status] title`

**Alternatives Considered**:
- JSON output: Not human-friendly for console
- Rich/colored output: External dependency
- No prefix: Harder to distinguish success/error

### 9. Testing Framework

**Research Question**: Which testing framework to use?

**Decision**: pytest (primary) with unittest fallback

**Rationale**:
- pytest is more Pythonic and readable
- Excellent fixture system
- Good coverage reporting with pytest-cov
- unittest available if pytest unavailable

**Test Categories**:
- Unit tests: Individual functions and methods
- Integration tests: CLI command flows
- Contract tests: Command syntax verification

**Alternatives Considered**:
- unittest only: More verbose, less readable
- nose: Deprecated
- doctest: Limited for complex scenarios

### 10. Project Structure

**Research Question**: How to organize the codebase?

**Decision**: Standard Python package structure with separation of concerns

**Rationale**:
- Clear module boundaries
- Testable components
- Follows Python packaging conventions
- Supports future evolution

**Structure**:
```
src/
├── models/      # Domain entities (Task)
├── services/    # Business logic (skills)
├── state/       # State management
└── cli/         # Command interface
```

**Alternatives Considered**:
- Flat structure: Doesn't scale for later phases
- Feature-based: Overkill for Phase I
- Single file: Unmaintainable

## Resolved Unknowns

| Item | Resolution |
|------|------------|
| Python version | 3.11+ |
| Storage structure | dict with int keys |
| Model implementation | dataclass |
| CLI parser | argparse |
| ID generation | Auto-increment from 1 |
| Timestamps | datetime.now() |
| Error handling | Custom exception hierarchy |
| Output format | Prefix patterns [OK]/[ERROR] |
| Testing | pytest with coverage |
| Project structure | src/ with models/services/state/cli |

## Best Practices Identified

### Python Dataclasses
- Use `field(default_factory=...)` for mutable defaults
- Implement `__post_init__` for validation
- Use `frozen=False` when updates needed

### argparse Subcommands
- Define each command as a subparser
- Use `set_defaults(func=handler)` for routing
- Provide clear help text for each option

### pytest Fixtures
- Use `@pytest.fixture` for reusable test setup
- Scope fixtures appropriately (function, module, session)
- Use `conftest.py` for shared fixtures

### Type Hints
- Use `Optional[T]` for nullable types
- Use `List[T]` / `Dict[K,V]` for collections
- Return types on all functions

## Context7 MCP Sync

This research has been completed and documented. Key decisions:

1. **Language**: Python 3.11+ selected
2. **Storage**: In-memory dict with integer keys
3. **Models**: Dataclass-based Task entity
4. **CLI**: argparse with subcommands
5. **Testing**: pytest with 80% coverage target

All decisions align with Constitution principles and Phase I constraints.
