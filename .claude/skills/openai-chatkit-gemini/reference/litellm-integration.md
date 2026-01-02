# LiteLLM Integration Reference

This reference documents how to use LiteLLM to integrate Gemini (and other providers)
with the OpenAI Agents SDK.

## 1. Overview

LiteLLM is an abstraction layer that provides a unified interface for 100+ LLM providers.
The OpenAI Agents SDK has built-in support for LiteLLM via `LitellmModel`.

### 1.1 Why Use LiteLLM?

- **Provider Agnostic**: Same code works with OpenAI, Gemini, Claude, etc.
- **Easy Switching**: Change providers via environment variable
- **Built-in Features**: Retry logic, fallbacks, caching
- **Consistent API**: Unified interface regardless of provider

## 2. Installation

```bash
# Install openai-agents with LiteLLM support
pip install 'openai-agents[litellm]'

# Or with poetry
poetry add 'openai-agents[litellm]'

# Or with uv
uv add 'openai-agents[litellm]'
```

## 3. Basic Usage

### 3.1 Simple Agent with LiteLLM

```python
from agents import Agent, Runner
from agents.extensions.models.litellm_model import LitellmModel

# Create Gemini model via LiteLLM
model = LitellmModel(model_id="gemini/gemini-2.5-flash")

agent = Agent(
    name="gemini-litellm-agent",
    model=model,
    instructions="You are a helpful assistant.",
)

result = Runner.run_sync(agent, "Hello!")
print(result.final_output)
```

### 3.2 Model ID Format

LiteLLM uses the format `provider/model-name`:

```python
# Gemini models
"gemini/gemini-2.5-flash"
"gemini/gemini-2.5-pro"
"gemini/gemini-2.0-flash"

# OpenAI models
"openai/gpt-4o-mini"
"openai/gpt-4.1"
"openai/gpt-4o"

# Anthropic models
"anthropic/claude-3-5-sonnet-20241022"
"anthropic/claude-3-opus-20240229"

# Other providers
"deepseek/deepseek-chat"
"perplexity/llama-3.1-sonar-large-128k-online"
```

## 4. Environment Configuration

### 4.1 API Keys

```bash
# .env file

# Gemini
GEMINI_API_KEY=your-gemini-key

# Optional: Other providers
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
```

### 4.2 Debug Logging

```bash
# Enable LiteLLM debug output
LITELLM_LOG=DEBUG
```

## 5. Factory Pattern with LiteLLM

### 5.1 Provider-Based Factory

```python
# agents/factory.py
import os
from agents.extensions.models.litellm_model import LitellmModel

# Provider to model mapping
DEFAULT_MODELS = {
    "gemini": "gemini/gemini-2.5-flash",
    "openai": "openai/gpt-4o-mini",
    "anthropic": "anthropic/claude-3-5-sonnet-20241022",
    "deepseek": "deepseek/deepseek-chat",
}


def create_model(model_override: str | None = None):
    """Create a LiteLLM model based on configuration.

    Args:
        model_override: Optional specific model ID to use.

    Returns:
        LitellmModel instance.
    """
    if model_override:
        return LitellmModel(model_id=model_override)

    provider = os.getenv("LLM_PROVIDER", "gemini").lower()
    model_id = DEFAULT_MODELS.get(provider, DEFAULT_MODELS["gemini"])

    return LitellmModel(model_id=model_id)
```

### 5.2 Usage

```python
from agents import Agent, Runner
from agents.factory import create_model

# Uses LLM_PROVIDER env var
agent = Agent(
    name="flexible-agent",
    model=create_model(),
    instructions="...",
)

# Override for specific use case
coding_agent = Agent(
    name="coding-agent",
    model=create_model("anthropic/claude-3-5-sonnet-20241022"),
    instructions="You are a coding assistant.",
)
```

## 6. Advanced Configuration

### 6.1 Model Parameters

```python
from agents.extensions.models.litellm_model import LitellmModel

model = LitellmModel(
    model_id="gemini/gemini-2.5-flash",
    # Additional parameters passed to LiteLLM
    temperature=0.7,
    max_tokens=4096,
    top_p=0.95,
)
```

### 6.2 Fallback Models

```python
import litellm

# Configure fallbacks at LiteLLM level
litellm.set_fallback_models(
    primary_model="gemini/gemini-2.5-flash",
    fallback_models=[
        "gemini/gemini-2.0-flash",
        "openai/gpt-4o-mini",
    ]
)
```

### 6.3 Caching

```python
import litellm

# Enable LiteLLM caching
litellm.cache = litellm.Cache(
    type="redis",
    host="localhost",
    port=6379,
)

# Or simple in-memory cache
litellm.cache = litellm.Cache(type="local")
```

## 7. Tool Calling with LiteLLM

### 7.1 Basic Tools

```python
from agents import Agent, Runner, function_tool
from agents.extensions.models.litellm_model import LitellmModel

@function_tool
def calculate(expression: str) -> str:
    """Calculate a mathematical expression safely."""
    import ast
    import operator

    # Safe operators only
    ops = {
        ast.Add: operator.add, ast.Sub: operator.sub,
        ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.Pow: operator.pow, ast.USub: operator.neg,
    }

    def _eval(node):
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            return ops[type(node.op)](_eval(node.left), _eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            return ops[type(node.op)](_eval(node.operand))
        raise ValueError(f"Unsupported: {type(node)}")

    return str(_eval(ast.parse(expression, mode="eval").body))

model = LitellmModel(model_id="gemini/gemini-2.5-flash")

agent = Agent(
    name="calculator-agent",
    model=model,
    instructions="You are a calculator. Use the calculate tool for math.",
    tools=[calculate],
)

result = Runner.run_sync(agent, "What is 15 * 7 + 23?")
```

### 7.2 Tool Compatibility Notes

Not all providers support tools equally well through LiteLLM:

| Provider | Tool Support | Notes |
|----------|-------------|-------|
| Gemini | Good | Some preview models have issues |
| OpenAI | Excellent | Full support |
| Anthropic | Good | Full support |
| DeepSeek | Partial | May need workarounds |

## 8. Streaming with LiteLLM

### 8.1 Basic Streaming

```python
import asyncio
from agents import Agent, Runner
from agents.extensions.models.litellm_model import LitellmModel

model = LitellmModel(model_id="gemini/gemini-2.5-flash")

agent = Agent(
    name="streaming-agent",
    model=model,
    instructions="...",
)

async def stream():
    result = Runner.run_streamed(agent, "Tell me a story")

    async for event in result.stream_events():
        if hasattr(event, 'data') and hasattr(event.data, 'delta'):
            print(event.data.delta, end="", flush=True)

asyncio.run(stream())
```

### 8.2 ChatKit Integration

```python
from chatkit.agents import stream_agent_response, AgentContext
from agents import Agent, Runner
from agents.extensions.models.litellm_model import LitellmModel

model = LitellmModel(model_id="gemini/gemini-2.5-flash")

agent = Agent(
    name="chatkit-litellm",
    model=model,
    instructions="...",
)

async def respond(thread, input, context):
    agent_context = AgentContext(thread=thread, store=store, request_context=context)
    result = Runner.run_streamed(agent, input, context=agent_context)

    async for event in stream_agent_response(agent_context, result):
        yield event
```

## 9. Error Handling

### 9.1 Provider-Specific Errors

```python
import litellm
from litellm.exceptions import (
    AuthenticationError,
    RateLimitError,
    ServiceUnavailableError,
)

async def safe_call(agent, input):
    try:
        return await Runner.run(agent, input)

    except AuthenticationError:
        # Invalid API key for the provider
        raise

    except RateLimitError:
        # Rate limit hit - implement backoff
        raise

    except ServiceUnavailableError:
        # Provider is down - try fallback
        raise
```

### 9.2 Automatic Retries

```python
import litellm

# Configure automatic retries
litellm.num_retries = 3
litellm.retry_after = 5  # seconds
```

## 10. Multi-Provider Setup

### 10.1 Different Agents, Different Providers

```python
from agents import Agent
from agents.extensions.models.litellm_model import LitellmModel

# Fast agent for simple tasks
fast_agent = Agent(
    name="fast-responder",
    model=LitellmModel(model_id="gemini/gemini-2.5-flash"),
    instructions="Be concise and quick.",
)

# Smart agent for complex tasks
smart_agent = Agent(
    name="analyzer",
    model=LitellmModel(model_id="anthropic/claude-3-5-sonnet-20241022"),
    instructions="Analyze thoroughly.",
)

# Coding agent
coding_agent = Agent(
    name="coder",
    model=LitellmModel(model_id="openai/gpt-4.1"),
    instructions="Write clean, documented code.",
)
```

### 10.2 Router Pattern

```python
from agents import Agent, Runner
from agents.extensions.models.litellm_model import LitellmModel

# Router agent decides which specialist to use
router = Agent(
    name="router",
    model=LitellmModel(model_id="gemini/gemini-2.5-flash"),
    instructions="""Classify the user's request:
    - 'coding' for programming tasks
    - 'analysis' for research/analysis
    - 'quick' for simple questions
    Reply with just the category.""",
)

SPECIALISTS = {
    "coding": LitellmModel(model_id="openai/gpt-4.1"),
    "analysis": LitellmModel(model_id="anthropic/claude-3-5-sonnet-20241022"),
    "quick": LitellmModel(model_id="gemini/gemini-2.5-flash"),
}

def get_specialist_model(category: str):
    return SPECIALISTS.get(category.strip().lower(), SPECIALISTS["quick"])
```

## 11. Comparison: Direct vs LiteLLM

| Aspect | Direct OpenAI-Compatible | LiteLLM |
|--------|-------------------------|---------|
| Setup | Manual per provider | Unified |
| Switching | Code changes | Env var |
| Fallbacks | Manual | Built-in |
| Caching | Manual | Built-in |
| Logging | Manual | Built-in |
| Dependencies | Minimal | Extra package |
| Control | Full | Abstracted |

**Recommendation:**
- Use **Direct** for production with single provider
- Use **LiteLLM** for development/testing multiple providers
- Use **LiteLLM** when you need fallbacks/caching
