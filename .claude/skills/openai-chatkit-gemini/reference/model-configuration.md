# Gemini Model Configuration Reference

This reference documents all configuration options for integrating Google Gemini
models with the OpenAI Agents SDK.

## 1. OpenAI-Compatible Endpoint Configuration

### 1.1 Base URL

```python
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
```

This is Google's official OpenAI-compatible endpoint that translates OpenAI API
calls to Gemini API calls.

### 1.2 Client Configuration

```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
```

### 1.3 Model Configuration

```python
from agents import OpenAIChatCompletionsModel

model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=client,
)
```

## 2. Available Gemini Models

### 2.1 Production Models

| Model ID | Context Window | Best For |
|----------|----------------|----------|
| `gemini-2.5-flash` | 1M tokens | Fast responses, general tasks |
| `gemini-2.5-pro` | 1M tokens | Complex reasoning, analysis |
| `gemini-2.0-flash` | 1M tokens | Balanced speed/quality |
| `gemini-2.0-flash-lite` | 1M tokens | Cost optimization |

### 2.2 Model Selection Guidelines

**Use `gemini-2.5-flash` when:**
- Speed is important
- General-purpose chat/assistant tasks
- High volume applications
- Default choice for most use cases

**Use `gemini-2.5-pro` when:**
- Complex multi-step reasoning required
- Code generation/review tasks
- Detailed analysis needed
- Quality is more important than speed

**Use `gemini-2.0-flash` when:**
- Need proven stability
- Fallback from 2.5 models
- Legacy compatibility required

## 3. API Key Configuration

### 3.1 Getting a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API key" in the sidebar
4. Create a new API key or use existing one
5. Copy the key to your environment

### 3.2 Environment Variable Setup

```bash
# .env file
GEMINI_API_KEY=AIzaSy...your-key-here

# Or export directly
export GEMINI_API_KEY="AIzaSy...your-key-here"
```

### 3.3 Secure Key Management

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gemini_api_key: str
    gemini_default_model: str = "gemini-2.5-flash"
    llm_provider: str = "gemini"

    model_config = {"env_file": ".env"}
```

## 4. Rate Limits and Quotas

### 4.1 Free Tier Limits

| Metric | Limit |
|--------|-------|
| Requests per minute | 15 |
| Tokens per minute | 1,000,000 |
| Requests per day | 1,500 |

### 4.2 Paid Tier Limits

| Metric | Limit |
|--------|-------|
| Requests per minute | 1,000+ |
| Tokens per minute | 4,000,000+ |
| Requests per day | Unlimited |

### 4.3 Handling Rate Limits

```python
import asyncio
from openai import RateLimitError

async def call_with_retry(agent, input, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await Runner.run(agent, input)
        except RateLimitError:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                await asyncio.sleep(wait_time)
            else:
                raise
```

## 5. Request Configuration

### 5.1 Temperature and Sampling

```python
from agents import Agent, ModelSettings

agent = Agent(
    name="creative-gemini",
    model=create_model(),
    model_settings=ModelSettings(
        temperature=0.7,      # 0.0-2.0, higher = more creative
        top_p=0.95,           # Nucleus sampling
        max_tokens=4096,      # Maximum response length
    ),
    instructions="...",
)
```

### 5.2 Common Temperature Settings

| Use Case | Temperature | Notes |
|----------|-------------|-------|
| Factual Q&A | 0.0-0.3 | Deterministic responses |
| General chat | 0.5-0.7 | Balanced creativity |
| Creative writing | 0.8-1.0 | More varied responses |
| Brainstorming | 1.0-1.5 | Maximum creativity |

## 6. Tool Calling Configuration

### 6.1 Basic Tool Definition

```python
from agents import function_tool
from pydantic import BaseModel

class SearchParams(BaseModel):
    query: str
    max_results: int = 10

@function_tool
def search_database(params: SearchParams) -> list[dict]:
    """Search the database for matching records.

    Args:
        params: Search parameters including query and max results.

    Returns:
        List of matching records.
    """
    # Implementation
    return [{"id": 1, "title": "Result 1"}]
```

### 6.2 Tool Calling Best Practices for Gemini

```python
# Good: Simple, flat parameter schema
@function_tool
def get_user(user_id: str) -> dict:
    """Get user by ID."""
    pass

# Avoid: Complex nested schemas
@function_tool
def complex_operation(
    config: dict[str, dict[str, list[str]]]  # Too complex
) -> dict:
    """This may not work well with Gemini."""
    pass
```

### 6.3 Agent Instructions for Tools

```python
agent = Agent(
    name="tool-using-agent",
    model=create_model(),
    instructions="""You are a helpful assistant with tool access.

    TOOL USAGE RULES:
    1. Use tools when they can help answer the user's question
    2. Do NOT reformat or display tool results - they render automatically
    3. After a tool call, provide a brief natural language summary
    4. If a tool fails, explain what went wrong and try alternatives
    """,
    tools=[tool1, tool2, tool3],
)
```

## 7. Streaming Configuration

### 7.1 Enable Streaming

```python
from agents import Agent, Runner

agent = Agent(
    name="streaming-agent",
    model=create_model(),
    instructions="...",
)

async def stream():
    result = Runner.run_streamed(agent, "Tell me a story")

    async for event in result.stream_events():
        if hasattr(event, 'data'):
            if hasattr(event.data, 'delta'):
                yield event.data.delta
```

### 7.2 SSE Format for ChatKit

```python
async def sse_generator(agent, user_input):
    result = Runner.run_streamed(agent, user_input)

    async for event in result.stream_events():
        if hasattr(event, 'data') and hasattr(event.data, 'delta'):
            chunk = event.data.delta
            yield f"data: {json.dumps({'text': chunk})}\n\n"

    yield f"data: {json.dumps({'done': True})}\n\n"
```

## 8. Error Handling

### 8.1 Common Errors

```python
from openai import (
    APIError,
    AuthenticationError,
    RateLimitError,
    APIConnectionError,
)

async def safe_agent_call(agent, input):
    try:
        return await Runner.run(agent, input)

    except AuthenticationError:
        # Invalid API key
        raise ValueError("Invalid GEMINI_API_KEY")

    except RateLimitError:
        # Quota exceeded
        raise ValueError("Rate limit exceeded, try again later")

    except APIConnectionError:
        # Network issues
        raise ValueError("Cannot connect to Gemini API")

    except APIError as e:
        # Other API errors
        raise ValueError(f"Gemini API error: {e}")
```

### 8.2 Content Filter Handling

Gemini may filter content for safety. Handle this gracefully:

```python
async def handle_filtered_response(result):
    if result.final_output is None or result.final_output == "":
        return "I'm unable to respond to that request. Please try rephrasing."
    return result.final_output
```

## 9. Performance Optimization

### 9.1 Connection Pooling

```python
# Create client once, reuse across requests
_gemini_client = None

def get_gemini_client():
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = AsyncOpenAI(
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url=GEMINI_BASE_URL,
        )
    return _gemini_client
```

### 9.2 Caching Strategies

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_model_config(model_name: str):
    """Cache model configuration to avoid repeated setup."""
    return OpenAIChatCompletionsModel(
        model=model_name,
        openai_client=get_gemini_client(),
    )
```

## 10. Comparison: Gemini vs OpenAI

| Feature | Gemini | OpenAI |
|---------|--------|--------|
| Context window | 1M tokens | 128K tokens |
| Streaming | Yes | Yes |
| Tool calling | Yes (some differences) | Yes |
| JSON mode | Limited | Full support |
| Vision | Yes | Yes |
| Code execution | Via tools | Via tools |
| Price | Generally lower | Higher |

## 11. Migration Guide

### 11.1 From OpenAI to Gemini

```python
# Before (OpenAI)
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = OpenAIChatCompletionsModel(model="gpt-4o-mini", openai_client=client)

# After (Gemini)
client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
model = OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=client)

# Agent code remains unchanged!
agent = Agent(name="my-agent", model=model, instructions="...")
```

### 11.2 Factory Pattern for Easy Switching

```python
def create_model():
    provider = os.getenv("LLM_PROVIDER", "openai")

    if provider == "gemini":
        return create_gemini_model()
    return create_openai_model()

# Usage - switch by changing LLM_PROVIDER env var
agent = Agent(name="my-agent", model=create_model(), instructions="...")
```
