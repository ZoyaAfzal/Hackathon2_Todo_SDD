# Docker Image Optimization

Techniques to reduce image size and improve build performance.

## Size Reduction Strategies

### 1. Use Minimal Base Images

| Language | Full | Slim | Alpine |
|----------|------|------|--------|
| Node.js | node:20 (~1GB) | node:20-slim (~200MB) | node:20-alpine (~130MB) |
| Python | python:3.11 (~1GB) | python:3.11-slim (~150MB) | python:3.11-alpine (~50MB) |

```dockerfile
# Prefer alpine or slim
FROM node:20-alpine
FROM python:3.11-slim
```

### 2. Multi-Stage Builds

See [multi-stage.md](multi-stage.md) for complete patterns.

```dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY . .
RUN npm ci && npm run build

# Production stage (only runtime)
FROM node:20-alpine
COPY --from=builder /app/dist ./dist
CMD ["node", "dist/index.js"]
```

### 3. Minimize Layers

```dockerfile
# Bad: Multiple RUN commands
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get clean

# Good: Single RUN with cleanup
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

### 4. Use .dockerignore

Create `.dockerignore` to exclude unnecessary files:

```
# Version control
.git
.gitignore

# Dependencies (rebuilt in container)
node_modules
.venv
__pycache__

# Build outputs
.next
dist
build

# Development
.env*
*.log
.DS_Store
.vscode
.idea

# Documentation
README.md
docs/

# Tests
tests/
*.test.js
*.spec.js
coverage/
.pytest_cache/
```

### 5. Order Layers by Change Frequency

```dockerfile
# Rarely changes - install dependencies first
COPY package*.json ./
RUN npm ci

# Frequently changes - copy source last
COPY . .
RUN npm run build
```

### 6. Clean Up in Same Layer

```dockerfile
# Install and clean in same RUN
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      curl \
      ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
```

### 7. Don't Install Unnecessary Packages

```dockerfile
# Use --no-install-recommends
RUN apt-get install -y --no-install-recommends curl

# Python: no cache
RUN pip install --no-cache-dir -r requirements.txt

# Node: production only
RUN npm ci --only=production
```

## Build Performance

### 1. Leverage Build Cache

```dockerfile
# Dependencies change less often
COPY package*.json ./
RUN npm ci  # Cached unless package.json changes

# Source changes more often
COPY . .    # Invalidates from here down
RUN npm run build
```

### 2. Use BuildKit

```bash
# Enable BuildKit
export DOCKER_BUILDKIT=1
docker build -t myapp .

# Or in docker-compose
COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose build
```

### 3. Cache Mounts (BuildKit)

```dockerfile
# Cache pip downloads
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Cache npm downloads
RUN --mount=type=cache,target=/root/.npm \
    npm ci

# Cache apt downloads
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get install -y curl
```

### 4. Bind Mounts for Build

```dockerfile
# Don't copy requirements, bind mount instead
RUN --mount=type=bind,source=requirements.txt,target=requirements.txt \
    pip install -r requirements.txt
```

### 5. Parallel Builds

```dockerfile
# BuildKit can parallelize independent stages
FROM node:20-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/ .
RUN npm ci && npm run build

FROM python:3.11-slim AS backend-builder
WORKDIR /backend
COPY backend/ .
RUN pip install -r requirements.txt

# Final stage combines both
FROM nginx:alpine
COPY --from=frontend-builder /frontend/dist /usr/share/nginx/html
COPY --from=backend-builder /backend /app
```

## Size Analysis

### Check Image Size

```bash
# List images with sizes
docker images myapp

# Detailed size breakdown
docker history myapp:latest

# No truncation
docker history myapp:latest --no-trunc
```

### Analyze with Dive

```bash
# Install dive
# macOS: brew install dive
# Windows: scoop install dive

# Analyze image
dive myapp:latest
```

### Compare Sizes

```bash
# Build with tag
docker build -t myapp:v1 .

# Make changes, rebuild
docker build -t myapp:v2 .

# Compare
docker images myapp
```

## Common Optimizations

### Node.js

```dockerfile
FROM node:20-alpine

# Production dependencies only
ENV NODE_ENV=production

WORKDIR /app

# Install production deps
COPY package*.json ./
RUN npm ci --only=production

# Copy built files (not source)
COPY dist ./dist

CMD ["node", "dist/index.js"]
```

### Python

```dockerfile
FROM python:3.11-slim

# Prevent Python from writing bytecode
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install with no cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

### Next.js Standalone

```javascript
// next.config.js
module.exports = {
  output: 'standalone',  // Creates minimal production bundle
}
```

```dockerfile
# Copy only standalone output (~130MB instead of ~500MB)
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
```

## Size Targets

| Application Type | Target Size | Notes |
|-----------------|-------------|-------|
| Next.js | < 500MB | Use standalone output |
| Express/Node | < 300MB | Production deps only |
| FastAPI/Python | < 500MB | Use slim base |
| Go | < 50MB | Use scratch or alpine |
| Static Site | < 50MB | nginx:alpine |

## Verification

```bash
# Check final size
docker images myapp

# Verify no dev dependencies
docker run --rm myapp:latest npm ls --prod

# Verify no source files
docker run --rm myapp:latest ls -la

# Check for secrets
docker history myapp:latest --no-trunc | grep -i "key\|secret\|password"
```

## Checklist

- [ ] Using minimal base image (alpine/slim)
- [ ] Multi-stage build implemented
- [ ] .dockerignore configured
- [ ] Layers ordered by change frequency
- [ ] Cleanup in same layer as install
- [ ] No dev dependencies in final image
- [ ] No source code in final image (if compiled)
- [ ] Image size within target
- [ ] Build time acceptable
