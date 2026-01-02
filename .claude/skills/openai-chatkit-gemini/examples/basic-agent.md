# Basic Gemini Agent Examples

Practical examples for creating agents with Gemini models using the OpenAI Agents SDK.

## Example 1: Minimal Gemini Agent

The simplest possible Gemini agent.

```python
# minimal_agent.py
import os
from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel

# Configure Gemini client
client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Create model
model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=client,
)

# Create agent
agent = Agent(
    name="gemini-assistant",
    model=model,
    instructions="You are a helpful assistant. Be concise and accurate.",
)

# Run synchronously
result = Runner.run_sync(agent, "What is the capital of France?")
print(result.final_output)
```

## Example 2: Factory-Based Agent

Using the factory pattern for clean configuration.

```python
# agents/factory.py
import os
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


def create_model():
    """Create model based on LLM_PROVIDER environment variable."""
    provider = os.getenv("LLM_PROVIDER", "openai").lower()

    if provider == "gemini":
        client = AsyncOpenAI(
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url=GEMINI_BASE_URL,
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
```

```python
# main.py
from agents import Agent, Runner
from agents.factory import create_model

agent = Agent(
    name="factory-agent",
    model=create_model(),
    instructions="You are a helpful assistant.",
)

result = Runner.run_sync(agent, "Hello!")
print(result.final_output)
```

```bash
# .env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-api-key
GEMINI_DEFAULT_MODEL=gemini-2.5-flash
```

## Example 3: Async Agent

Asynchronous agent execution.

```python
# async_agent.py
import asyncio
from agents import Agent, Runner
from agents.factory import create_model

agent = Agent(
    name="async-gemini",
    model=create_model(),
    instructions="You are a helpful assistant.",
)


async def main():
    # Single async call
    result = await Runner.run(agent, "Tell me a short joke")
    print(result.final_output)

    # Multiple concurrent calls
    tasks = [
        Runner.run(agent, "What is 2+2?"),
        Runner.run(agent, "What color is the sky?"),
        Runner.run(agent, "Name a fruit"),
    ]
    results = await asyncio.gather(*tasks)

    for r in results:
        print(f"- {r.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
```

## Example 4: Streaming Agent

Real-time streaming responses.

```python
# streaming_agent.py
import asyncio
from agents import Agent, Runner
from agents.factory import create_model

agent = Agent(
    name="streaming-gemini",
    model=create_model(),
    instructions="You are a storyteller. Tell engaging stories.",
)


async def stream_response(prompt: str):
    result = Runner.run_streamed(agent, prompt)

    async for event in result.stream_events():
        if hasattr(event, "data"):
            if hasattr(event.data, "delta"):
                print(event.data.delta, end="", flush=True)

    print()  # Newline at end
    final = await result.final_output
    return final


async def main():
    print("Streaming response:\n")
    await stream_response("Tell me a very short story about a robot")


if __name__ == "__main__":
    asyncio.run(main())
```

## Example 5: Agent with Custom Settings

Configuring temperature and other model parameters.

```python
# custom_settings_agent.py
from agents import Agent, Runner, ModelSettings
from agents.factory import create_model

# Creative agent with high temperature
creative_agent = Agent(
    name="creative-writer",
    model=create_model(),
    model_settings=ModelSettings(
        temperature=0.9,
        max_tokens=2048,
        top_p=0.95,
    ),
    instructions="""You are a creative writer.
    Generate unique, imaginative content.
    Don't be afraid to be unconventional.""",
)

# Precise agent with low temperature
precise_agent = Agent(
    name="fact-checker",
    model=create_model(),
    model_settings=ModelSettings(
        temperature=0.1,
        max_tokens=1024,
    ),
    instructions="""You are a fact-focused assistant.
    Provide accurate, verified information only.
    If uncertain, say so.""",
)

# Run both
creative_result = Runner.run_sync(
    creative_agent,
    "Write a unique metaphor for learning"
)
print(f"Creative: {creative_result.final_output}\n")

precise_result = Runner.run_sync(
    precise_agent,
    "What is the speed of light in vacuum?"
)
print(f"Precise: {precise_result.final_output}")
```

## Example 6: Conversation Agent

Multi-turn conversation handling.

```python
# conversation_agent.py
import asyncio
from agents import Agent, Runner
from agents.factory import create_model

agent = Agent(
    name="conversational-gemini",
    model=create_model(),
    instructions="""You are a friendly conversational assistant.
    Remember context from previous messages.
    Be engaging and ask follow-up questions.""",
)


async def chat():
    conversation_history = []

    print("Chat with Gemini (type 'quit' to exit)\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "quit":
            print("Goodbye!")
            break

        if not user_input:
            continue

        # Build input with history
        messages = conversation_history + [
            {"role": "user", "content": user_input}
        ]

        result = await Runner.run(agent, messages)
        response = result.final_output

        # Update history
        conversation_history.append({"role": "user", "content": user_input})
        conversation_history.append({"role": "assistant", "content": response})

        print(f"Gemini: {response}\n")


if __name__ == "__main__":
    asyncio.run(chat())
```

## Example 7: Error Handling

Robust error handling for production.

```python
# robust_agent.py
import asyncio
from openai import (
    APIError,
    AuthenticationError,
    RateLimitError,
    APIConnectionError,
)
from agents import Agent, Runner
from agents.factory import create_model

agent = Agent(
    name="robust-gemini",
    model=create_model(),
    instructions="You are a helpful assistant.",
)


async def safe_query(prompt: str, max_retries: int = 3) -> str:
    """Execute agent query with error handling and retries."""
    last_error = None

    for attempt in range(max_retries):
        try:
            result = await Runner.run(agent, prompt)
            return result.final_output

        except AuthenticationError:
            # Don't retry auth errors
            raise ValueError("Invalid GEMINI_API_KEY")

        except RateLimitError as e:
            last_error = e
            if attempt < max_retries - 1:
                wait = 2 ** attempt
                print(f"Rate limited, waiting {wait}s...")
                await asyncio.sleep(wait)

        except APIConnectionError as e:
            last_error = e
            if attempt < max_retries - 1:
                wait = 1
                print(f"Connection error, retrying in {wait}s...")
                await asyncio.sleep(wait)

        except APIError as e:
            last_error = e
            print(f"API error: {e}")
            break

    raise ValueError(f"Failed after {max_retries} attempts: {last_error}")


async def main():
    try:
        response = await safe_query("What is 2+2?")
        print(f"Response: {response}")
    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
```

## Example 8: Testing Gemini Connection

Verify your setup works before building agents.

```python
# test_connection.py
import os
import asyncio
from openai import AsyncOpenAI

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


async def test_gemini_connection():
    """Test basic Gemini API connectivity."""
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("ERROR: GEMINI_API_KEY not set")
        return False

    try:
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=GEMINI_BASE_URL,
        )

        response = await client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[{"role": "user", "content": "Say 'Hello World'"}],
            max_tokens=50,
        )

        content = response.choices[0].message.content
        print(f"SUCCESS: {content}")
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        return False


async def test_streaming():
    """Test streaming capability."""
    api_key = os.getenv("GEMINI_API_KEY")

    client = AsyncOpenAI(
        api_key=api_key,
        base_url=GEMINI_BASE_URL,
    )

    print("Testing streaming: ", end="")

    stream = await client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[{"role": "user", "content": "Count to 5"}],
        stream=True,
    )

    async for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)

    print("\nStreaming: OK")


if __name__ == "__main__":
    print("Testing Gemini connection...\n")
    asyncio.run(test_gemini_connection())
    print()
    asyncio.run(test_streaming())
```

## Running the Examples

1. Set up environment:
```bash
export GEMINI_API_KEY="your-api-key"
export LLM_PROVIDER="gemini"
export GEMINI_DEFAULT_MODEL="gemini-2.5-flash"
```

2. Install dependencies:
```bash
pip install openai-agents openai
```

3. Run any example:
```bash
python minimal_agent.py
python streaming_agent.py
python test_connection.py
```
