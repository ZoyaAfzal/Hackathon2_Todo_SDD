# OpenAI Agents SDK Reference

This document provides detailed reference for the OpenAI Agents SDK (`openai-agents` package) used in ChatKit backends.

## Installation

```bash
pip install openai-agents
```

## Core Components

### 1. Agent Class

```python
from agents import Agent

agent = Agent(
    name="my-agent",           # Required: Agent identifier
    model=create_model(),      # Required: Model instance
    instructions="...",        # Required: System prompt
    tools=[tool1, tool2],      # Optional: List of tools
)
```

### 2. Function Tool Decorator

The `@function_tool` decorator converts Python functions into tools the agent can use.

```python
from agents import function_tool

@function_tool
def my_tool(param1: str, param2: int = 10) -> dict:
    """Tool description for the AI.

    Args:
        param1: Description of param1
        param2: Description of param2 (default: 10)

    Returns:
        Result dictionary
    """
    return {"result": f"Processed {param1} with {param2}"}
```

**Important:**
- Docstring becomes the tool description for the AI
- Type hints are required for parameters
- Return type should be serializable (dict, str, list, etc.)

### 3. Tools with Context

For tools that need access to the agent context (e.g., for streaming widgets):

```python
from agents import function_tool, RunContextWrapper

@function_tool
async def tool_with_context(
    ctx: RunContextWrapper[AgentContext],  # Context parameter
    user_id: str,
    query: str,
) -> str:
    """Tool that accesses context."""
    # Access the agent context
    agent_context = ctx.context

    # Stream a widget (for ChatKit)
    await agent_context.stream_widget(widget)

    return "Done"
```

**Context Parameter Rules:**
- Must be first parameter after `self` (if any)
- Type hint must be `RunContextWrapper[YourContextType]`
- Not visible to the AI (excluded from tool schema)

### 4. Runner Class

The Runner executes agents and manages the conversation flow.

#### Asynchronous Execution (Primary Method)

```python
from agents import Runner

result = await Runner.run(
    starting_agent=agent,
    input="User message here",
    context=agent_context,  # Optional context
)

# Access the result
print(result.final_output)  # The agent's final text response
```

**Note:** `Runner.run()` is async. There is no `run_sync()` method - use `asyncio.run()` if you need synchronous execution:

```python
import asyncio

async def main():
    result = await Runner.run(agent, "User message")
    return result.final_output

output = asyncio.run(main())
```

#### Streaming Execution (CRITICAL for Phase III)

```python
from agents import Runner

# Get a streaming result object
result = Runner.run_streamed(
    starting_agent=agent,
    input=agent_input,
    context=agent_context,
)

# Stream events as they occur
async for event in result.stream_events():
    if event.type == "raw_response_event":
        # Handle streaming text chunks
        pass
    elif event.type == "run_item_stream_event":
        # Handle tool calls, etc.
        pass
```

### 5. Result Object

```python
result = Runner.run_sync(agent, input)

# Properties
result.final_output    # str: The agent's final text response
result.last_agent      # Agent: The last agent that ran (for multi-agent)
result.new_items       # list: Items produced during the run
result.input_guardrail_results   # Guardrail check results
result.output_guardrail_results  # Guardrail check results
```

### 6. Model Factory Pattern

```python
# agents/factory.py
import os
from agents import OpenAIChatCompletionsModel, AsyncOpenAI

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
        model=os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4.1-mini"),
        openai_client=client,
    )
```

## Phase III Integration Pattern

### Complete ChatKit + Agents SDK Integration

```python
from agents import Agent, Runner, function_tool, RunContextWrapper
from chatkit.agents import AgentContext, simple_to_agent_input, stream_agent_response
from chatkit.widgets import ListView, ListViewItem, Text

# 1. Define MCP-style tools with context
@function_tool
async def list_tasks(
    ctx: RunContextWrapper[AgentContext],
    user_id: str,
    status: str = "all",
) -> None:
    """List tasks for a user.

    Args:
        user_id: The user's ID
        status: Filter - "all", "pending", or "completed"
    """
    # Fetch tasks from database
    tasks = await fetch_tasks_from_db(user_id, status)

    # Create widget
    widget = create_task_list_widget(tasks)

    # Stream widget to ChatKit UI
    await ctx.context.stream_widget(widget)

    # Return None - widget is already streamed


@function_tool
async def add_task(
    ctx: RunContextWrapper[AgentContext],
    user_id: str,
    title: str,
    description: str = None,
) -> dict:
    """Create a new task.

    Args:
        user_id: The user's ID
        title: Task title
        description: Optional description
    """
    task = await create_task_in_db(user_id, title, description)
    return {"task_id": task.id, "status": "created", "title": task.title}


# 2. Create agent with tools
def create_task_agent():
    return Agent(
        name="task-assistant",
        model=create_model(),
        instructions="""You are a helpful task management assistant.

Use the available tools to help users manage their tasks:
- list_tasks: Show user's tasks
- add_task: Create a new task
- complete_task: Mark a task as done
- delete_task: Remove a task
- update_task: Modify a task

IMPORTANT: When tools like list_tasks are called, DO NOT format or display
the data yourself. Simply say "Here are your tasks" or similar brief
acknowledgment. The data will be displayed automatically in a widget.

Always confirm actions with a friendly response.""",
        tools=[list_tasks, add_task, complete_task, delete_task, update_task],
    )


# 3. ChatKitServer respond method
async def respond(
    self,
    thread: ThreadMetadata,
    input: UserMessageItem | None,
    context: Any,
):
    """Process user messages and stream responses."""

    # Create agent context
    agent_context = AgentContext(
        thread=thread,
        store=self.store,
        request_context=context,
    )

    # Convert ChatKit input to Agent SDK format
    agent_input = await simple_to_agent_input(input) if input else []

    # Run agent with streaming (CRITICAL: use run_streamed, NOT run_sync)
    result = Runner.run_streamed(
        self.agent,
        agent_input,
        context=agent_context,
    )

    # Stream agent response (widgets are streamed separately by tools)
    async for event in stream_agent_response(agent_context, result):
        yield event
```

## Key Patterns for Phase III

### 1. Stateless Architecture

```python
# Each request must be independent
async def handle_chat(user_id: str, message: str, conversation_id: int):
    # 1. Fetch conversation history from DB
    history = await get_conversation_history(conversation_id)

    # 2. Store user message BEFORE agent runs
    await store_message(conversation_id, "user", message)

    # 3. Run agent with history
    agent_input = format_history(history) + [{"role": "user", "content": message}]
    result = Runner.run_streamed(agent, agent_input, context=ctx)

    # 4. Collect response
    response = await collect_response(result)

    # 5. Store assistant response AFTER completion
    await store_message(conversation_id, "assistant", response)

    # 6. Return (server holds NO state)
    return response
```

### 2. Widget Streaming vs Text Response

```python
# WRONG: Agent outputs widget data as text
@function_tool
def list_tasks(user_id: str) -> str:
    tasks = get_tasks(user_id)
    return json.dumps(tasks)  # Agent will try to format this!

# CORRECT: Tool streams widget directly
@function_tool
async def list_tasks(
    ctx: RunContextWrapper[AgentContext],
    user_id: str,
) -> None:
    tasks = get_tasks(user_id)
    widget = create_widget(tasks)
    await ctx.context.stream_widget(widget)
    # Return None - agent just confirms action
```

### 3. Error Handling in Tools

```python
@function_tool
async def complete_task(
    ctx: RunContextWrapper[AgentContext],
    user_id: str,
    task_id: int,
) -> dict:
    """Mark a task as complete."""
    try:
        task = await get_task(task_id)
        if not task:
            return {"error": "Task not found", "task_id": task_id}
        if task.user_id != user_id:
            return {"error": "Unauthorized", "task_id": task_id}

        task.completed = True
        await save_task(task)
        return {"task_id": task_id, "status": "completed", "title": task.title}

    except Exception as e:
        return {"error": str(e), "task_id": task_id}
```

## Debugging Tips

| Issue | Solution |
|-------|----------|
| Tool not being called | Check docstring - it must describe what the tool does |
| Agent outputs JSON | Update agent instructions to NOT format tool data |
| Streaming not working | Use `Runner.run_streamed()` not `run_sync()` |
| Context not available | Add `ctx: RunContextWrapper[AgentContext]` parameter |
| Widgets not rendering | Check `await ctx.context.stream_widget(widget)` |
| Type errors | Ensure all tool parameters have type hints |

## Environment Variables

```bash
# Provider selection
LLM_PROVIDER=openai  # or "gemini"

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_DEFAULT_MODEL=gpt-4.1-mini

# Gemini (via OpenAI-compatible endpoint)
GEMINI_API_KEY=...
GEMINI_DEFAULT_MODEL=gemini-2.5-flash
```
