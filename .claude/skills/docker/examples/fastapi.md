# FastAPI Docker Pattern

Production-ready Dockerfile for Python FastAPI applications.

## Complete Dockerfile

```dockerfile
FROM python:3.11-slim

# Prevent Python from writing bytecode and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create non-root user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Install dependencies with caching
# Note: BuildKit cache mount handles caching, so we don't use --no-cache-dir here
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Copy application code
COPY . .

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Alternative: Without BuildKit Cache

If BuildKit is not available:

```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create non-root user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --uid "${UID}" \
    appuser

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## .dockerignore

```
.git
.gitignore
__pycache__
*.pyc
*.pyo
*.pyd
.Python
.venv
venv
env
.env*
*.log
.DS_Store
.vscode
.idea
.pytest_cache
.coverage
htmlcov
dist
build
*.egg-info
Dockerfile*
docker-compose*
README.md
tests/
```

## Build and Run

```bash
# Build image
docker build -t myapp-backend:latest .

# Run container with environment variables
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@host:5432/db" \
  -e BETTER_AUTH_SECRET="your-secret" \
  --name backend \
  myapp-backend:latest

# Verify
curl http://localhost:8000/health
```

## Environment Variables

Pass sensitive values at runtime:

```bash
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL="${DATABASE_URL}" \
  -e BETTER_AUTH_SECRET="${BETTER_AUTH_SECRET}" \
  -e GROQ_API_KEY="${GROQ_API_KEY}" \
  -e CORS_ORIGINS="http://localhost:3000" \
  myapp-backend:latest
```

## Size Optimization

Target: **< 1GB**

Tips:
- Use `python:3.11-slim` (not full python image)
- Use `--no-cache-dir` with pip
- Don't include test files
- Remove __pycache__ via .dockerignore

## Health Endpoint

Ensure your FastAPI app has a health endpoint:

```python
# main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

## Verification

```bash
# Check image size
docker images myapp-backend

# Verify non-root user
docker run --rm myapp-backend:latest whoami
# Should output: appuser

# Check health endpoint
docker run -d -p 8000:8000 myapp-backend:latest
curl http://localhost:8000/health
```

## Common Issues

### Module not found

**Cause**: Missing dependency in requirements.txt

**Fix**: Ensure all dependencies are listed:
```bash
pip freeze > requirements.txt
```

### Permission denied

**Cause**: Files owned by root, running as non-root user

**Fix**: Add ownership change before USER instruction:
```dockerfile
RUN chown -R appuser:appuser /app
USER appuser
```

### Slow builds

**Cause**: Reinstalling all dependencies on every build

**Fix**: Use BuildKit cache mounts:
```dockerfile
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
```

### Database connection fails

**Cause**: Missing environment variable

**Fix**: Pass DATABASE_URL at runtime:
```bash
docker run -e DATABASE_URL="..." myapp-backend:latest
```
