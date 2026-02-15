# Data Model: Phase III AI-Powered Todo Chatbot

**Date**: 2026-02-02
**Branch**: `002-phase-3-ai-chatbot`

## Existing Entities (Phase II — no changes)

### User
| Field         | Type         | Constraints          |
|---------------|--------------|----------------------|
| id            | UUID         | PK, auto-generated   |
| email         | VARCHAR(255) | UNIQUE, NOT NULL     |
| password_hash | VARCHAR(255) | NOT NULL             |
| created_at    | TIMESTAMP    | NOT NULL, default now|

### Task
| Field       | Type         | Constraints                    |
|-------------|--------------|--------------------------------|
| id          | UUID         | PK, auto-generated             |
| title       | VARCHAR(255) | NOT NULL                       |
| description | TEXT         | NULLABLE                       |
| completed   | BOOLEAN      | NOT NULL, default false        |
| created_at  | TIMESTAMP    | NOT NULL, default now          |
| updated_at  | TIMESTAMP    | NOT NULL, default now          |
| version     | INTEGER      | NOT NULL, default 1            |
| user_id     | UUID         | FK → user.id, NOT NULL, INDEX  |

## New Entities (Phase III)

### Conversation
| Field      | Type         | Constraints                    |
|------------|--------------|--------------------------------|
| id         | UUID         | PK, auto-generated             |
| user_id    | UUID         | FK → user.id, NOT NULL, INDEX  |
| title      | VARCHAR(255) | NULLABLE, auto-generated       |
| created_at | TIMESTAMP    | NOT NULL, default now          |
| updated_at | TIMESTAMP    | NOT NULL, default now          |

**Relationships**:
- Conversation → User: many-to-one (user_id FK)
- Conversation → Message: one-to-many

**Lifecycle**: Created on first message when no `conversation_id`
provided. Title auto-set from first user message (first 50 chars).
Updated timestamp refreshed on each new message.

### Message
| Field            | Type    | Constraints                           |
|------------------|---------|---------------------------------------|
| id               | UUID    | PK, auto-generated                    |
| conversation_id  | UUID    | FK → conversation.id, NOT NULL, INDEX |
| role             | VARCHAR | NOT NULL, enum: "user", "assistant"   |
| content          | TEXT    | NOT NULL                              |
| tool_calls       | JSONB   | NULLABLE, stores MCP tool invocations |
| sequence_number  | INTEGER | NOT NULL, auto-increment per convo    |
| created_at       | TIMESTAMP | NOT NULL, default now               |

**Relationships**:
- Message → Conversation: many-to-one (conversation_id FK)

**Ordering**: Messages ordered by `sequence_number` ASC within a
conversation. Sequence numbers are assigned at insert time,
incrementing from the max in that conversation.

**Context Window**: When loading history for the AI agent, the most
recent 50 messages (by sequence_number DESC) are loaded.

## Entity Relationship Diagram

```
User (1) ──── (N) Task
  │
  └──── (N) Conversation (1) ──── (N) Message
```

## Indexes

- `conversation.user_id` — filter conversations by user
- `message.conversation_id` — load messages for a conversation
- `message.(conversation_id, sequence_number)` — composite for
  ordered message retrieval

## Data Isolation Rules

- All queries for Task, Conversation, and Message MUST include
  `user_id` filter (directly or via conversation ownership)
- Message queries go through conversation ownership: verify
  `conversation.user_id` matches the authenticated user before
  loading messages
