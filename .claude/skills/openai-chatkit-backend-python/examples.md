# ChatKit Custom Backend — Python Examples

These examples support the `openai-chatkit-backend-python` Skill.
They are **patterns**, not drop‑in production code, but they are close to
runnable and show realistic structure.

---

## Example 1 — Complete ChatKit Protocol Handler (SSE Streaming)

This is the CORRECT pattern based on actual ChatKit protocol requirements.

```python
# backend/src/api/chatkit.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, Any, AsyncIterator
import json

from agents import Agent, Runner
from agents.factory import create_model
from src.models import User
from src.services.chat_service import ChatService

router = APIRouter()

def route_chatkit_request(request_type: str, params: Dict[str, Any]):
    """Route ChatKit requests to appropriate handlers."""
    if request_type == "threads.list":
        return handle_threads_list(params)
    elif request_type == "threads.create":
        # Check if this is a message send disguised as thread.create
        if has_user_input(params):
            return handle_messages_send(params)  # Stream response
        return handle_threads_create(params)  # JSON response
    elif request_type == "threads.get":
        return handle_threads_get(params)
    elif request_type == "threads.delete":
        return handle_threads_delete(params)
    elif request_type == "messages.send":
        return handle_messages_send(params)  # Stream response
    else:
        raise HTTPException(status_code=400, detail=f"Unknown type: {request_type}")

def has_user_input(params: Dict[str, Any]) -> bool:
    """Check if params contains user input (message)."""
    input_data = params.get("input", {})
    if not input_data:
        return False
    content = input_data.get("content", [])
    for item in content:
        if isinstance(item, dict) and item.get("type") in ("input_text", "text"):
            if item.get("text", "").strip():
                return True
    return False

async def handle_messages_send(
    params: Dict[str, Any],
    session: Session,
    user: User,
) -> StreamingResponse:
    """Handle message streaming with CORRECT ChatKit SSE protocol."""

    # Extract message text
    input_data = params.get("input", {})
    content = input_data.get("content", [])
    message_text = ""
    for item in content:
        if isinstance(item, dict) and item.get("type") in ("input_text", "text"):
            message_text = item.get("text", "")
            break

    # Save user message to database
    chat_service = ChatService(session)
    conversation = chat_service.get_or_create_conversation(user.id)
    user_message = chat_service.save_message(
        conversation_id=conversation.id,
        user_id=user.id,
        role="user",
        content=message_text,
    )

    # Generate item IDs
    item_counter = [0]
    def generate_item_id():
        item_counter[0] += 1
        return f"item_{conversation.id}_{item_counter[0]}"

    async def generate() -> AsyncIterator[str]:
        # 1. Send thread.created event
        yield f"data: {json.dumps({'type': 'thread.created', 'thread': {'id': str(conversation.id), 'title': 'Chat'}})}\n\n"

        # 2. Send user message via thread.item.added (MUST use input_text type)
        user_item = {
            'type': 'user_message',
            'id': str(user_message.id),
            'thread_id': str(conversation.id),
            'content': [{'type': 'input_text', 'text': message_text}],
            'attachments': [],
            'quoted_text': None,
            'inference_options': {}
        }
        yield f"data: {json.dumps({'type': 'thread.item.added', 'item': user_item})}\n\n"

        # 3. Create agent and run
        agent = Agent(
            name="TaskAssistant",
            model=create_model(),
            instructions="You are a helpful task management assistant."
        )

        messages = [{"role": "user", "content": message_text}]
        result = Runner.run_streamed(agent, input=messages)

        assistant_item_id = generate_item_id()
        full_response = []

        # 4. Send assistant message start via thread.item.added (MUST use output_text type)
        assistant_item = {
            'type': 'assistant_message',
            'id': assistant_item_id,
            'thread_id': str(conversation.id),
            'content': [{'type': 'output_text', 'text': '', 'annotations': []}]
        }
        yield f"data: {json.dumps({'type': 'thread.item.added', 'item': assistant_item})}\n\n"

        # 5. Stream text deltas via thread.item.updated
        async for event in result.stream_events():
            if event.type == 'raw_response_event' and hasattr(event, 'data'):
                data = event.data
                if getattr(data, 'type', '') == 'response.output_text.delta':
                    text = getattr(data, 'delta', None)
                    if text:
                        full_response.append(text)
                        update_event = {
                            'type': 'thread.item.updated',
                            'item_id': assistant_item_id,
                            'update': {
                                'type': 'assistant_message.content_part.text_delta',
                                'content_index': 0,
                                'delta': text
                            }
                        }
                        yield f"data: {json.dumps(update_event)}\n\n"

        # 6. Send thread.item.done with complete message
        assistant_response = "".join(full_response) or result.final_output
        final_item = {
            'type': 'assistant_message',
            'id': assistant_item_id,
            'thread_id': str(conversation.id),
            'content': [{'type': 'output_text', 'text': assistant_response, 'annotations': []}]
        }
        yield f"data: {json.dumps({'type': 'thread.item.done', 'item': final_item})}\n\n"

        # Save to database
        chat_service.save_message(
            conversation_id=conversation.id,
            user_id=user.id,
            role="assistant",
            content=assistant_response,
        )

    return StreamingResponse(generate(), media_type="text/event-stream")

@router.post("/chatkit")
async def chatkit_endpoint(
    request: Request,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """Main ChatKit protocol endpoint."""
    body = await request.json()
    request_type = body.get("type")
    params = body.get("params", {})

    result = route_chatkit_request(request_type, params, session, user)

    # If result is StreamingResponse, return it directly
    if isinstance(result, StreamingResponse):
        return result

    # Otherwise return JSON
    return result
```

**Key Protocol Points:**
1. User messages MUST use `"type": "input_text"` in content
2. Assistant messages MUST use `"type": "output_text"` in content
3. SSE events use `thread.created`, `thread.item.added`, `thread.item.updated`, `thread.item.done`
4. Text deltas go in `update.delta`, not `delta.text`
5. Always include `attachments`, `quoted_text`, `inference_options` for user messages
6. Always include `annotations` for assistant messages

---

## Example 2 — Minimal FastAPI ChatKit Backend (Non‑Streaming)

```python
# main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from agents.factory import create_model
from agents import Agent, Runner

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chatkit/api")
async def chatkit_api(request: Request):
    # 1) Auth (simplified)
    auth_header = request.headers.get("authorization")
    if not auth_header:
        return {"error": "Unauthorized"}, 401

    # 2) Parse ChatKit event
    event = await request.json()
    user_message = event.get("message", {}).get("content") or ""

    # 3) Run agent through Agents SDK
    agent = Agent(
        name="simple-backend-agent",
        model=create_model(),
        instructions=(
            "You are the backend agent behind a ChatKit UI. "
            "Answer clearly in a single paragraph."
        ),
    )
    result = Runner.run_sync(starting_agent=agent, input=user_message)

    # 4) Map to ChatKit-style response (simplified)
    return {
        "type": "message",
        "content": result.final_output,
        "done": True,
    }
```

---

## Example 2 — FastAPI Backend with Streaming (SSE‑like)

```python
# streaming_backend.py
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from agents.factory import create_model
from agents import Agent, Runner

app = FastAPI()

def agent_stream(user_text: str):
    # In a real implementation, you might use an async generator
    # and partial tokens from the Agents SDK. Here we fake steps.
    yield "data: {"partial": "Thinking..."}\n\n"

    agent = Agent(
        name="streaming-agent",
        model=create_model(),
        instructions="Respond in short sentences suitable for streaming.",
    )
    result = Runner.run_sync(starting_agent=agent, input=user_text)

    yield f"data: {{"final": "{result.final_output}", "done": true}}\n\n"

@app.post("/chatkit/api")
async def chatkit_api(request: Request):
    event = await request.json()
    user_text = event.get("message", {}).get("content", "")

    return StreamingResponse(
        agent_stream(user_text),
        media_type="text/event-stream",
    )
```

---

## Example 3 — Backend with a Tool (ERP Employee Lookup)

```python
# agents/tools/erp_tools.py
from pydantic import BaseModel
from agents import function_tool

class EmployeeLookup(BaseModel):
    emp_id: int

@function_tool
def get_employee(data: EmployeeLookup):
    # In reality, query your ERP or DB here.
    if data.emp_id == 7:
        return {"id": 7, "name": "Zeeshan", "status": "active"}
    return {"id": data.emp_id, "name": "Unknown", "status": "not_found"}
```

```python
# agents/support_agent.py
from agents import Agent
from agents.factory import create_model
from agents.tools.erp_tools import get_employee

def build_support_agent() -> Agent:
    return Agent(
        name="erp-support",
        model=create_model(),
        instructions=(
            "You are an ERP support agent. "
            "Use tools to fetch employee or order data when needed."
        ),
        tools=[get_employee],
    )
```

```python
# chatkit/router.py
from agents import Runner
from agents.support_agent import build_support_agent

async def handle_user_message(event: dict) -> dict:
    text = event.get("message", {}).get("content", "")
    agent = build_support_agent()
    result = Runner.run_sync(starting_agent=agent, input=text)

    return {
        "type": "message",
        "content": result.final_output,
        "done": True,
    }
```

---

## Example 4 — Multi‑Agent Router Pattern

```python
# agents/router_agent.py
from agents import Agent
from agents.factory import create_model

def build_router_agent() -> Agent:
    return Agent(
        name="router",
        model=create_model(),
        instructions=(
            "You are a router agent. Decide which specialist should handle "
            "the query. Reply with exactly one of: "
            ""billing", "tech", or "general"."
        ),
    )
```

```python
# chatkit/router.py
from agents import Runner
from agents.router_agent import build_router_agent
from agents.billing_agent import build_billing_agent
from agents.tech_agent import build_tech_agent
from agents.general_agent import build_general_agent

def route_to_specialist(user_text: str):
    router = build_router_agent()
    route_result = Runner.run_sync(starting_agent=router, input=user_text)
    choice = (route_result.final_output or "").strip().lower()

    if "billing" in choice:
        return build_billing_agent()
    if "tech" in choice:
        return build_tech_agent()
    return build_general_agent()

async def handle_user_message(event: dict) -> dict:
    text = event.get("message", {}).get("content", "")
    agent = route_to_specialist(text)
    result = Runner.run_sync(starting_agent=agent, input=text)
    return {"type": "message", "content": result.final_output, "done": True}
```

---

## Example 5 — File Upload Endpoint for Direct Uploads

```python
# chatkit/upload.py
from fastapi import UploadFile
from uuid import uuid4
from pathlib import Path

UPLOAD_ROOT = Path("uploads")

async def handle_upload(file: UploadFile):
    UPLOAD_ROOT.mkdir(exist_ok=True)
    suffix = Path(file.filename).suffix
    target_name = f"{uuid4().hex}{suffix}"
    target_path = UPLOAD_ROOT / target_name

    with target_path.open("wb") as f:
        f.write(await file.read())

    # In real life, you might upload to S3 or another CDN instead
    public_url = f"https://cdn.example.com/{target_name}"
    return {"url": public_url}
```

```python
# main.py (excerpt)
from fastapi import UploadFile
from chatkit.upload import handle_upload

@app.post("/chatkit/api/upload")
async def chatkit_upload(file: UploadFile):
    return await handle_upload(file)
```

---

## Example 6 — Using Gemini via OpenAI‑Compatible Endpoint

```python
# agents/factory.py
import os
from agents import OpenAIChatCompletionsModel, AsyncOpenAI

def create_model():
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

---

## Example 7 — Injecting User/Tenant Context into Agent

```python
# chatkit/router.py (excerpt)
from agents import Agent, Runner
from agents.factory import create_model

async def handle_user_message(event: dict, user_id: str, tenant_id: str, role: str):
    text = event.get("message", {}).get("content", "")

    instructions = (
        f"You are a support agent for tenant {tenant_id}. "
        f"The current user is {user_id} with role {role}. "
        "Never reveal data from other tenants. "
        "Respect the user's role for access control."
    )

    agent = Agent(
        name="tenant-aware-support",
        model=create_model(),
        instructions=instructions,
    )

    result = Runner.run_sync(starting_agent=agent, input=text)
    return {"type": "message", "content": result.final_output, "done": True}
```

These patterns together cover most real-world scenarios for a **ChatKit
custom backend in Python** with the Agents SDK.
