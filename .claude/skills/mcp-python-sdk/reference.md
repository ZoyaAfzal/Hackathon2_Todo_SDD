# MCP Python SDK Reference

## Installation

```bash
pip install mcp
# or with uv
uv add mcp
```

## FastMCP Class (High-Level API)

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name: str,                      # Server name (required)
    instructions: str = None,       # Optional instructions for AI
    lifespan: Callable = None,      # Optional async context manager for setup/teardown
    json_response: bool = False,    # Enable JSON responses
    website_url: str = None,        # Server website URL
    icons: list[Icon] = None,       # Server icons for UI display
)
```

## Tool Decorator

```python
@mcp.tool()
def tool_name(param: type) -> return_type:
    """Docstring becomes tool description for AI."""
    ...

# With title
@mcp.tool(title="Human Readable Name")
def my_tool(...): ...

# With icons
@mcp.tool(icons=[icon])
def my_tool(...): ...
```

**Return Types for Structured Output:**

```python
# Pydantic models (recommended for rich structures)
class WeatherData(BaseModel):
    temperature: float = Field(description="Temperature in Celsius")
    condition: str

@mcp.tool()
def get_weather(city: str) -> WeatherData:
    return WeatherData(temperature=22.5, condition="sunny")

# TypedDict for simpler structures
class LocationInfo(TypedDict):
    latitude: float
    longitude: float

@mcp.tool()
def get_location(addr: str) -> LocationInfo:
    return LocationInfo(latitude=51.5, longitude=-0.1)

# Dict for flexible schemas
@mcp.tool()
def get_stats() -> dict[str, float]:
    return {"mean": 42.5, "median": 40.0}

# Primitive types (automatically wrapped in {"result": value})
@mcp.tool()
def get_temp() -> float:
    return 22.5  # Returns: {"result": 22.5}

# Direct CallToolResult for full control
@mcp.tool()
def advanced() -> CallToolResult:
    return CallToolResult(
        content=[TextContent(type="text", text="Response")],
        structuredContent={"data": "value"},
        _meta={"hidden": "metadata"}
    )

# With validation via Annotated
@mcp.tool()
def validated() -> Annotated[CallToolResult, ValidationModel]:
    return CallToolResult(...)
```

## Resource Decorator

```python
# Static resource
@mcp.resource("uri://path")
def resource_name() -> str:
    """Resource description."""
    return "content"

# Dynamic resource with URI template
@mcp.resource("users://{user_id}/data")
def get_user_data(user_id: str) -> str:
    """Get data for user."""
    return json.dumps({"user_id": user_id})

# With icons
@mcp.resource("demo://resource", icons=[icon])
def my_resource() -> str:
    return "content"

# Async resource
@mcp.resource("tasks://{user_id}")
async def get_tasks(user_id: str) -> str:
    tasks = await fetch_tasks(user_id)
    return json.dumps(tasks)
```

## Prompt Decorator

```python
from mcp.server.fastmcp.prompts import base

# Simple string prompt
@mcp.prompt()
def simple_prompt(param: str) -> str:
    """Prompt description."""
    return f"Process: {param}"

# With title
@mcp.prompt(title="Code Review")
def review_code(code: str) -> str:
    return f"Review this code:\n{code}"

# Multi-turn conversation prompt
@mcp.prompt(title="Debug Assistant")
def multi_turn_prompt(error: str) -> list[base.Message]:
    """Multi-turn conversation prompt."""
    return [
        base.UserMessage("First message"),
        base.AssistantMessage("Response"),
        base.UserMessage(error),
    ]
```

## Context Object

```python
from mcp.server.fastmcp import Context
from mcp.server.session import ServerSession

@mcp.tool()
async def tool_with_context(param: str, ctx: Context[ServerSession, AppContext]) -> str:
    # Logging
    await ctx.info("Info message")
    await ctx.debug("Debug message")
    await ctx.warning("Warning message")

    # Progress reporting
    await ctx.report_progress(
        progress=0.5,       # Current progress
        total=1.0,          # Total (for percentage)
        message="Halfway"   # Optional message
    )

    # Access lifespan context (if configured)
    app_ctx = ctx.request_context.lifespan_context
    db = app_ctx.db

    # Read other resources
    content = await ctx.read_resource("config://settings")

    # Access server properties
    server_name = ctx.fastmcp.name
    debug_mode = ctx.fastmcp.settings.debug

    # Send notifications
    await ctx.session.send_resource_list_changed()

    # User elicitation (interactive input)
    result = await ctx.elicit(
        message="Need more info",
        schema=PreferencesModel  # Pydantic model
    )
    if result.action == "accept" and result.data:
        # Use result.data (validated against schema)
        pass

    return "result"
```

## Icon Class

```python
from mcp.server.fastmcp import Icon

icon = Icon(
    src="icon.png",           # File path or URL
    mimeType="image/png",     # MIME type
    sizes="64x64"             # Size specification
)

# Usage
mcp = FastMCP("Server", icons=[icon])

@mcp.tool(icons=[icon])
def my_tool(): ...

@mcp.resource("uri://path", icons=[icon])
def my_resource(): ...
```

## Lifespan Management

```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

@dataclass
class AppContext:
    db: Database
    config: dict

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage server lifecycle."""
    # Startup
    db = await Database.connect()
    config = load_config()
    try:
        yield AppContext(db=db, config=config)
    finally:
        # Shutdown
        await db.disconnect()

mcp = FastMCP("My App", lifespan=app_lifespan)
```

## Running the Server

```python
# Streamable HTTP transport (default for web)
mcp.run(transport="streamable-http")  # http://localhost:8000/mcp

# stdio transport (for CLI tools)
mcp.run(transport="stdio")

# Async execution
import anyio
anyio.run(mcp.run_async)
```

## Low-Level Server API

For advanced use cases requiring more control:

```python
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

server = Server("example-server")

# Or with lifespan
server = Server("example-server", lifespan=server_lifespan)

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="my_tool",
            description="Tool description",
            inputSchema={
                "type": "object",
                "properties": {
                    "param": {"type": "string", "description": "Parameter"}
                },
                "required": ["param"]
            },
            outputSchema={  # Optional: for structured output
                "type": "object",
                "properties": {
                    "result": {"type": "string"}
                },
                "required": ["result"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> dict | list[types.TextContent]:
    if name == "my_tool":
        # Return dict for structured output (validated against outputSchema)
        return {"result": "value"}
        # Or return TextContent for unstructured
        # return [types.TextContent(type="text", text="result")]
    raise ValueError(f"Unknown tool: {name}")

@server.list_resources()
async def list_resources() -> list[types.Resource]:
    return [
        types.Resource(
            uri=types.AnyUrl("data://example"),
            name="Example",
            description="Example resource"
        )
    ]

@server.read_resource()
async def read_resource(uri: types.AnyUrl) -> str | bytes:
    if str(uri) == "data://example":
        return '{"data": "value"}'
    raise ValueError(f"Unknown resource: {uri}")

@server.list_prompts()
async def list_prompts() -> list[types.Prompt]:
    return [
        types.Prompt(
            name="example-prompt",
            description="Example prompt",
            arguments=[
                types.PromptArgument(name="arg1", description="Argument 1", required=True)
            ]
        )
    ]

@server.get_prompt()
async def get_prompt(name: str, arguments: dict | None) -> types.GetPromptResult:
    if name != "example-prompt":
        raise ValueError(f"Unknown prompt: {name}")
    arg1 = (arguments or {}).get("arg1", "default")
    return types.GetPromptResult(
        description="Example prompt",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=f"Prompt with: {arg1}")
            )
        ]
    )

# Run the server
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
    import asyncio
    asyncio.run(run())
```

## Client API

### Stdio Client

```python
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from pydantic import AnyUrl

server_params = StdioServerParameters(
    command="python",
    args=["server.py"],
    env={"KEY": "value"},  # Optional environment
)

async def connect():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List tools
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"Tool: {tool.name}")

            # Call tool
            result = await session.call_tool("tool_name", {"param": "value"})
            # Unstructured content
            if isinstance(result.content[0], types.TextContent):
                print(result.content[0].text)
            # Structured content
            print(result.structuredContent)

            # List resources
            resources = await session.list_resources()

            # Read resource
            content = await session.read_resource(AnyUrl("uri://path"))

            # List resource templates
            templates = await session.list_resource_templates()

            # List prompts
            prompts = await session.list_prompts()

            # Get prompt
            prompt = await session.get_prompt("prompt_name", {"arg": "value"})
```

### HTTP Client

```python
from mcp.client.streamable_http import streamablehttp_client

async def connect():
    async with streamablehttp_client("http://localhost:8000/mcp") as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools = await session.list_tools()
```

### Pagination

```python
from mcp.types import PaginatedRequestParams

async def list_all_resources():
    all_resources = []
    cursor = None

    while True:
        result = await session.list_resources(
            params=PaginatedRequestParams(cursor=cursor)
        )
        all_resources.extend(result.resources)

        if result.nextCursor:
            cursor = result.nextCursor
        else:
            break

    return all_resources
```

## Key Types

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
    AnyUrl,

    # Prompt types
    Prompt,
    PromptMessage,
    PromptArgument,
    GetPromptResult,

    # Pagination
    PaginatedRequestParams,

    # Protocol
    LATEST_PROTOCOL_VERSION,
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
from mcp.server.session import ServerSession

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client
```

## Multiple Servers with Starlette

```python
import contextlib
from starlette.applications import Starlette

api_mcp = FastMCP("API Server")
chat_mcp = FastMCP("Chat Server")

@contextlib.asynccontextmanager
async def lifespan(app: Starlette):
    async with contextlib.AsyncExitStack() as stack:
        await stack.enter_async_context(api_mcp.session_manager.run())
        await stack.enter_async_context(chat_mcp.session_manager.run())
        yield

app = Starlette(lifespan=lifespan)
```

## Experimental: Tasks

```python
from mcp.server import Server
from mcp.server.experimental.task_context import ServerTaskContext
from mcp.types import CallToolResult, TextContent, TASK_REQUIRED, TaskMetadata

server = Server("my-server")
server.experimental.enable_tasks()

@server.call_tool()
async def handle_tool(name: str, arguments: dict):
    ctx = server.request_context
    ctx.experimental.validate_task_mode(TASK_REQUIRED)

    async def work(task: ServerTaskContext):
        await task.update_status("Processing...")
        # ... do work ...
        return CallToolResult(content=[TextContent(type="text", text="Done!")])

    return await ctx.experimental.run_task(work)

# Task metadata with TTL
task = TaskMetadata(ttl=60000)  # TTL in milliseconds
```

## Complete Example: Task Manager Server

```python
"""Complete Task Manager MCP Server"""
from typing import Optional
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
import json

from mcp.server.fastmcp import FastMCP, Context
from mcp.server.session import ServerSession
from sqlmodel import Session, select, create_engine, SQLModel, Field

# Database model
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    title: str
    description: Optional[str] = None
    completed: bool = Field(default=False)

# Database setup
engine = create_engine("sqlite:///tasks.db")

@dataclass
class AppContext:
    engine: any

@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Initialize database on startup."""
    SQLModel.metadata.create_all(engine)
    yield AppContext(engine=engine)

# Create server
mcp = FastMCP(
    "Task Manager",
    instructions="Manage user tasks with CRUD operations",
    lifespan=lifespan
)

@mcp.tool()
def add_task(
    user_id: str,
    title: str,
    description: Optional[str] = None,
    ctx: Context[ServerSession, AppContext] = None
) -> dict:
    """Create a new task for a user."""
    with Session(ctx.request_context.lifespan_context.engine) as session:
        task = Task(user_id=user_id, title=title, description=description)
        session.add(task)
        session.commit()
        session.refresh(task)
        return {"task_id": task.id, "status": "created", "title": task.title}

@mcp.tool()
def list_tasks(
    user_id: str,
    status: str = "all",
    ctx: Context[ServerSession, AppContext] = None
) -> list:
    """List tasks for a user. Status: all, pending, or completed."""
    with Session(ctx.request_context.lifespan_context.engine) as session:
        stmt = select(Task).where(Task.user_id == user_id)
        if status == "pending":
            stmt = stmt.where(Task.completed == False)
        elif status == "completed":
            stmt = stmt.where(Task.completed == True)
        tasks = session.exec(stmt).all()
        return [{"id": t.id, "title": t.title, "completed": t.completed} for t in tasks]

@mcp.tool()
def complete_task(
    user_id: str,
    task_id: int,
    ctx: Context[ServerSession, AppContext] = None
) -> dict:
    """Mark a task as complete."""
    with Session(ctx.request_context.lifespan_context.engine) as session:
        task = session.get(Task, task_id)
        if not task or task.user_id != user_id:
            return {"error": "Task not found"}
        task.completed = True
        session.add(task)
        session.commit()
        return {"task_id": task.id, "status": "completed", "title": task.title}

@mcp.tool()
def delete_task(
    user_id: str,
    task_id: int,
    ctx: Context[ServerSession, AppContext] = None
) -> dict:
    """Delete a task."""
    with Session(ctx.request_context.lifespan_context.engine) as session:
        task = session.get(Task, task_id)
        if not task or task.user_id != user_id:
            return {"error": "Task not found"}
        title = task.title
        session.delete(task)
        session.commit()
        return {"task_id": task_id, "status": "deleted", "title": title}

@mcp.resource("tasks://{user_id}")
def get_tasks_resource(user_id: str) -> str:
    """Get all tasks for a user as a resource."""
    with Session(engine) as session:
        tasks = session.exec(select(Task).where(Task.user_id == user_id)).all()
        return json.dumps([
            {"id": t.id, "title": t.title, "completed": t.completed}
            for t in tasks
        ])

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```
