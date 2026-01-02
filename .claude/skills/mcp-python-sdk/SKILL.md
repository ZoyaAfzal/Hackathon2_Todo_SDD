---
name: mcp-python-sdk
description: >
  Model Context Protocol (MCP) Python SDK for building servers with tools, resources,
  and prompts. Use when implementing MCP servers for AI agent integrations, creating
  tools that agents can invoke, or building standardized AI interfaces.
---

# MCP Python SDK Skill

You are an **MCP Python SDK specialist**.

Your job is to help users design and implement **MCP servers** using the official Model Context Protocol Python SDK (`mcp` package).

## 1. When to Use This Skill

Use this Skill **whenever**:

- The user mentions:
  - "MCP server"
  - "MCP tools"
  - "Model Context Protocol"
  - "AI tool interface"
  - "standardized agent tools"
- Or asks to:
  - Create tools that AI agents can invoke
  - Build resources for agent access
  - Implement prompts for agent interactions
  - Connect agents to backend operations

## 2. Core Concepts

### 2.1 FastMCP (High-Level API)

The recommended approach for most use cases:

```python
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Demo", json_response=True)

# Add a tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# Add a dynamic resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

# Add a prompt
@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    """Generate a greeting prompt"""
    styles = {
        "friendly": "Please write a warm, friendly greeting",
        "formal": "Please write a formal, professional greeting",
        "casual": "Please write a casual, relaxed greeting",
    }
    return f"{styles.get(style, styles['friendly'])} for someone named {name}."

# Run with streamable HTTP transport (default)
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

### 2.2 Three Core Primitives

1. **Tools** - Functions the AI can invoke to perform actions
2. **Resources** - Data/content the AI can read (like files or APIs)
3. **Prompts** - Reusable prompt templates

## 3. Tool Definition Patterns

### 3.1 Basic Sync Tool

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Task Manager")

@mcp.tool()
def add_task(user_id: str, title: str, description: str = None) -> dict:
    """Create a new task for a user.

    Args:
        user_id: The user's ID
        title: Task title (required)
        description: Optional task description

    Returns:
        Created task with id, status, and title
    """
    task_id = create_task_in_db(user_id, title, description)
    return {"task_id": task_id, "status": "created", "title": title}
```

### 3.2 Async Tool

```python
@mcp.tool()
async def list_tasks(user_id: str, status: str = "all") -> list:
    """List tasks for a user.

    Args:
        user_id: The user's ID
        status: Filter by status - "all", "pending", or "completed"

    Returns:
        List of task objects
    """
    tasks = await fetch_tasks_from_db(user_id, status)
    return [{"id": t.id, "title": t.title, "completed": t.completed} for t in tasks]
```

### 3.3 Tool with Context

Context provides access to MCP capabilities like logging, progress reporting, and resource reading:

```python
from mcp.server.fastmcp import Context, FastMCP
from mcp.server.session import ServerSession

mcp = FastMCP("Progress Example")

@mcp.tool()
async def long_running_task(
    task_name: str,
    ctx: Context[ServerSession, None],
    steps: int = 5
) -> str:
    """Execute a task with progress updates."""
    await ctx.info(f"Starting: {task_name}")

    for i in range(steps):
        progress = (i + 1) / steps
        await ctx.report_progress(
            progress=progress,
            total=1.0,
            message=f"Step {i + 1}/{steps}",
        )
        await ctx.debug(f"Completed step {i + 1}")

    return f"Task '{task_name}' completed"
```

### 3.4 Structured Output with Pydantic

```python
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Structured Output Example")

class WeatherData(BaseModel):
    """Weather information structure."""
    temperature: float = Field(description="Temperature in Celsius")
    humidity: float = Field(description="Humidity percentage")
    condition: str
    wind_speed: float

@mcp.tool()
def get_weather(city: str) -> WeatherData:
    """Get weather for a city - returns structured data."""
    return WeatherData(
        temperature=22.5,
        humidity=45.0,
        condition="sunny",
        wind_speed=5.2,
    )
```

### 3.5 TypedDict for Simpler Structures

```python
from typing import TypedDict

class LocationInfo(TypedDict):
    latitude: float
    longitude: float
    name: str

@mcp.tool()
def get_location(address: str) -> LocationInfo:
    """Get location coordinates"""
    return LocationInfo(latitude=51.5074, longitude=-0.1278, name="London, UK")
```

### 3.6 Advanced: Direct CallToolResult

For complete control over response including metadata:

```python
from typing import Annotated
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP
from mcp.types import CallToolResult, TextContent

mcp = FastMCP("CallToolResult Example")

class ValidationModel(BaseModel):
    status: str
    data: dict[str, int]

@mcp.tool()
def advanced_tool() -> CallToolResult:
    """Return CallToolResult directly for full control including _meta field."""
    return CallToolResult(
        content=[TextContent(type="text", text="Response visible to the model")],
        _meta={"hidden": "data for client applications only"},
    )

@mcp.tool()
def validated_tool() -> Annotated[CallToolResult, ValidationModel]:
    """Return CallToolResult with structured output validation."""
    return CallToolResult(
        content=[TextContent(type="text", text="Validated response")],
        structuredContent={"status": "success", "data": {"result": 42}},
        _meta={"internal": "metadata"},
    )
```

## 4. Resource Definition Patterns

### 4.1 Static Resource

```python
@mcp.resource("config://app")
def get_config() -> str:
    """Application configuration."""
    return '{"theme": "dark", "version": "1.0"}'
```

### 4.2 Dynamic Resource with URI Template

```python
@mcp.resource("users://{user_id}/profile")
def get_user_profile(user_id: str) -> str:
    """Get user profile by ID."""
    user = fetch_user(user_id)
    return json.dumps({"id": user.id, "name": user.name})
```

### 4.3 Resource with Context

```python
@mcp.resource("tasks://{user_id}")
async def get_user_tasks(user_id: str, ctx: Context) -> str:
    """Get all tasks for a user."""
    await ctx.info(f"Fetching tasks for user {user_id}")
    tasks = await fetch_tasks(user_id)
    return json.dumps([t.dict() for t in tasks])
```

### 4.4 Resource with Icons

```python
from mcp.server.fastmcp import FastMCP, Icon

icon = Icon(src="icon.png", mimeType="image/png", sizes="64x64")

@mcp.resource("demo://resource", icons=[icon])
def my_resource():
    """Resource with an icon."""
    return "content"
```

## 5. Prompt Definition Patterns

### 5.1 Simple Prompt

```python
@mcp.prompt(title="Code Review")
def review_code(code: str) -> str:
    """Generate a code review prompt."""
    return f"Please review this code:\n\n{code}"
```

### 5.2 Multi-turn Prompt

```python
from mcp.server.fastmcp.prompts import base

@mcp.prompt(title="Debug Assistant")
def debug_error(error: str) -> list[base.Message]:
    """Generate a debugging conversation."""
    return [
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]
```

## 6. Lifespan Management (Setup/Teardown)

### 6.1 FastMCP Lifespan with Type-Safe Context

```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from mcp.server.fastmcp import Context, FastMCP
from mcp.server.session import ServerSession

class Database:
    @classmethod
    async def connect(cls) -> "Database":
        return cls()

    async def disconnect(self) -> None:
        pass

    def query(self, sql: str) -> str:
        return "Query result"

@dataclass
class AppContext:
    """Application context with typed dependencies."""
    db: Database

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with type-safe context."""
    db = await Database.connect()
    try:
        yield AppContext(db=db)
    finally:
        await db.disconnect()

# Pass lifespan to server
mcp = FastMCP("My App", lifespan=app_lifespan)

# Access type-safe lifespan context in tools
@mcp.tool()
def query_db(sql: str, ctx: Context[ServerSession, AppContext]) -> str:
    """Tool that uses initialized resources."""
    db = ctx.request_context.lifespan_context.db
    return db.query(sql)
```

## 7. User Elicitation (Interactive Input)

```python
from pydantic import BaseModel, Field
from mcp.server.fastmcp import Context, FastMCP
from mcp.server.session import ServerSession

mcp = FastMCP("Booking Service")

class BookingPreferences(BaseModel):
    checkAlternative: bool = Field(description="Check another date?")
    alternativeDate: str = Field(
        default="2024-12-26",
        description="Alternative date (YYYY-MM-DD)"
    )

@mcp.tool()
async def book_table(
    date: str,
    time: str,
    party_size: int,
    ctx: Context[ServerSession, None]
) -> str:
    """Book a table with date availability checking."""
    if date == "2024-12-25":
        # Request user input when date unavailable
        result = await ctx.elicit(
            message=f"No tables available for {party_size} on {date}. Try another date?",
            schema=BookingPreferences
        )

        if result.action == "accept" and result.data:
            if result.data.checkAlternative:
                return f"[SUCCESS] Booked for {result.data.alternativeDate}"
            return "[CANCELLED] No booking made"
        return "[CANCELLED] Booking cancelled"

    return f"[SUCCESS] Booked for {date} at {time} for {party_size} people"
```

## 8. Transport Options

### 8.1 Streamable HTTP (Default - for Web)

```python
if __name__ == "__main__":
    mcp.run(transport="streamable-http")  # Default, accessible at http://localhost:8000/mcp
```

### 8.2 stdio (for CLI tools)

```python
if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### 8.3 Async Execution

```python
import anyio

if __name__ == "__main__":
    anyio.run(mcp.run_async)
```

## 9. Low-Level Server API

For advanced use cases requiring more control:

```python
import asyncio
from typing import Any
import mcp.server.stdio
import mcp.types as types
from mcp.server.lowlevel import NotificationOptions, Server
from mcp.server.models import InitializationOptions

server = Server("example-server")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """Return available tools."""
    return [
        types.Tool(
            name="calculate",
            description="Perform calculations",
            inputSchema={
                "type": "object",
                "properties": {
                    "operation": {"type": "string", "enum": ["add", "multiply"]},
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["operation", "a", "b"]
            },
            outputSchema={
                "type": "object",
                "properties": {
                    "result": {"type": "number"},
                    "operation": {"type": "string"}
                },
                "required": ["result", "operation"]
            }
        )
    ]

@server.call_tool()
async def handle_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Handle tool execution with structured output."""
    if name != "calculate":
        raise ValueError(f"Unknown tool: {name}")

    operation = arguments["operation"]
    a, b = arguments["a"], arguments["b"]

    if operation == "add":
        result = a + b
    elif operation == "multiply":
        result = a * b
    else:
        raise ValueError(f"Unknown operation: {operation}")

    return {"result": result, "operation": operation}

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """Return available resources."""
    return [
        types.Resource(
            uri=types.AnyUrl("data://stats"),
            name="Statistics",
            description="System statistics"
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: types.AnyUrl) -> str | bytes:
    """Read resource content."""
    if str(uri) == "data://stats":
        return '{"cpu": 45, "memory": 60}'
    raise ValueError(f"Unknown resource: {uri}")

async def run():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="example-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(run())
```

## 10. Client API

For connecting to MCP servers:

```python
import asyncio
from pydantic import AnyUrl
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List and call tools
            tools = await session.list_tools()
            print(f"Available tools: {[t.name for t in tools.tools]}")

            result = await session.call_tool("add", arguments={"a": 5, "b": 3})
            if isinstance(result.content[0], types.TextContent):
                print(f"Tool result: {result.content[0].text}")

            # List and read resources
            resources = await session.list_resources()
            resource_content = await session.read_resource(AnyUrl("greeting://World"))

            # List and get prompts
            prompts = await session.list_prompts()
            if prompts.prompts:
                prompt = await session.get_prompt(
                    "greet_user",
                    arguments={"name": "Alice", "style": "friendly"}
                )

if __name__ == "__main__":
    asyncio.run(main())
```

### HTTP Client Transport

```python
from mcp.client.streamable_http import streamablehttp_client

async def main():
    async with streamablehttp_client("http://localhost:8000/mcp") as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(f"Available tools: {[tool.name for tool in tools.tools]}")
```

## 11. Key Types Reference

```python
from mcp.types import (
    # Content types
    TextContent,
    ImageContent,
    EmbeddedResource,

    # Tool types
    Tool,
    ToolAnnotations,
    CallToolResult,

    # Resource types
    Resource,
    ResourceTemplate,

    # Prompt types
    Prompt,
    PromptMessage,
    GetPromptResult,

    # Protocol
    LATEST_PROTOCOL_VERSION,
    AnyUrl,
)

from mcp.server.fastmcp import (
    FastMCP,
    Context,
    Icon,
)

from mcp.server.fastmcp.prompts import base
# base.Message, base.UserMessage, base.AssistantMessage

from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions
```

## 12. Debugging Tips

- **Tool not being called**: Check docstring - it must describe what the tool does
- **Parameter errors**: Ensure type hints match expected input
- **Context not available**: Add `ctx: Context` parameter with type annotation
- **Transport issues**: Verify correct transport - `streamable-http` for web, `stdio` for CLI
- **Lifespan context errors**: Access via `ctx.request_context.lifespan_context`
- **Structured output not working**: Use Pydantic models with type hints for schema generation
