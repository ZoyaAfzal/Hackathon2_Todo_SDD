# Gemini Agent with Tools Examples

Examples demonstrating tool/function calling with Gemini models in the OpenAI Agents SDK.

## Example 1: Simple Tool

Basic single-parameter tool.

```python
# simple_tool.py
from agents import Agent, Runner, function_tool
from agents.factory import create_model


@function_tool
def get_weather(city: str) -> str:
    """Get current weather for a city.

    Args:
        city: Name of the city to get weather for.

    Returns:
        Weather description string.
    """
    # Mock implementation - replace with real API
    weather_data = {
        "london": "Cloudy, 15°C",
        "tokyo": "Sunny, 22°C",
        "new york": "Rainy, 18°C",
        "paris": "Partly cloudy, 19°C",
    }
    return weather_data.get(city.lower(), f"Weather data not available for {city}")


agent = Agent(
    name="weather-agent",
    model=create_model(),
    instructions="""You are a weather assistant.
    When asked about weather, use the get_weather tool.
    Provide friendly, conversational responses.""",
    tools=[get_weather],
)

# Test the agent
result = Runner.run_sync(agent, "What's the weather like in Tokyo?")
print(result.final_output)
```

## Example 2: Multiple Tools

Agent with several specialized tools.

```python
# multi_tool_agent.py
from datetime import datetime
from agents import Agent, Runner, function_tool
from agents.factory import create_model


@function_tool
def get_current_time() -> str:
    """Get the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@function_tool
def calculate(expression: str) -> str:
    """Calculate a mathematical expression safely.

    Args:
        expression: Math expression to evaluate (e.g., "2 + 2", "12 * 5").

    Returns:
        Result as a string.
    """
    import ast
    import operator
    import math

    # Safe operators for mathematical expressions
    SAFE_OPS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
        ast.Mod: operator.mod,
        ast.FloorDiv: operator.floordiv,
    }

    SAFE_FUNCS = {
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "sqrt": math.sqrt,
        "pow": pow,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "log10": math.log10,
    }

    SAFE_CONSTS = {"pi": math.pi, "e": math.e}

    def safe_eval(node):
        if isinstance(node, ast.Constant):  # Numbers
            return node.value
        elif isinstance(node, ast.BinOp):  # Binary operations
            left = safe_eval(node.left)
            right = safe_eval(node.right)
            op = SAFE_OPS.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
            return op(left, right)
        elif isinstance(node, ast.UnaryOp):  # Unary operations
            operand = safe_eval(node.operand)
            op = SAFE_OPS.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
            return op(operand)
        elif isinstance(node, ast.Call):  # Function calls
            if isinstance(node.func, ast.Name):
                func = SAFE_FUNCS.get(node.func.id)
                if func is None:
                    raise ValueError(f"Unsupported function: {node.func.id}")
                args = [safe_eval(arg) for arg in node.args]
                return func(*args)
            raise ValueError("Invalid function call")
        elif isinstance(node, ast.Name):  # Constants like pi, e
            if node.id in SAFE_CONSTS:
                return SAFE_CONSTS[node.id]
            raise ValueError(f"Unknown variable: {node.id}")
        else:
            raise ValueError(f"Unsupported expression type: {type(node).__name__}")

    try:
        tree = ast.parse(expression, mode="eval")
        result = safe_eval(tree.body)
        return str(result)
    except Exception as e:
        return f"Error: {e}"


@function_tool
def search_knowledge(query: str) -> str:
    """Search internal knowledge base.

    Args:
        query: Search query string.

    Returns:
        Relevant information from knowledge base.
    """
    # Mock knowledge base
    knowledge = {
        "company": "Acme Corp, founded 2020, headquartered in San Francisco",
        "product": "Our main product is WidgetPro, a productivity tool",
        "support": "Contact support at support@acme.com or 1-800-ACME",
    }

    query_lower = query.lower()
    for key, value in knowledge.items():
        if key in query_lower:
            return value

    return "No relevant information found in knowledge base"


agent = Agent(
    name="multi-tool-assistant",
    model=create_model(),
    instructions="""You are a helpful assistant with access to multiple tools.

    Available tools:
    - get_current_time: For time/date queries
    - calculate: For math calculations
    - search_knowledge: For company information

    Choose the appropriate tool based on the user's question.
    Be natural and conversational in your responses.""",
    tools=[get_current_time, calculate, search_knowledge],
)


# Test queries
queries = [
    "What time is it?",
    "Calculate the square root of 144",
    "What's your company's main product?",
]

for query in queries:
    print(f"Q: {query}")
    result = Runner.run_sync(agent, query)
    print(f"A: {result.final_output}\n")
```

## Example 3: Pydantic Model Parameters

Using structured input parameters.

```python
# structured_tools.py
from pydantic import BaseModel, Field
from typing import Optional, Literal
from agents import Agent, Runner, function_tool
from agents.factory import create_model


class TaskCreate(BaseModel):
    """Parameters for creating a task."""
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    priority: Literal["low", "medium", "high"] = Field(
        "medium",
        description="Task priority level"
    )
    due_date: Optional[str] = Field(
        None,
        description="Due date in YYYY-MM-DD format"
    )


class TaskQuery(BaseModel):
    """Parameters for querying tasks."""
    status: Optional[Literal["pending", "completed", "all"]] = Field(
        "all",
        description="Filter by status"
    )
    priority: Optional[Literal["low", "medium", "high"]] = Field(
        None,
        description="Filter by priority"
    )


# Mock database
TASKS = []


@function_tool
def create_task(params: TaskCreate) -> str:
    """Create a new task.

    Args:
        params: Task creation parameters.

    Returns:
        Confirmation message with task ID.
    """
    task_id = len(TASKS) + 1
    task = {
        "id": task_id,
        "title": params.title,
        "description": params.description,
        "priority": params.priority,
        "due_date": params.due_date,
        "status": "pending",
    }
    TASKS.append(task)
    return f"Created task #{task_id}: {params.title} (Priority: {params.priority})"


@function_tool
def list_tasks(params: TaskQuery) -> str:
    """List tasks with optional filters.

    Args:
        params: Query parameters for filtering tasks.

    Returns:
        Formatted list of matching tasks.
    """
    filtered = TASKS.copy()

    if params.status and params.status != "all":
        filtered = [t for t in filtered if t["status"] == params.status]

    if params.priority:
        filtered = [t for t in filtered if t["priority"] == params.priority]

    if not filtered:
        return "No tasks found matching criteria"

    result = []
    for task in filtered:
        result.append(
            f"#{task['id']} [{task['priority']}] {task['title']} - {task['status']}"
        )

    return "\n".join(result)


@function_tool
def complete_task(task_id: int) -> str:
    """Mark a task as completed.

    Args:
        task_id: ID of the task to complete.

    Returns:
        Confirmation message.
    """
    for task in TASKS:
        if task["id"] == task_id:
            task["status"] = "completed"
            return f"Task #{task_id} marked as completed"

    return f"Task #{task_id} not found"


agent = Agent(
    name="task-manager",
    model=create_model(),
    instructions="""You are a task management assistant.

    Help users:
    - Create new tasks with create_task
    - View their tasks with list_tasks
    - Mark tasks done with complete_task

    When creating tasks, ask for details if not provided.
    Be helpful and proactive about task organization.""",
    tools=[create_task, list_tasks, complete_task],
)


# Interactive demo
def demo():
    queries = [
        "Create a task to buy groceries with high priority",
        "Add a task: Review quarterly report, due 2024-12-31",
        "Show me all my tasks",
        "Mark task 1 as done",
        "Show only high priority tasks",
    ]

    for query in queries:
        print(f"\nUser: {query}")
        result = Runner.run_sync(agent, query)
        print(f"Agent: {result.final_output}")


if __name__ == "__main__":
    demo()
```

## Example 4: Async Tools

Tools with async operations.

```python
# async_tools.py
import asyncio
import httpx
from agents import Agent, Runner, function_tool
from agents.factory import create_model


@function_tool
async def fetch_url(url: str) -> str:
    """Fetch content from a URL.

    Args:
        url: URL to fetch.

    Returns:
        First 500 characters of the response.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            content = response.text[:500]
            return f"Status: {response.status_code}\nContent: {content}..."
        except Exception as e:
            return f"Error fetching URL: {e}"


@function_tool
async def parallel_search(queries: list[str]) -> str:
    """Search multiple queries in parallel.

    Args:
        queries: List of search queries.

    Returns:
        Combined results from all queries.
    """
    async def mock_search(query: str) -> str:
        await asyncio.sleep(0.1)  # Simulate API delay
        return f"Results for '{query}': Found 10 items"

    tasks = [mock_search(q) for q in queries]
    results = await asyncio.gather(*tasks)
    return "\n".join(results)


agent = Agent(
    name="async-agent",
    model=create_model(),
    instructions="""You are a research assistant with async capabilities.
    Use fetch_url to get web content.
    Use parallel_search for multiple queries.""",
    tools=[fetch_url, parallel_search],
)


async def main():
    result = await Runner.run(
        agent,
        "Search for these topics in parallel: python, javascript, rust"
    )
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
```

## Example 5: Tool with Context

Tools that access agent context (for ChatKit).

```python
# context_tools.py
from agents import Agent, Runner, function_tool, RunContextWrapper
from chatkit.agents import AgentContext
from chatkit.widgets import ListView, ListViewItem, Text, Row, Badge
from agents.factory import create_model


@function_tool
async def get_user_tasks(
    ctx: RunContextWrapper[AgentContext],
    status_filter: str = "all",
) -> None:
    """Get tasks for the current user and display in widget.

    Args:
        ctx: Agent context with user info.
        status_filter: Filter by 'pending', 'completed', or 'all'.

    Returns:
        None - displays widget directly.
    """
    # Get user from context
    user_id = ctx.context.request_context.get("user_id", "unknown")

    # Mock: fetch tasks from database
    tasks = [
        {"id": 1, "title": "Buy groceries", "status": "pending"},
        {"id": 2, "title": "Review code", "status": "completed"},
        {"id": 3, "title": "Write docs", "status": "pending"},
    ]

    # Filter if needed
    if status_filter != "all":
        tasks = [t for t in tasks if t["status"] == status_filter]

    # Build widget
    items = []
    for task in tasks:
        icon = "checkmark" if task["status"] == "completed" else "circle"
        items.append(
            ListViewItem(
                children=[
                    Row(
                        children=[
                            Text(value=icon),
                            Text(value=task["title"], weight="semibold"),
                            Badge(label=f"#{task['id']}", size="sm"),
                        ],
                        gap=2,
                    )
                ]
            )
        )

    widget = ListView(
        children=items,
        status={"text": f"Tasks ({len(tasks)})", "icon": {"name": "list"}},
    )

    # Stream widget to ChatKit UI
    await ctx.context.stream_widget(widget)


agent = Agent(
    name="chatkit-task-agent",
    model=create_model(),
    instructions="""You are a task assistant in ChatKit.

    IMPORTANT: When get_user_tasks is called, the data displays automatically
    in a widget. DO NOT format the data yourself - just confirm the action.

    Example: "Here are your tasks" or "Showing your pending tasks"
    """,
    tools=[get_user_tasks],
)
```

## Example 6: Tool Error Handling

Graceful error handling in tools.

```python
# error_handling_tools.py
from typing import Optional
from agents import Agent, Runner, function_tool
from agents.factory import create_model


class ToolError(Exception):
    """Custom tool error with user-friendly message."""
    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(message)


@function_tool
def divide_numbers(a: float, b: float) -> str:
    """Divide two numbers.

    Args:
        a: Numerator.
        b: Denominator.

    Returns:
        Result of division.
    """
    if b == 0:
        return "Error: Cannot divide by zero"

    result = a / b
    return f"{a} / {b} = {result}"


@function_tool
def fetch_user_data(user_id: str) -> str:
    """Fetch user data from database.

    Args:
        user_id: User identifier.

    Returns:
        User information or error message.
    """
    # Mock database
    users = {
        "user_1": {"name": "Alice", "email": "alice@example.com"},
        "user_2": {"name": "Bob", "email": "bob@example.com"},
    }

    if user_id not in users:
        return f"Error: User '{user_id}' not found. Available: {list(users.keys())}"

    user = users[user_id]
    return f"User: {user['name']}, Email: {user['email']}"


@function_tool
def risky_operation(value: str) -> str:
    """Perform an operation that might fail.

    Args:
        value: Input value.

    Returns:
        Result or error message.
    """
    try:
        # Simulate risky operation
        if len(value) < 3:
            raise ValueError("Input too short")

        return f"Processed: {value.upper()}"

    except Exception as e:
        return f"Operation failed: {e}. Please try with a longer input."


agent = Agent(
    name="error-aware-agent",
    model=create_model(),
    instructions="""You are a helpful assistant.

    When tools return errors:
    1. Explain the error clearly to the user
    2. Suggest how to fix the issue
    3. Offer alternatives if available

    Never expose technical error details unnecessarily.""",
    tools=[divide_numbers, fetch_user_data, risky_operation],
)


# Test error scenarios
test_cases = [
    "Divide 10 by 0",
    "Get data for user_999",
    "Process the value 'ab'",
]

for test in test_cases:
    print(f"\nQ: {test}")
    result = Runner.run_sync(agent, test)
    print(f"A: {result.final_output}")
```

## Best Practices for Gemini Tool Calling

### 1. Keep Tool Schemas Simple

```python
# Good: Simple, flat parameters
@function_tool
def get_item(item_id: str, include_details: bool = False) -> str:
    """Get item by ID."""
    pass

# Avoid: Complex nested structures
@function_tool
def complex_query(
    filters: dict[str, list[dict[str, str]]]  # Too complex for Gemini
) -> str:
    pass
```

### 2. Write Clear Docstrings

```python
@function_tool
def search_products(
    query: str,
    category: str = "all",
    max_results: int = 10,
) -> str:
    """Search for products in the catalog.

    Use this tool when the user wants to find products.
    The search is case-insensitive and supports partial matches.

    Args:
        query: Search terms (e.g., "blue shirt", "laptop").
        category: Product category filter. Options: "all", "electronics",
                  "clothing", "home". Default is "all".
        max_results: Maximum number of results to return (1-50). Default is 10.

    Returns:
        Formatted list of matching products with prices.
    """
    pass
```

### 3. Add Tool Usage to Instructions

```python
agent = Agent(
    name="guided-agent",
    model=create_model(),
    instructions="""You are a shopping assistant.

    TOOL USAGE GUIDE:
    - search_products: Use for finding items. Always search before recommending.
    - get_product_details: Use when user asks about specific product.
    - check_inventory: Use before confirming availability.

    IMPORTANT: After tool calls, summarize results naturally.
    Do not dump raw data to the user.""",
    tools=[...],
)
```
