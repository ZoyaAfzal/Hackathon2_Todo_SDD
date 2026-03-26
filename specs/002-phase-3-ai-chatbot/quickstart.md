# Quickstart: Phase III AI-Powered Todo Chatbot

## Prerequisites

- Python 3.11+
- Node.js 20+
- Neon PostgreSQL database (from Phase II)
- OpenAI API key
- Phase II backend and frontend running

## Environment Variables

Add these to `backend/.env` (in addition to existing Phase II vars):

```env
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4o-mini
```

## Backend Setup

```bash
cd backend

# Install new dependencies
pip install openai-agents mcp

# Run database migrations (adds conversation + message tables)
python -m alembic upgrade head

# Start the server
python -m uvicorn src.main:app --reload --port 8000
```

## Frontend Setup

```bash
cd frontend

# No new dependencies needed (uses existing fetch-based API client)
npm run dev
```

## Test the Chat Endpoint

```bash
# Get a JWT token (use existing login)
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}' \
  | jq -r '.token')

# Send a chat message (replace USER_ID with your user's UUID)
curl -X POST http://localhost:8000/api/{USER_ID}/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to buy groceries"}'
```

Expected response:
```json
{
  "conversation_id": "uuid-here",
  "reply": "I've created a task 'Buy groceries' for you!",
  "tool_calls": [
    {
      "tool_name": "add_task",
      "arguments": {"title": "Buy groceries"},
      "result": {"id": "uuid", "title": "Buy groceries", "completed": false}
    }
  ]
}
```

## Verify

1. Chat creates tasks: Send "Add a task to read a book" — check DB
2. Chat lists tasks: Send "Show my tasks" — see task list
3. Chat completes: Send "Mark task X as done" — check completed=true
4. Conversation persists: Restart server, send message with same
   `conversation_id` — context preserved
