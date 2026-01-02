# ChatKit Custom Backend — Python Reference

This document supports the `openai-chatkit-backend-python` Skill.
It standardizes how you implement and reason about a **custom ChatKit backend**
in Python, powered by the **OpenAI Agents SDK** (and optionally Gemini via an
OpenAI-compatible endpoint).

Use this as the **high-authority reference** for:
- Folder structure and separation of concerns
- Environment variables and model factory behavior
- Expected HTTP endpoints for ChatKit
- How ChatKit events are handled in the backend
- How to integrate Agents SDK (agents, tools, runners)
- Streaming, auth, security, and troubleshooting

---

## 1. Recommended Folder Structure

A clean project structure keeps ChatKit transport logic separate from the
Agents SDK logic and business tools.

```text
backend/
  main.py                # FastAPI / Flask / Django entry
  env.py                 # env loading, settings
  chatkit/
    __init__.py
    router.py            # ChatKit event routing + handlers
    upload.py            # Upload endpoint helpers
    streaming.py         # SSE helpers (optional)
    types.py             # Typed helpers for ChatKit events (optional)
  agents/
    __init__.py
    factory.py           # create_model() lives here
    base_agent.py        # base configuration or utilities
    support_agent.py     # example specialized agent
    tools/
      __init__.py
      db_tools.py        # DB-related tools
      erp_tools.py       # ERP-related tools
```

**Key idea:**  
- `chatkit/` knows about HTTP requests/responses and ChatKit event shapes.  
- `agents/` knows about models, tools, and reasoning.  
- Nothing in `agents/` should know that ChatKit exists.

---

## 2. Environment Variables & Model Factory Contract

All model selection must go through a **single factory function** in
`agents/factory.py`. This keeps your backend flexible and prevents
ChatKit-specific code from hard-coding model choices.

### 2.1 Required/Recommended Env Vars

```text
LLM_PROVIDER=openai or gemini

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_DEFAULT_MODEL=gpt-4.1-mini

# Gemini via OpenAI-compatible endpoint
GEMINI_API_KEY=...
GEMINI_DEFAULT_MODEL=gemini-2.5-flash

# Optional
LOG_LEVEL=INFO
```

### 2.2 Factory Contract

```python
# agents/factory.py

def create_model():
    """Return a model object compatible with the Agents SDK.

    - Uses LLM_PROVIDER to decide provider.
    - Uses provider-specific env vars for keys and defaults.
    - Returns a model usable in Agent(model=...).
    """
```

Rules:

- If `LLM_PROVIDER` is `"gemini"`, use an OpenAI-compatible client with:
  `base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"`.
- If it is `"openai"` or unset, use OpenAI default with `OPENAI_API_KEY`.
- Never instantiate models directly inside ChatKit handlers; always call
  `create_model()`.

---

## 3. Required HTTP Endpoints for ChatKit

In **custom backend** mode, the frontend ChatKit client is configured to call
your backend instead of OpenAI’s hosted workflows.

At minimum, the backend should provide:

### 3.1 Main Chat Endpoint

```http
POST /chatkit/api
```

Responsibilities:

- Authenticate the incoming request (session / JWT / cookie).
- Parse the incoming ChatKit event (e.g., user message, action).
- Create or reuse an appropriate agent (using `create_model()`).
- Invoke the Agents SDK (Agent + Runner).
- Return a response in a shape compatible with ChatKit expectations
  (usually a JSON object / stream that represents the assistant’s reply).

### 3.2 Upload Endpoint (Optional)

If the frontend config uses a **direct upload strategy**, you’ll also need:

```http
POST /chatkit/api/upload
```

Responsibilities:

- Accept file uploads (`multipart/form-data`).
- Store the file (local disk, S3, etc.).
- Return a JSON body with a URL and any metadata ChatKit expects
  (e.g., `{ "url": "https://cdn.example.com/path/file.pdf" }`).

The frontend will include this URL in messages or pass it as context.

---

## 4. ChatKit Protocol (CRITICAL)

### 4.1 Request Protocol

ChatKit sends JSON requests with `type` and `params` fields:

```python
# threads.list - Get conversation list
{"type": "threads.list", "params": {"limit": 9999, "order": "desc"}}

# threads.create - Create new thread (may include initial message in params.input)
{"type": "threads.create", "params": {"input": {...}}}

# threads.get - Get thread with messages
{"type": "threads.get", "params": {"threadId": "123"}}

# threads.delete - Delete thread
{"type": "threads.delete", "params": {"threadId": "123"}}

# messages.send - Send message (rarely used - usually sent via threads.create)
{"type": "messages.send", "params": {"threadId": "123", "input": {...}}}
```

**IMPORTANT**: ChatKit often sends user messages via `threads.create` with an `input` field, NOT via separate `messages.send` calls. Check for `params.input.content` in threads.create requests.

### 4.2 SSE Response Protocol (CRITICAL)

When streaming responses, you MUST use the exact ChatKit SSE event format:

**Event Types:**
1. `thread.created` - Announce thread
2. `thread.item.added` - Add new item (user message, assistant message, widget)
3. `thread.item.updated` - Stream text deltas or widget updates
4. `thread.item.done` - Finalize item with complete content
5. `error` - Error event

**SSE Format:**
```
data: {"type":"<event_type>",...}\n\n
```

**Critical: Content Type Discriminators**

User messages use `type: "input_text"`:
```python
{
  "type": "thread.item.added",
  "item": {
    "type": "user_message",
    "id": "msg_123",
    "thread_id": "thread_456",
    "content": [{"type": "input_text", "text": "user message"}],
    "attachments": [],
    "quoted_text": None,
    "inference_options": {}
  }
}
```

Assistant messages use `type: "output_text"`:
```python
{
  "type": "thread.item.added",
  "item": {
    "type": "assistant_message",
    "id": "msg_789",
    "thread_id": "thread_456",
    "content": [{"type": "output_text", "text": "", "annotations": []}]
  }
}
```

**Text Delta Streaming:**
```python
{
  "type": "thread.item.updated",
  "item_id": "msg_789",
  "update": {
    "type": "assistant_message.content_part.text_delta",
    "content_index": 0,
    "delta": "text chunk"
  }
}
```

**Final Item:**
```python
{
  "type": "thread.item.done",
  "item": {
    "type": "assistant_message",
    "id": "msg_789",
    "thread_id": "thread_456",
    "content": [{"type": "output_text", "text": "full response", "annotations": []}]
  }
}
```

### 4.3 Common Protocol Errors

**Error: "Expected undefined to be output_text"**
- Cause: Using `"type": "text"` instead of `"type": "output_text"` in assistant message content
- Fix: Always use `"output_text"` for assistant messages, `"input_text"` for user messages

**Error: "Cannot read properties of undefined (reading 'filter')"**
- Cause: Missing required fields in user_message items (attachments, quoted_text, inference_options)
- Fix: Always include all required fields even if empty/null

**Error: Widget not rendering**
- Cause: Frontend CDN script not loaded
- Fix: Ensure ChatKit CDN is loaded in frontend (see frontend skill)

---

## 5. Agents SDK Integration Rules

All reasoning and tool execution should be done via the **Agents SDK**,
not via direct `chat.completions` calls.

### 5.1 Basic Agent Execution

```python
from agents import Agent, Runner
from agents.factory import create_model

def run_simple_agent(user_text: str) -> str:
    agent = Agent(
        name="chatkit-backend-agent",
        model=create_model(),
        instructions=(
            "You are the backend agent behind a ChatKit UI. "
            "Respond concisely and be robust to noisy input."
        ),
    )
    result = Runner.run_sync(starting_agent=agent, input=user_text)
    return result.final_output
```

### 5.2 Tools Integration: MCP vs Function Tools

The OpenAI Agents SDK supports **TWO tool integration patterns**:

#### Option A: Function Tools (Simple, In-Process)

```python
from agents import function_tool

@function_tool
async def add_task(title: str, description: str = "") -> dict:
    """Add a task directly in the same process."""
    # Tool logic here
    return {"status": "created", "title": title}

agent = Agent(
    name="Task Agent",
    tools=[add_task],  # Direct function
    model=create_model()
)
```

**Pros**: Simple, fast, no extra process
**Cons**: Not reusable across applications, coupled to Python process

#### Option B: MCP Server Tools (Production, Reusable) ✅ RECOMMENDED

```python
from agents.mcp import MCPServerStdio

async with MCPServerStdio(
    name="Task Management Server",
    params={
        "command": "python",
        "args": ["mcp_server.py"],  # Separate process
    },
) as server:
    agent = Agent(
        name="Task Agent",
        mcp_servers=[server],  # MCP protocol
        model=create_model()
    )

    result = await Runner.run(agent, "Add task homework")
```

**Pros**:
- Reusable across Claude Desktop, VS Code, your app
- Process isolation (security)
- Industry standard (MCP protocol)
- Tool discovery automatic

**Cons**: Requires separate MCP server process

### 5.3 Building MCP Servers

MCP servers are separate processes that expose tools via the Model Context Protocol.

**Required Dependencies:**
```bash
pip install mcp>=1.0.0  # Official MCP Python SDK
```

**MCP Server Structure** (`mcp_server.py`):

```python
import asyncio
from mcp.server import Server
from mcp.server import stdio
from mcp.types import Tool, TextContent, CallToolResult

# Create MCP server
server = Server("my-task-server")

# Register tools
@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="add_task",
            description="Create a new task",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["title"]
            }
        )
    ]

# Handle tool calls
@server.call_tool()
async def handle_call(name: str, arguments: dict) -> CallToolResult:
    if name == "add_task":
        title = arguments["title"]
        # Business logic here
        return CallToolResult(
            content=[TextContent(type="text", text=f"Created: {title}")],
            structuredContent={"task_id": 123, "title": title}
        )

# Run server
async def main():
    async with stdio.stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
```

### 5.4 MCP Server Integration with FastAPI

**In your ChatKit handler:**

```python
from agents.mcp import MCPServerStdio

async def handle_messages_send(params, session, user, request):
    # Create MCP server connection (async context manager)
    async with MCPServerStdio(
        name="Task Management",
        params={
            "command": "python",
            "args": ["backend/mcp_server.py"],
            "env": {
                "DATABASE_URL": os.environ["DATABASE_URL"],
                "USER_ID": user.id  # Pass context to MCP server
            }
        },
        cache_tools_list=True,  # Cache for performance
    ) as mcp_server:

        # Create agent with MCP tools
        agent = Agent(
            name="TaskAssistant",
            instructions="Help manage tasks",
            model=create_model(),
            mcp_servers=[mcp_server],  # ← MCP tools
        )

        # Run agent
        result = Runner.run_streamed(agent, messages)

        async for event in result.stream_events():
            # Stream to ChatKit
            yield event
```

### 5.5 MCP Tool Parameter Rules (CRITICAL)

**Problem**: Pydantic/OpenAI Agents SDK marks ALL parameters as required in JSON schema, even with defaults.

**Solution**: Use explicit empty strings/defaults with clear documentation:

```python
# In MCP server tool registration
Tool(
    name="add_task",
    inputSchema={
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Task title (REQUIRED)"
            },
            "description": {
                "type": "string",
                "description": "Task description (optional, can be empty string)"
            }
        },
        "required": ["title"]  # Only truly required fields
    }
)
```

**In Agent Instructions**:
```
TOOL: add_task
- title: REQUIRED
- description: OPTIONAL (can be omitted or empty string)

Examples:
✅ add_task(title="homework")
✅ add_task(title="homework", description="Math assignment")
❌ add_task() - missing title
```

### 5.6 When to Use Which Pattern

| Use Case | Pattern | Why |
|----------|---------|-----|
| Prototype/MVP | Function Tools | Faster to implement |
| Production | MCP Server | Reusable, secure, standard |
| Multi-app | MCP Server | One server, many clients |
| Simple tools | Function Tools | No process overhead |
| Complex workflows | MCP Server | Better isolation |

**Recommendation**: Start with function tools, migrate to MCP for production.

---

## 5.7 MCP Transport Options

The MCP SDK supports multiple transports:

### Stdio (Local Development)
```python
MCPServerStdio(
    params={"command": "python", "args": ["mcp_server.py"]}
)
```

### SSE (Remote/Production)
```python
from agents.mcp import MCPServerSse

MCPServerSse(
    params={"url": "https://mcp.example.com/sse"}
)
```

### Streamable HTTP (Low-latency)
```python
from agents.mcp import MCPServerStreamableHttp

MCPServerStreamableHttp(
    params={"url": "https://mcp.example.com/mcp"}
)
```

ChatKit itself does not know about tools; it only sees the agent's messages.

---

## 6. Streaming Responses

For better UX, you may choose to stream responses to ChatKit using
Server-Sent Events (SSE) or an equivalent streaming mechanism supported
by your framework.

General rules:

- The handler for `/chatkit/api` should return a streaming response.
- Each chunk should be formatted consistently (e.g., `data: {...}\n\n`).
- The final chunk should clearly indicate completion (e.g., `done: true`).

You may wrap the Agents SDK call in a generator that yields partial tokens
or partial messages as they are produced.

---

## 7. Auth, Security, and Tenant Context

### 7.1 Auth

- Every request to `/chatkit/api` and `/chatkit/api/upload` must be authenticated.
- Common patterns: bearer tokens, session cookies, signed headers.
- The backend must **never** return API keys or other secrets to the browser.

### 7.2 Tenant / User Context

Often you’ll want to include:

- `user_id`
- `tenant_id` / `company_id`
- user’s role (e.g. `employee`, `manager`, `admin`)

into the agent’s instructions or tool calls. For example:

```python
instructions = f"""
You are the support agent for tenant {tenant_id}.
You must respect role-based access and never leak other tenants' data.
Current user: {user_id}, role: {role}.
"""
```

### 7.3 Domain Allowlist

If the ChatKit widget renders blank or fails silently, verify:

- The frontend origin domain is included in the OpenAI dashboard allowlist.
- The `domainKey` configured on the frontend matches the backend’s expectations.

---

## 8. Logging and Troubleshooting

### 8.1 What to Log

- Incoming ChatKit event types and minimal metadata (no secrets).
- Auth failures (excluding raw tokens).
- Agents SDK errors (model not found, invalid arguments, tool exceptions).
- File upload failures.

### 8.2 Common Failure Modes

- **Blank ChatKit UI**  
  → Domain not allowlisted or domainKey mismatch.

- **“Loading…” never completes**  
  → Backend did not return a valid response or streaming never sends final chunk.

- **Model / provider errors**  
  → Wrong `LLM_PROVIDER`, incorrect API key, or wrong base URL.

- **Multipart upload errors**  
  → Upload endpoint doesn’t accept `multipart/form-data` or returns wrong JSON shape.

Having structured logs (JSON logs) greatly speeds up debugging.

---

## 9. Evolution and Versioning

Over time, ChatKit and the Agents SDK may evolve. To keep this backend
maintainable:

- Treat the official ChatKit Custom Backends docs as the top-level source of truth.
- Treat `agents/factory.py` as the single place to update model/provider logic.
- When updating the Agents SDK:
  - Verify that Agent/Runner APIs have not changed.
  - Update tools to match any new signatures or capabilities.

When templates or examples drift from the docs, prefer the **docs** and
update the local files accordingly.
