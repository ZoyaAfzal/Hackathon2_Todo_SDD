# ChatKit Integration with Gemini Examples

Complete examples for building ChatKit backends powered by Gemini models.

## Example 1: Minimal ChatKit Backend

The simplest ChatKit backend with Gemini.

```python
# main.py
import os
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel

# Initialize FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url=GEMINI_BASE_URL,
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=client,
)

# Create agent
agent = Agent(
    name="chatkit-gemini",
    model=model,
    instructions="You are a helpful assistant. Be concise and friendly.",
)


@app.post("/chatkit/api")
async def chatkit_endpoint(request: Request):
    """Handle ChatKit API requests."""
    event = await request.json()
    user_message = event.get("message", {}).get("content", "")

    # Non-streaming response
    result = Runner.run_sync(agent, user_message)

    return {
        "type": "message",
        "content": result.final_output,
        "done": True,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Example 2: Streaming ChatKit Backend

Real-time streaming responses with Gemini.

```python
# streaming_backend.py
import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini configuration
client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=client)

agent = Agent(
    name="streaming-gemini",
    model=model,
    instructions="You are a helpful assistant. Provide detailed responses.",
)


async def generate_stream(user_message: str):
    """Generate SSE stream from agent response."""
    result = Runner.run_streamed(agent, user_message)

    async for event in result.stream_events():
        if hasattr(event, "data") and hasattr(event.data, "delta"):
            chunk = event.data.delta
            if chunk:
                yield f"data: {json.dumps({'text': chunk})}\n\n"

    # Signal completion
    yield f"data: {json.dumps({'done': True})}\n\n"


@app.post("/chatkit/api")
async def chatkit_streaming(request: Request):
    """Handle ChatKit requests with streaming."""
    event = await request.json()
    user_message = event.get("message", {}).get("content", "")

    return StreamingResponse(
        generate_stream(user_message),
        media_type="text/event-stream",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Example 3: Full ChatKit Server with Tools

Complete ChatKitServer implementation with Gemini and widget streaming.

```python
# chatkit_server.py
import os
from typing import AsyncIterator, Any
from chatkit.server import ChatKitServer, ThreadMetadata, UserMessageItem, ThreadStreamEvent
from chatkit.stores import FileStore
from chatkit.agents import AgentContext, simple_to_agent_input, stream_agent_response
from chatkit.widgets import ListView, ListViewItem, Text, Row, Col, Badge

from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel, function_tool, RunContextWrapper


# Configure Gemini
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url=GEMINI_BASE_URL,
)

model = OpenAIChatCompletionsModel(
    model=os.getenv("GEMINI_DEFAULT_MODEL", "gemini-2.5-flash"),
    openai_client=client,
)


# Define tools with widget streaming
@function_tool
async def list_tasks(
    ctx: RunContextWrapper[AgentContext],
    status: str = "all",
) -> None:
    """List user's tasks with optional status filter.

    Args:
        ctx: Agent context.
        status: Filter by 'pending', 'completed', or 'all'.
    """
    # Get user from context
    user_id = ctx.context.request_context.get("user_id", "guest")

    # Mock: fetch from database
    tasks = [
        {"id": 1, "title": "Review PR #123", "status": "pending", "priority": "high"},
        {"id": 2, "title": "Update docs", "status": "pending", "priority": "medium"},
        {"id": 3, "title": "Fix login bug", "status": "completed", "priority": "high"},
    ]

    # Filter by status
    if status != "all":
        tasks = [t for t in tasks if t["status"] == status]

    # Build widget items
    items = []
    for task in tasks:
        icon = "checkmark.circle.fill" if task["status"] == "completed" else "circle"
        color = "green" if task["status"] == "completed" else "primary"

        items.append(
            ListViewItem(
                children=[
                    Row(
                        children=[
                            Text(value=icon, size="lg"),
                            Col(
                                children=[
                                    Text(
                                        value=task["title"],
                                        weight="semibold",
                                        color=color,
                                        lineThrough=task["status"] == "completed",
                                    ),
                                    Text(
                                        value=f"Priority: {task['priority']}",
                                        size="sm",
                                        color="secondary",
                                    ),
                                ],
                                gap=1,
                            ),
                            Badge(
                                label=f"#{task['id']}",
                                color="secondary",
                                size="sm",
                            ),
                        ],
                        gap=3,
                        align="center",
                    )
                ]
            )
        )

    # Create widget
    widget = ListView(
        children=items if items else [
            ListViewItem(
                children=[Text(value="No tasks found", color="secondary", italic=True)]
            )
        ],
        status={"text": f"Tasks ({len(tasks)})", "icon": {"name": "checklist"}},
        limit="auto",
    )

    # Stream widget to ChatKit
    await ctx.context.stream_widget(widget)


@function_tool
async def add_task(
    ctx: RunContextWrapper[AgentContext],
    title: str,
    priority: str = "medium",
) -> str:
    """Add a new task.

    Args:
        ctx: Agent context.
        title: Task title.
        priority: Task priority (low, medium, high).

    Returns:
        Confirmation message.
    """
    user_id = ctx.context.request_context.get("user_id", "guest")

    # Mock: save to database
    task_id = 4  # Would be from DB

    return f"Created task #{task_id}: '{title}' with {priority} priority"


@function_tool
async def complete_task(
    ctx: RunContextWrapper[AgentContext],
    task_id: int,
) -> str:
    """Mark a task as completed.

    Args:
        ctx: Agent context.
        task_id: ID of task to complete.

    Returns:
        Confirmation message.
    """
    # Mock: update in database
    return f"Task #{task_id} marked as completed"


# Create ChatKit server
class GeminiChatServer(ChatKitServer):
    def __init__(self):
        self.store = FileStore(base_path="./chat_data")
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        return Agent(
            name="gemini-task-assistant",
            model=model,
            instructions="""You are a task management assistant powered by Gemini.

            AVAILABLE TOOLS:
            - list_tasks: Show user's tasks (displays automatically in a widget)
            - add_task: Create a new task
            - complete_task: Mark a task as done

            IMPORTANT RULES:
            1. When list_tasks is called, the data displays automatically in a widget
            2. DO NOT format task data as text/JSON - just say "Here are your tasks"
            3. Be helpful and proactive about task organization
            4. Confirm actions clearly after add_task or complete_task
            """,
            tools=[list_tasks, add_task, complete_task],
        )

    async def respond(
        self,
        thread: ThreadMetadata,
        input: UserMessageItem | None,
        context: Any,
    ) -> AsyncIterator[ThreadStreamEvent]:
        """Process user messages and stream responses."""

        # Create agent context
        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=context,
        )

        # Convert ChatKit input to Agent SDK format
        agent_input = await simple_to_agent_input(input) if input else []

        # Run agent with streaming
        result = Runner.run_streamed(
            self.agent,
            agent_input,
            context=agent_context,
        )

        # Stream response (widgets streamed by tools)
        async for event in stream_agent_response(agent_context, result):
            yield event


# FastAPI integration
from fastapi import FastAPI, Request, Header
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

server = GeminiChatServer()


@app.post("/chatkit/api")
async def chatkit_api(
    request: Request,
    authorization: str = Header(None),
):
    """Handle ChatKit API requests."""
    # Extract user from auth header
    user_id = "guest"
    if authorization:
        # Validate JWT and extract user_id
        # user_id = validate_jwt(authorization)
        pass

    # Parse request
    body = await request.json()

    # Build thread metadata
    thread = ThreadMetadata(
        id=body.get("thread_id", "default"),
        # Additional thread metadata
    )

    # Build input
    input_data = body.get("input")
    input_item = UserMessageItem(
        content=input_data.get("content", ""),
    ) if input_data else None

    # Context for tools
    context = {
        "user_id": user_id,
        "request": request,
    }

    async def generate():
        async for event in server.respond(thread, input_item, context):
            yield f"data: {event.model_dump_json()}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Example 4: Provider-Switchable Backend

Backend that can switch between OpenAI and Gemini.

```python
# switchable_backend.py
import os
from typing import AsyncIterator
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Model factory
def create_model():
    """Create model based on LLM_PROVIDER environment variable."""
    provider = os.getenv("LLM_PROVIDER", "openai").lower()

    if provider == "gemini":
        client = AsyncOpenAI(
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
        return OpenAIChatCompletionsModel(
            model=os.getenv("GEMINI_DEFAULT_MODEL", "gemini-2.5-flash"),
            openai_client=client,
        )

    # Default: OpenAI
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return OpenAIChatCompletionsModel(
        model=os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4o-mini"),
        openai_client=client,
    )


# Create agent
agent = Agent(
    name="switchable-assistant",
    model=create_model(),
    instructions="""You are a helpful assistant.
    Be concise, accurate, and friendly.""",
)


async def stream_response(user_message: str) -> AsyncIterator[str]:
    """Stream agent response as SSE."""
    import json

    result = Runner.run_streamed(agent, user_message)

    async for event in result.stream_events():
        if hasattr(event, "data") and hasattr(event.data, "delta"):
            chunk = event.data.delta
            if chunk:
                yield f"data: {json.dumps({'text': chunk})}\n\n"

    yield f"data: {json.dumps({'done': True})}\n\n"


@app.post("/chatkit/api")
async def chatkit_endpoint(request: Request):
    event = await request.json()
    user_message = event.get("message", {}).get("content", "")

    return StreamingResponse(
        stream_response(user_message),
        media_type="text/event-stream",
    )


@app.get("/health")
async def health():
    provider = os.getenv("LLM_PROVIDER", "openai")
    return {"status": "healthy", "provider": provider}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Usage:
```bash
# Run with Gemini
LLM_PROVIDER=gemini GEMINI_API_KEY=your-key uvicorn switchable_backend:app

# Run with OpenAI
LLM_PROVIDER=openai OPENAI_API_KEY=your-key uvicorn switchable_backend:app
```

## Example 5: Frontend Configuration

Next.js frontend configuration for Gemini backend.

```tsx
// app/chat/page.tsx
"use client";

import { ChatKitWidget } from "@anthropic-ai/chatkit";

export default function ChatPage() {
  return (
    <ChatKitWidget
      config={{
        api: {
          url: "http://localhost:8000/chatkit/api",
          // Custom fetch for authentication
          fetch: async (url, options) => {
            const token = await getAuthToken(); // Your auth logic

            return fetch(url, {
              ...options,
              headers: {
                ...options?.headers,
                Authorization: `Bearer ${token}`,
              },
            });
          },
        },
        // Widget configuration
        theme: "light",
        placeholder: "Ask me anything...",
      }}
    />
  );
}
```

```tsx
// app/layout.tsx
// CRITICAL: Load CDN for widget styling

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        {/* REQUIRED: ChatKit CDN for widget styling */}
        <script
          src="https://cdn.openai.com/chatkit/latest/chatkit.min.js"
          defer
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
```

## Environment Setup

```bash
# .env file for Gemini backend

# Provider selection
LLM_PROVIDER=gemini

# Gemini configuration
GEMINI_API_KEY=your-gemini-api-key
GEMINI_DEFAULT_MODEL=gemini-2.5-flash

# Optional: OpenAI fallback
OPENAI_API_KEY=your-openai-key
OPENAI_DEFAULT_MODEL=gpt-4o-mini

# Server configuration
HOST=0.0.0.0
PORT=8000
```

## Running the Examples

1. Install dependencies:
```bash
pip install fastapi uvicorn openai-agents openai chatkit
```

2. Set environment variables:
```bash
export GEMINI_API_KEY="your-api-key"
export LLM_PROVIDER="gemini"
```

3. Run the server:
```bash
uvicorn chatkit_server:app --reload --port 8000
```

4. Test with curl:
```bash
curl -X POST http://localhost:8000/chatkit/api \
  -H "Content-Type: application/json" \
  -d '{"message": {"content": "Hello!"}}'
```
