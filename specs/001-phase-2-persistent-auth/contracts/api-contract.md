# API Contract: Phase II - Task Management API

**Date**: 2026-01-07
**Branch**: `001-phase-2-persistent-auth`
**Spec**: [../spec.md](../spec.md)
**Data Model**: [../data-model.md](../data-model.md)

---

## Overview

This contract defines the REST API endpoints for task management in Phase II. All `/api/*` endpoints require valid JWT authentication (FR-015).

**Base URL**: `/api/v1`

---

## Authentication

All task endpoints require a valid JWT token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

The `user_id` is extracted exclusively from the JWT payload (FR-022). Any user_id parameters in URLs are ignored.

---

## Endpoints

### 1. List Tasks

**Endpoint**: `GET /api/v1/tasks`

**Description**: Retrieve all tasks for the authenticated user with cursor-based pagination.

**Request**:
```http
GET /api/v1/tasks?limit=20&after_id=uuid HTTP/1.1
Authorization: Bearer <token>
```

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | integer | No | 20 | Number of tasks to return (max 100) |
| `after_id` | UUID | No | null | Cursor for pagination (last task ID from previous page) |

**Response**: `200 OK`
```json
{
  "tasks": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "created_at": "2026-01-07T10:00:00Z",
      "updated_at": "2026-01-07T10:00:00Z",
      "version": 1
    }
  ],
  "has_more": true,
  "next_cursor": "123e4567-e89b-12d3-a456-426614174001"
}
```

**Errors**:
| Status | Code | Description |
|--------|------|-------------|
| 401 | `unauthorized` | Missing or invalid JWT token |
| 400 | `invalid_cursor` | Invalid after_id format |

---

### 2. Get Task by ID

**Endpoint**: `GET /api/v1/tasks/{task_id}`

**Description**: Retrieve a specific task by ID. Returns 404 if task doesn't exist or belongs to another user (FR-013).

**Request**:
```http
GET /api/v1/tasks/123e4567-e89b-12d3-a456-426614174000 HTTP/1.1
Authorization: Bearer <token>
```

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | UUID | Yes | The task's unique identifier |

**Response**: `200 OK`
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2026-01-07T10:00:00Z",
  "updated_at": "2026-01-07T10:00:00Z",
  "version": 1
}
```

**Errors**:
| Status | Code | Description |
|--------|------|-------------|
| 401 | `unauthorized` | Missing or invalid JWT token |
| 404 | `not_found` | Task not found or belongs to another user |

---

### 3. Create Task

**Endpoint**: `POST /api/v1/tasks`

**Description**: Create a new task for the authenticated user.

**Request**:
```http
POST /api/v1/tasks HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

**Request Body**:
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `title` | string | Yes | 1-255 chars | Task title |
| `description` | string | No | - | Task description |

**Response**: `201 Created`
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2026-01-07T10:00:00Z",
  "updated_at": "2026-01-07T10:00:00Z",
  "version": 1
}
```

**Errors**:
| Status | Code | Description |
|--------|------|-------------|
| 400 | `validation_error` | Invalid request body |
| 400 | `title_required` | Title is missing or empty |
| 400 | `title_too_long` | Title exceeds 255 characters |
| 401 | `unauthorized` | Missing or invalid JWT token |

---

### 4. Update Task

**Endpoint**: `PUT /api/v1/tasks/{task_id}`

**Description**: Update an existing task. Requires version for optimistic locking.

**Request**:
```http
PUT /api/v1/tasks/123e4567-e89b-12d3-a456-426614174000 HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Buy groceries and supplies",
  "description": "Milk, eggs, bread, paper towels",
  "version": 1
}
```

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | UUID | Yes | The task's unique identifier |

**Request Body**:
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `title` | string | No | 1-255 chars | New task title |
| `description` | string | No | - | New task description |
| `completed` | boolean | No | - | New completion status |
| `version` | integer | Yes | - | Expected version for optimistic locking |

**Response**: `200 OK`
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Buy groceries and supplies",
  "description": "Milk, eggs, bread, paper towels",
  "completed": false,
  "created_at": "2026-01-07T10:00:00Z",
  "updated_at": "2026-01-07T10:05:00Z",
  "version": 2
}
```

**Errors**:
| Status | Code | Description |
|--------|------|-------------|
| 400 | `validation_error` | Invalid request body |
| 400 | `title_empty` | Title cannot be empty |
| 400 | `title_too_long` | Title exceeds 255 characters |
| 400 | `version_required` | Version field is required |
| 401 | `unauthorized` | Missing or invalid JWT token |
| 404 | `not_found` | Task not found or belongs to another user |
| 409 | `conflict` | Version mismatch (task was modified) |

---

### 5. Complete Task

**Endpoint**: `POST /api/v1/tasks/{task_id}/complete`

**Description**: Mark a task as complete.

**Request**:
```http
POST /api/v1/tasks/123e4567-e89b-12d3-a456-426614174000/complete HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{
  "version": 1
}
```

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | UUID | Yes | The task's unique identifier |

**Request Body**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | integer | Yes | Expected version for optimistic locking |

**Response**: `200 OK`
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": true,
  "created_at": "2026-01-07T10:00:00Z",
  "updated_at": "2026-01-07T10:10:00Z",
  "version": 2
}
```

**Errors**:
| Status | Code | Description |
|--------|------|-------------|
| 400 | `version_required` | Version field is required |
| 401 | `unauthorized` | Missing or invalid JWT token |
| 404 | `not_found` | Task not found or belongs to another user |
| 409 | `conflict` | Version mismatch |

---

### 6. Uncomplete Task

**Endpoint**: `POST /api/v1/tasks/{task_id}/uncomplete`

**Description**: Mark a task as incomplete.

**Request**:
```http
POST /api/v1/tasks/123e4567-e89b-12d3-a456-426614174000/uncomplete HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{
  "version": 2
}
```

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | UUID | Yes | The task's unique identifier |

**Request Body**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | integer | Yes | Expected version for optimistic locking |

**Response**: `200 OK`
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2026-01-07T10:00:00Z",
  "updated_at": "2026-01-07T10:15:00Z",
  "version": 3
}
```

**Errors**:
| Status | Code | Description |
|--------|------|-------------|
| 400 | `version_required` | Version field is required |
| 401 | `unauthorized` | Missing or invalid JWT token |
| 404 | `not_found` | Task not found or belongs to another user |
| 409 | `conflict` | Version mismatch |

---

### 7. Delete Task

**Endpoint**: `DELETE /api/v1/tasks/{task_id}`

**Description**: Permanently delete a task (hard delete per FR-020a).

**Request**:
```http
DELETE /api/v1/tasks/123e4567-e89b-12d3-a456-426614174000 HTTP/1.1
Authorization: Bearer <token>
```

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | UUID | Yes | The task's unique identifier |

**Response**: `204 No Content`

**Errors**:
| Status | Code | Description |
|--------|------|-------------|
| 401 | `unauthorized` | Missing or invalid JWT token |
| 404 | `not_found` | Task not found or belongs to another user |

---

## Error Response Format

All error responses follow this format:

```json
{
  "error": {
    "code": "error_code",
    "message": "Human-readable error message",
    "details": {}
  }
}
```

### Validation Error Example

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed",
    "details": {
      "title": ["Title is required"],
      "version": ["Version must be a positive integer"]
    }
  }
}
```

---

## HTTP Status Codes

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 201 | Created |
| 204 | No Content (successful deletion) |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (invalid/missing token) |
| 404 | Not Found (resource doesn't exist or not owned) |
| 409 | Conflict (optimistic locking failure) |
| 500 | Internal Server Error |

---

## Rate Limiting

Rate limiting is not implemented in Phase II but is planned for future enhancement.

---

## Versioning

The API is versioned via URL path (`/api/v1/`). Breaking changes will increment the version number.
