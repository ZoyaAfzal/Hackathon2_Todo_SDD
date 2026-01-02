# Gemini Integration Troubleshooting Guide

Common issues and solutions when integrating Gemini with OpenAI Agents SDK.

## 1. Connection Issues

### 1.1 Authentication Errors

**Error:** `401 Unauthorized` or `AuthenticationError`

**Causes:**
- Invalid or missing API key
- Expired API key
- Wrong environment variable name

**Solutions:**

```bash
# Verify API key is set
echo $GEMINI_API_KEY

# Test API key directly
curl "https://generativelanguage.googleapis.com/v1beta/openai/models" \
  -H "Authorization: Bearer $GEMINI_API_KEY"
```

```python
# Verify in code
import os
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not set")
print(f"Key starts with: {api_key[:10]}...")
```

### 1.2 Connection Refused

**Error:** `APIConnectionError` or `Connection refused`

**Causes:**
- Network issues
- Firewall blocking requests
- Wrong base URL

**Solutions:**

```python
# Verify base URL is correct
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
# Note: trailing slash is important!

# Test connectivity
import httpx
response = httpx.get(
    "https://generativelanguage.googleapis.com/v1beta/openai/models",
    headers={"Authorization": f"Bearer {api_key}"}
)
print(response.status_code)
```

### 1.3 Timeout Errors

**Error:** `ReadTimeout` or `ConnectTimeout`

**Solutions:**

```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url=GEMINI_BASE_URL,
    timeout=60.0,  # Increase timeout
)
```

## 2. Model Errors

### 2.1 Model Not Found

**Error:** `404 Not Found` or `Model not found`

**Causes:**
- Incorrect model name
- Model not available in your region
- Typo in model ID

**Solutions:**

```python
# Correct model names
VALID_MODELS = [
    "gemini-2.5-flash",      # Correct
    "gemini-2.5-pro",        # Correct
    "gemini-2.0-flash",      # Correct
    # "gemini-flash-2.5",    # WRONG - incorrect format
    # "gemini/2.5-flash",    # WRONG - this is LiteLLM format
]

# List available models
async def list_models():
    client = AsyncOpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url=GEMINI_BASE_URL,
    )
    models = await client.models.list()
    for model in models.data:
        print(model.id)
```

### 2.2 AttributeError with Tools

**Error:** `AttributeError: 'NoneType' object has no attribute 'model_dump'`

**Cause:** Some Gemini preview models return `None` for message when tools are specified.

**Solutions:**

1. Use stable model versions:
```python
# Use this (stable)
model = "gemini-2.5-flash"

# Avoid this (preview)
model = "gemini-2.5-flash-preview-05-20"
```

2. Update the SDK:
```bash
pip install --upgrade openai-agents
```

3. Add error handling:
```python
async def safe_run(agent, input):
    try:
        result = await Runner.run(agent, input)
        if result.final_output is None:
            return "I couldn't generate a response. Please try again."
        return result.final_output
    except AttributeError:
        return "Response was filtered. Please rephrase your request."
```

## 3. Tool Calling Issues

### 3.1 Tools Not Being Called

**Symptoms:**
- Agent ignores tools and responds with text only
- Tool calls not appearing in response

**Solutions:**

1. Improve tool descriptions:
```python
@function_tool
def get_weather(city: str) -> str:
    """Get current weather for a city.

    IMPORTANT: Always use this tool when asked about weather.
    Do not guess or make up weather information.

    Args:
        city: City name (e.g., "London", "Tokyo", "New York").

    Returns:
        Current weather conditions and temperature.
    """
    pass
```

2. Update agent instructions:
```python
agent = Agent(
    name="weather-agent",
    model=create_model(),
    instructions="""You are a weather assistant.

    TOOL USAGE RULES:
    1. ALWAYS use get_weather when asked about weather
    2. NEVER make up weather data
    3. If unsure about city name, ask for clarification

    When asked about weather, your FIRST action should be calling get_weather.
    """,
    tools=[get_weather],
)
```

### 3.2 Tool Parameters Not Parsed Correctly

**Symptoms:**
- Tool receives wrong parameter types
- Missing required parameters

**Solutions:**

1. Simplify parameter schemas:
```python
# Good: Simple types
@function_tool
def search(query: str, limit: int = 10) -> str:
    pass

# Avoid: Complex nested types
@function_tool
def search(filters: dict[str, list[str]]) -> str:  # Too complex
    pass
```

2. Use Pydantic for validation:
```python
from pydantic import BaseModel, Field

class SearchParams(BaseModel):
    query: str = Field(..., description="Search query")
    limit: int = Field(10, ge=1, le=100, description="Max results")

@function_tool
def search(params: SearchParams) -> str:
    # Pydantic ensures valid params
    pass
```

### 3.3 Tool Output Not Displayed

**Symptoms:**
- Agent says "Here are your tasks" but no widget appears
- Tool runs but output is lost

**Solutions for ChatKit:**

1. Ensure widget streaming:
```python
@function_tool
async def list_items(ctx: RunContextWrapper[AgentContext]) -> None:
    # Create widget
    widget = ListView(...)

    # CRITICAL: Stream widget
    await ctx.context.stream_widget(widget)

    # Return None - widget already sent
```

2. Check frontend CDN:
```html
<!-- REQUIRED in layout.tsx -->
<script src="https://cdn.openai.com/chatkit/latest/chatkit.min.js" defer />
```

## 4. Streaming Issues

### 4.1 Streaming Not Working

**Symptoms:**
- Response arrives all at once
- No incremental updates

**Solutions:**

1. Use `run_streamed` not `run_sync`:
```python
# Wrong
result = Runner.run_sync(agent, input)

# Correct for streaming
result = Runner.run_streamed(agent, input)
async for event in result.stream_events():
    # Process events
    pass
```

2. Check SSE format:
```python
async def generate():
    result = Runner.run_streamed(agent, input)
    async for event in result.stream_events():
        if hasattr(event, 'data') and hasattr(event.data, 'delta'):
            # Must be valid SSE format
            yield f"data: {json.dumps({'text': event.data.delta})}\n\n"
```

### 4.2 Partial Responses

**Symptoms:**
- Response cuts off mid-sentence
- Incomplete streaming

**Solutions:**

```python
# Ensure final event is sent
async def generate():
    result = Runner.run_streamed(agent, input)

    async for event in result.stream_events():
        yield f"data: {json.dumps({'text': event.data.delta})}\n\n"

    # IMPORTANT: Signal completion
    yield f"data: {json.dumps({'done': True})}\n\n"
```

## 5. Rate Limiting

### 5.1 Rate Limit Errors

**Error:** `429 Too Many Requests` or `RateLimitError`

**Solutions:**

1. Implement retry logic:
```python
import asyncio
from openai import RateLimitError

async def call_with_backoff(agent, input, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await Runner.run(agent, input)
        except RateLimitError:
            if attempt < max_retries - 1:
                wait = 2 ** attempt  # 1, 2, 4 seconds
                await asyncio.sleep(wait)
            else:
                raise
```

2. Use connection pooling:
```python
# Create client once, reuse
_client = None

def get_client():
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url=GEMINI_BASE_URL,
        )
    return _client
```

## 6. Content Filtering

### 6.1 Responses Being Filtered

**Symptoms:**
- Empty responses
- `finish_reason: content_filter`

**Solutions:**

1. Handle filtered responses:
```python
async def safe_generate(agent, input):
    result = await Runner.run(agent, input)

    if not result.final_output:
        return "I'm unable to respond to that. Please rephrase your question."

    return result.final_output
```

2. Adjust content in instructions:
```python
agent = Agent(
    instructions="""You are a helpful assistant.

    CONTENT GUIDELINES:
    - Provide factual, helpful information
    - Avoid controversial topics
    - Keep responses professional
    """,
)
```

## 7. Debugging Tips

### 7.1 Enable Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# For more verbose output
logging.getLogger("openai").setLevel(logging.DEBUG)
logging.getLogger("httpx").setLevel(logging.DEBUG)
```

### 7.2 Test Connection Independently

```python
# test_gemini.py
import os
import asyncio
from openai import AsyncOpenAI

async def test():
    client = AsyncOpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

    # Test basic completion
    response = await client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[{"role": "user", "content": "Say hello"}],
    )
    print(f"Basic: {response.choices[0].message.content}")

    # Test streaming
    print("Streaming: ", end="")
    stream = await client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[{"role": "user", "content": "Count to 3"}],
        stream=True,
    )
    async for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="")
    print()

asyncio.run(test())
```

### 7.3 Inspect Raw API Responses

```python
import httpx

async def debug_request():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('GEMINI_API_KEY')}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gemini-2.5-flash",
                "messages": [{"role": "user", "content": "Hi"}],
            },
        )
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Body: {response.text}")
```

## 8. Quick Diagnostic Checklist

Run through this checklist when debugging:

- [ ] API key is set: `echo $GEMINI_API_KEY`
- [ ] Base URL is correct (with trailing slash)
- [ ] Model name is valid (e.g., `gemini-2.5-flash`)
- [ ] Using stable model version (not preview)
- [ ] SDK is up to date: `pip install --upgrade openai-agents`
- [ ] Network connectivity: Can reach Google APIs
- [ ] Rate limits: Not exceeded quotas
- [ ] For ChatKit: CDN script loaded in frontend
- [ ] For tools: `ctx.context.stream_widget()` called
- [ ] For streaming: Using `run_streamed` not `run_sync`
