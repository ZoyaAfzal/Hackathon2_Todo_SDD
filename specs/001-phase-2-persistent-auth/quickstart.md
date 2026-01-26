# Quickstart Guide: Phase II - Persistent Storage with Authentication

**Date**: 2026-01-07
**Branch**: `001-phase-2-persistent-auth`
**Spec**: [spec.md](./spec.md)

---

## Prerequisites

### Required Software

- **Python**: 3.11+ (for backend)
- **Node.js**: 20+ (for frontend)
- **pnpm**: 8+ (recommended) or npm
- **Git**: 2.40+

### Accounts Required

- **Neon PostgreSQL**: Free tier at [neon.tech](https://neon.tech)

---

## Project Setup

### 1. Clone and Setup Branch

```bash
# Clone the repository (if not already cloned)
git clone <repository-url>
cd evolution-of-todo

# Checkout the Phase II branch
git checkout 001-phase-2-persistent-auth
```

### 2. Create Project Structure

```bash
# Create backend and frontend directories
mkdir -p backend/src/{models,services,api/{routes,deps},core}
mkdir -p backend/tests/{unit,contract,integration}
mkdir -p frontend/src/{app,components,lib,types}
mkdir -p frontend/tests
```

---

## Backend Setup (FastAPI)

### 1. Create Virtual Environment

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# .\venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Create requirements.txt
cat > requirements.txt << 'EOF'
fastapi>=0.109.0
sqlmodel>=0.0.14
pyjwt>=2.8.0
python-dotenv>=1.0.0
psycopg2-binary>=2.9.9
opentelemetry-api>=1.22.0
opentelemetry-sdk>=1.22.0
opentelemetry-instrumentation-fastapi>=0.43b0
opentelemetry-instrumentation-sqlalchemy>=0.43b0
opentelemetry-exporter-otlp>=1.22.0
uvicorn>=0.27.0
alembic>=1.13.0
EOF

# Install dependencies
pip install -r requirements.txt

# Create dev requirements
cat > requirements-dev.txt << 'EOF'
pytest>=8.0.0
pytest-asyncio>=0.23.0
pytest-cov>=4.1.0
httpx>=0.26.0
EOF

pip install -r requirements-dev.txt
```

### 3. Environment Configuration

```bash
# Create .env file
cat > .env << 'EOF'
# Database (get from Neon console)
DATABASE_URL=postgresql://user:password@ep-name.region.aws.neon.tech/dbname?sslmode=require

# Authentication (shared with frontend)
BETTER_AUTH_SECRET=your-256-bit-secret-key-minimum-32-characters

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true

# OpenTelemetry (optional for development)
OTEL_SERVICE_NAME=todo-api
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
EOF
```

### 4. Database Setup

```bash
# Initialize Alembic
alembic init alembic

# Configure alembic.ini to use DATABASE_URL from environment

# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Run migrations
alembic upgrade head
```

### 5. Run Backend

```bash
# Development mode with auto-reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Backend will be available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

---

## Frontend Setup (Next.js)

### 1. Initialize Next.js Project

```bash
cd ../frontend

# Create Next.js app with App Router
pnpm create next-app . --typescript --tailwind --eslint --app --src-dir

# Or with npm:
# npx create-next-app . --typescript --tailwind --eslint --app --src-dir
```

### 2. Install Dependencies

```bash
# Install Better Auth and related packages
pnpm add better-auth @better-auth/client

# Or with npm:
# npm install better-auth @better-auth/client
```

### 3. Environment Configuration

```bash
# Create .env.local
cat > .env.local << 'EOF'
# App URL
NEXT_PUBLIC_APP_URL=http://localhost:3000

# API URL (FastAPI backend)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth (must match backend BETTER_AUTH_SECRET)
BETTER_AUTH_SECRET=your-256-bit-secret-key-minimum-32-characters

# Database (for Better Auth user storage)
DATABASE_URL=postgresql://user:password@ep-name.region.aws.neon.tech/dbname?sslmode=require
EOF
```

### 4. Configure Better Auth

```typescript
// src/lib/auth.ts
import { betterAuth } from "better-auth"
import { jwt } from "better-auth/plugins"

export const auth = betterAuth({
    database: {
        url: process.env.DATABASE_URL!
    },
    plugins: [
        jwt()
    ],
    secret: process.env.BETTER_AUTH_SECRET
})
```

```typescript
// src/lib/auth-client.ts
import { createAuthClient } from "better-auth/client"

export const authClient = createAuthClient({
    baseURL: process.env.NEXT_PUBLIC_APP_URL
})
```

### 5. Run Frontend

```bash
# Development mode
pnpm dev

# Frontend will be available at http://localhost:3000
```

---

## Neon PostgreSQL Setup

### 1. Create Neon Account

1. Go to [neon.tech](https://neon.tech)
2. Sign up for free account
3. Create a new project

### 2. Get Connection String

1. Go to your project dashboard
2. Click "Connection Details"
3. Copy the connection string
4. Use the **pooled** connection string for production

### 3. Connection String Format

```
# Standard (direct)
postgresql://user:password@ep-name-123456.us-east-2.aws.neon.tech/dbname?sslmode=require

# Pooled (recommended)
postgresql://user:password@ep-name-123456-pooler.us-east-2.aws.neon.tech/dbname?sslmode=require
```

---

## Running the Full Stack

### Terminal 1: Backend

```bash
cd backend
source venv/bin/activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2: Frontend

```bash
cd frontend
pnpm dev
```

### Access Points

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Next.js application |
| Backend API | http://localhost:8000 | FastAPI server |
| API Docs | http://localhost:8000/docs | Swagger UI |
| ReDoc | http://localhost:8000/redoc | Alternative API docs |

---

## Running Tests

### Backend Tests

```bash
cd backend
source venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_task_service.py

# Run specific test
pytest tests/unit/test_task_service.py::test_create_task
```

### Frontend Tests

```bash
cd frontend

# Run tests
pnpm test

# Run with coverage
pnpm test:coverage
```

---

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Run Tests Before Commit

```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && pnpm test
```

### 3. Commit Changes

```bash
git add .
git commit -m "feat: your feature description"
```

### 4. Push and Create PR

```bash
git push -u origin feature/your-feature-name
```

---

## Common Issues

### Issue: Database Connection Failed

**Error**: `psycopg2.OperationalError: could not connect to server`

**Solution**:
1. Check DATABASE_URL is correct
2. Ensure Neon compute is not suspended (make a request to wake it)
3. Check if `sslmode=require` is in connection string

### Issue: JWT Verification Failed

**Error**: `jwt.exceptions.InvalidSignatureError`

**Solution**:
1. Ensure `BETTER_AUTH_SECRET` matches in both backend and frontend
2. Check the secret is at least 32 characters
3. Verify token is being sent with `Bearer ` prefix

### Issue: CORS Errors

**Error**: `Access-Control-Allow-Origin` missing

**Solution**: Add CORS middleware to FastAPI:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Environment Variables Reference

### Backend (.env)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | Neon PostgreSQL connection string |
| `BETTER_AUTH_SECRET` | Yes | JWT signing secret (min 32 chars) |
| `HOST` | No | Server host (default: 0.0.0.0) |
| `PORT` | No | Server port (default: 8000) |
| `DEBUG` | No | Enable debug mode (default: false) |

### Frontend (.env.local)

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_APP_URL` | Yes | Frontend URL |
| `NEXT_PUBLIC_API_URL` | Yes | Backend API URL |
| `BETTER_AUTH_SECRET` | Yes | JWT signing secret (must match backend) |
| `DATABASE_URL` | Yes | Neon PostgreSQL for Better Auth |

---

## Next Steps

After completing setup:

1. Run `/sp.tasks` to generate implementation tasks
2. Follow TDD cycle: write tests first, then implement
3. Use the API contract as the source of truth for endpoints
4. Validate against spec acceptance criteria
