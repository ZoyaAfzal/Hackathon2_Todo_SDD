# Research: Phase III AI-Powered Todo Chatbot

**Date**: 2026-02-02
**Branch**: `002-phase-3-ai-chatbot`

## 1. OpenAI Agents SDK Integration

**Decision**: Use `openai-agents` Python SDK to create an Agent with
MCP tool access.

**Rationale**: The OpenAI Agents SDK provides built-in support for MCP
tool servers via `MCPServerStdio` or `MCPServerStreamableHttp`. It
handles tool calling, conversation management, and response streaming
natively. This eliminates custom intent parsing — the LLM handles
natural language understanding and tool selection.

**Alternatives considered**:
- LangChain: Heavier dependency, more abstraction layers than needed
- Direct OpenAI API with function calling: Lower level, requires
  manual tool dispatch and conversation loop management
- Custom NLP pipeline: Over-engineered for this scope

## 2. MCP Server Architecture

**Decision**: Implement an in-process MCP server using the official
`mcp` Python SDK. The MCP server runs as a stdio subprocess spawned
by the Agents SDK via `MCPServerStdio`.

**Rationale**: The Agents SDK's `MCPServerStdio` class spawns an MCP
server as a subprocess and communicates via stdin/stdout. This is the
simplest integration pattern. The MCP server script exposes 5 tools
(`add_task`, `list_tasks`, `update_task`, `complete_task`,
`delete_task`) that directly call the existing `TaskService`.

**Alternatives considered**:
- HTTP-based MCP server: Adds network overhead for local-only use
- Embedding tools directly as Agents SDK function tools: Bypasses
  MCP requirement from constitution

## 3. Conversation Persistence Strategy

**Decision**: Store conversations and messages in PostgreSQL using
SQLModel. Each chat request loads the last 50 messages for context,
sends them to the agent, and persists the new user message + assistant
response.

**Rationale**: Constitution mandates database-only state. Loading 50
messages balances context quality with token limits (~4000 tokens for
50 short messages). The agent receives full recent history per request.

**Alternatives considered**:
- Redis for conversation cache: Violates no-in-memory-state rule
- Full history load: Risk of token overflow on long conversations

## 4. Authentication Flow for Chat

**Decision**: Reuse the existing `get_current_user` JWT dependency
from `api/deps/auth.py`. The chat endpoint validates the JWT and
extracts `user_id`. The `{user_id}` path parameter is verified
against the token's `sub` claim to prevent ID spoofing.

**Rationale**: Phase II already has working JWT auth with Better Auth.
No new auth mechanism needed. Path parameter validation adds defense
in depth.

**Alternatives considered**:
- Session-based auth: Violates stateless requirement
- API key auth: Less secure, different from existing pattern

## 5. Database Schema for Conversations

**Decision**: Two new tables: `conversation` (id, user_id, title,
created_at, updated_at) and `message` (id, conversation_id, role,
content, tool_calls, created_at, sequence_number).

**Rationale**: Separate tables allow efficient queries. `sequence_number`
ensures ordering. `tool_calls` JSON column stores MCP tool invocations
for traceability. The `title` field on conversation enables future
conversation list UI.

**Alternatives considered**:
- Single denormalized table: Harder to query, wastes storage
- JSONB array of messages in conversation: Difficult to paginate

## 6. Error Handling & Retry

**Decision**: Single retry with 3-second timeout per attempt for AI
model API calls. Database errors return 503. Invalid task references
return 404 with descriptive message.

**Rationale**: Per clarification session, one retry balances
resilience vs latency. The 3-second timeout prevents hanging requests.

**Alternatives considered**:
- No retry: Poor UX for transient failures
- Exponential backoff: Too slow for interactive chat
