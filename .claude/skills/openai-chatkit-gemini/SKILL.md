---
name: openai-chatkit-gemini
description: >
  Integrate Google Gemini models (gemini-2.5-flash, gemini-2.0-flash, etc.) with
  OpenAI Agents SDK and ChatKit. Use this Skill when building ChatKit backends
  powered by Gemini via the OpenAI-compatible endpoint or LiteLLM integration.
---

# OpenAI Agents SDK + Gemini Integration Skill

You are a **Gemini integration specialist** for OpenAI Agents SDK and ChatKit backends.

Your job is to help users integrate **Google Gemini models** with the OpenAI Agents SDK
for use in ChatKit custom backends or standalone agent applications.

## 1. When to Use This Skill

Use this Skill **whenever**:

- The user mentions:
  - "Gemini with Agents SDK"
  - "gemini-2.5-flash" or any Gemini model
  - "ChatKit with Gemini"
  - "non-OpenAI models in Agents SDK"
  - "LiteLLM integration"
  - "OpenAI-compatible endpoint for Gemini"
- Or asks to:
  - Configure Gemini as the model provider for an agent
  - Switch from OpenAI to Gemini in their backend
  - Use Google's AI models with the OpenAI Agents SDK
  - Debug Gemini-related issues in their ChatKit backend

## 2. Integration Methods (Choose One)

There are **two primary methods** to integrate Gemini with OpenAI Agents SDK:

### Method 1: OpenAI-Compatible Endpoint (Recommended)

Uses Google's official OpenAI-compatible API endpoint directly.

**Pros:**
- Direct integration, no extra dependencies
- Full control over configuration
- Works with existing OpenAI SDK patterns

**Base URL:** `https://generativelanguage.googleapis.com/v1beta/openai/`

### Method 2: LiteLLM Integration

Uses LiteLLM as an abstraction layer for 100+ model providers.

**Pros:**
- Easy provider switching
- Consistent interface across providers
- Built-in retry and fallback logic

**Install:** `pip install 'openai-agents[litellm]'`

## 3. Core Architecture

### 3.1 Environment Variables

```text
# Required for Gemini
GEMINI_API_KEY=your-gemini-api-key

# Provider selection
LLM_PROVIDER=gemini

# Model selection
GEMINI_DEFAULT_MODEL=gemini-2.5-flash

# Optional: For LiteLLM method
LITELLM_LOG=DEBUG
```

### 3.2 Model Factory Pattern (MANDATORY)

**ALWAYS use a centralized factory function for model creation:**

```python
# agents/factory.py
import os
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel

# Gemini OpenAI-compatible base URL
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

def create_model():
    """Create model instance based on LLM_PROVIDER environment variable.

    Returns:
        Model instance compatible with OpenAI Agents SDK.
    """
    provider = os.getenv("LLM_PROVIDER", "openai").lower()

    if provider == "gemini":
        return create_gemini_model()

    # Default: OpenAI
    return create_openai_model()


def create_gemini_model(model_name: str | None = None):
    """Create Gemini model via OpenAI-compatible endpoint.

    Args:
        model_name: Gemini model ID. Defaults to GEMINI_DEFAULT_MODEL env var.

    Returns:
        OpenAIChatCompletionsModel configured for Gemini.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required")

    model = model_name or os.getenv("GEMINI_DEFAULT_MODEL", "gemini-2.5-flash")

    client = AsyncOpenAI(
        api_key=api_key,
        base_url=GEMINI_BASE_URL,
    )

    return OpenAIChatCompletionsModel(
        model=model,
        openai_client=client,
    )


def create_openai_model(model_name: str | None = None):
    """Create OpenAI model (default provider).

    Args:
        model_name: OpenAI model ID. Defaults to OPENAI_DEFAULT_MODEL env var.

    Returns:
        OpenAIChatCompletionsModel configured for OpenAI.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")

    model = model_name or os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4o-mini")

    client = AsyncOpenAI(api_key=api_key)

    return OpenAIChatCompletionsModel(
        model=model,
        openai_client=client,
    )
```

### 3.3 LiteLLM Alternative Factory

```python
# agents/factory_litellm.py
import os
from agents.extensions.models.litellm_model import LitellmModel

def create_model():
    """Create model using LiteLLM for provider abstraction."""
    provider = os.getenv("LLM_PROVIDER", "openai").lower()

    if provider == "gemini":
        model_id = os.getenv("GEMINI_DEFAULT_MODEL", "gemini-2.5-flash")
        # LiteLLM format: provider/model
        return LitellmModel(model_id=f"gemini/{model_id}")

    # Default: OpenAI
    model_id = os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4o-mini")
    return LitellmModel(model_id=f"openai/{model_id}")
```

## 4. Supported Gemini Models

| Model ID | Description | Recommended Use |
|----------|-------------|-----------------|
| `gemini-2.5-flash` | Latest fast model | **Default choice** - best speed/quality |
| `gemini-2.5-pro` | Most capable model | Complex reasoning tasks |
| `gemini-2.0-flash` | Previous generation fast | Fallback if 2.5 has issues |
| `gemini-2.0-flash-lite` | Lightweight variant | Cost-sensitive applications |

**IMPORTANT:** Use stable model versions in production. Preview models (e.g.,
`gemini-2.5-flash-preview-05-20`) may have compatibility issues with tool calling.

## 5. Agent Creation with Gemini

### 5.1 Basic Agent

```python
from agents import Agent, Runner
from agents.factory import create_model

agent = Agent(
    name="gemini-assistant",
    model=create_model(),  # Uses factory to get Gemini
    instructions="""You are a helpful assistant powered by Gemini.
    Be concise and accurate in your responses.""",
)

# Synchronous execution
result = Runner.run_sync(starting_agent=agent, input="Hello!")
print(result.final_output)
```

### 5.2 Agent with Tools

```python
from agents import Agent, Runner, function_tool
from agents.factory import create_model

@function_tool
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    # Implementation here
    return f"Weather in {city}: Sunny, 72°F"

agent = Agent(
    name="weather-assistant",
    model=create_model(),
    instructions="""You are a weather assistant.
    Use the get_weather tool when asked about weather.
    IMPORTANT: Do not format tool results as JSON - just describe them naturally.""",
    tools=[get_weather],
)

result = Runner.run_sync(starting_agent=agent, input="What's the weather in Tokyo?")
```

### 5.3 Streaming Agent

```python
import asyncio
from agents import Agent, Runner
from agents.factory import create_model

agent = Agent(
    name="streaming-gemini",
    model=create_model(),
    instructions="You are a helpful assistant. Respond in detail.",
)

async def stream_response(user_input: str):
    result = Runner.run_streamed(agent, user_input)

    async for event in result.stream_events():
        if hasattr(event, 'data') and hasattr(event.data, 'delta'):
            print(event.data.delta, end="", flush=True)

    print()  # Newline at end
    return await result.final_output

asyncio.run(stream_response("Explain quantum computing"))
```

## 6. ChatKit Integration with Gemini

### 6.1 ChatKitServer with Gemini

```python
# server.py
from chatkit.server import ChatKitServer
from chatkit.stores import FileStore
from chatkit.agents import AgentContext, simple_to_agent_input, stream_agent_response
from agents import Agent, Runner
from agents.factory import create_model

class GeminiChatServer(ChatKitServer):
    def __init__(self):
        self.store = FileStore(base_path="./chat_data")
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        return Agent(
            name="gemini-chatkit-agent",
            model=create_model(),  # Gemini via factory
            instructions="""You are a helpful assistant in a ChatKit interface.
            Keep responses concise and user-friendly.
            When tools return data, DO NOT reformat it - it displays automatically.""",
            tools=[...],  # Your MCP tools
        )

    async def respond(self, thread, input, context):
        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=context,
        )

        agent_input = await simple_to_agent_input(input) if input else []

        result = Runner.run_streamed(
            self.agent,
            agent_input,
            context=agent_context,
        )

        async for event in stream_agent_response(agent_context, result):
            yield event
```

### 6.2 FastAPI Endpoint

```python
# main.py
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from server import GeminiChatServer

app = FastAPI()
server = GeminiChatServer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chatkit/api")
async def chatkit_api(request: Request):
    # Auth validation here
    body = await request.json()
    thread_id = body.get("thread_id", "default")
    user_message = body.get("message", {}).get("content", "")

    # Build thread and input objects
    from chatkit.server import ThreadMetadata, UserMessageItem
    thread = ThreadMetadata(id=thread_id)
    input_item = UserMessageItem(content=user_message) if user_message else None
    context = {"user_id": "guest"}  # Add auth context here

    async def generate():
        async for event in server.respond(thread, input_item, context):
            yield f"data: {event.model_dump_json()}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

## 7. Known Issues & Workarounds

### 7.1 AttributeError with Tools (Fixed in SDK)

**Issue:** Some Gemini preview models return `None` for `choices[0].message`
when tools are specified, causing `AttributeError`.

**Affected Models:** `gemini-2.5-flash-preview-05-20` and similar previews

**Solution:**
1. Use stable model versions (e.g., `gemini-2.5-flash` without preview suffix)
2. Update to latest `openai-agents` package (fix merged in PR #746)

### 7.2 Structured Output Limitations

**Issue:** Gemini may not fully support `response_format` with `json_schema`.

**Solution:** Use instruction-based JSON formatting instead:

```python
agent = Agent(
    name="json-agent",
    model=create_model(),
    instructions="""Always respond with valid JSON in this format:
    {"result": "your answer", "confidence": 0.0-1.0}
    Do not include any text outside the JSON object.""",
)
```

### 7.3 Tool Calling Differences

**Issue:** Gemini's tool calling may behave slightly differently than OpenAI's.

**Best Practices:**
- Keep tool descriptions clear and concise
- Avoid complex nested parameter schemas
- Test tools thoroughly with Gemini before production
- Add explicit instructions about tool usage in agent instructions

## 8. Debugging Guide

### 8.1 Connection Issues

```python
# Test Gemini connection
import os
from openai import AsyncOpenAI
import asyncio

async def test_gemini():
    client = AsyncOpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

    response = await client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[{"role": "user", "content": "Hello!"}],
    )
    print(response.choices[0].message.content)

asyncio.run(test_gemini())
```

### 8.2 Common Error Messages

| Error | Cause | Fix |
|-------|-------|-----|
| `401 Unauthorized` | Invalid API key | Check GEMINI_API_KEY |
| `404 Not Found` | Wrong model name | Use valid model ID |
| `AttributeError: 'NoneType'...` | Preview model issue | Use stable model |
| `response_format` error | Structured output unsupported | Remove json_schema |

### 8.3 Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# For LiteLLM
import os
os.environ["LITELLM_LOG"] = "DEBUG"
```

## 9. Best Practices

1. **Always use the factory pattern** - Never hardcode model configuration
2. **Use stable model versions** - Avoid preview/experimental models in production
3. **Handle provider switching** - Design for easy OpenAI/Gemini switching
4. **Test tool calling** - Verify tools work correctly with Gemini
5. **Monitor rate limits** - Gemini has different quotas than OpenAI
6. **Keep SDK updated** - New fixes for Gemini compatibility are released regularly

## 10. Quick Reference

### Environment Setup

```bash
# .env file
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-api-key
GEMINI_DEFAULT_MODEL=gemini-2.5-flash
```

### Minimal Agent

```python
from agents import Agent, Runner
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel

client = AsyncOpenAI(
    api_key="your-gemini-api-key",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

agent = Agent(
    name="gemini-agent",
    model=OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=client),
    instructions="You are a helpful assistant.",
)

result = Runner.run_sync(agent, "Hello!")
print(result.final_output)
```

## 11. Related Skills

- `openai-chatkit-backend-python` - Full ChatKit backend patterns
- `openai-chatkit-frontend-embed-skill` - Frontend widget integration
- `fastapi` - Backend framework patterns
