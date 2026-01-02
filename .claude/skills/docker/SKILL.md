---
name: docker
description: Docker containerization patterns for production deployments. Covers multi-stage builds, image optimization, security best practices, and application-specific patterns for Next.js and Python/FastAPI.
---

# Docker Skill

Production-ready Docker containerization patterns for web applications.

## Quick Start

### Build Image

```bash
docker build -t myapp:latest .
```

### Run Container

```bash
docker run -d -p 3000:3000 --name myapp myapp:latest
```

### Verify

```bash
docker ps
curl http://localhost:3000
```

## Key Concepts

| Concept | Guide |
|---------|-------|
| **Multi-Stage Builds** | [reference/multi-stage.md](reference/multi-stage.md) |
| **Security** | [reference/security.md](reference/security.md) |
| **Optimization** | [reference/optimization.md](reference/optimization.md) |

## Examples

| Pattern | Guide |
|---------|-------|
| **Next.js Standalone** | [examples/nextjs.md](examples/nextjs.md) |
| **FastAPI Python** | [examples/fastapi.md](examples/fastapi.md) |
| **Node.js Express** | [examples/nodejs.md](examples/nodejs.md) |

## Multi-Stage Build Pattern

```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

# Stage 2: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Stage 3: Production
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
# Non-root user
RUN addgroup -g 1001 -S nodejs && adduser -S appuser -u 1001 -G nodejs
COPY --from=builder --chown=appuser:nodejs /app/dist ./dist
USER appuser
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

## .dockerignore Template

```
.git
.gitignore
node_modules
.next
dist
build
*.log
.env*
.DS_Store
.vscode
.idea
coverage
.pytest_cache
__pycache__
*.pyc
.venv
```

## Security Checklist

- [ ] Non-root user (`USER appuser`)
- [ ] No secrets in Dockerfile
- [ ] Minimal base image (alpine/slim)
- [ ] No unnecessary packages
- [ ] Pinned base image version

## Image Size Guidelines

| Application | Target | Base Image |
|-------------|--------|------------|
| Next.js | < 500MB | node:20-alpine |
| FastAPI | < 1GB | python:3.11-slim |
| Express | < 300MB | node:20-alpine |

## Verification Commands

```bash
# Check image size
docker images myapp

# Verify non-root user
docker run --rm myapp:latest whoami

# View layers
docker history myapp:latest

# Test container
docker run -d -p 3000:3000 myapp:latest
curl http://localhost:3000
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Running as root | Add `USER appuser` |
| Copying node_modules | Use multi-stage build |
| Secrets in image | Use environment variables |
| Using `latest` tag | Pin versions |
| No .dockerignore | Create and maintain |

## CRITICAL: Pre-Build Verification

**ALWAYS run local checks BEFORE Docker build to catch all errors at once!**

Docker builds are slow. Don't waste time discovering TypeScript errors one at a time.

### Frontend (Next.js/TypeScript)

```bash
# Run BEFORE docker build
cd frontend
npx tsc --noEmit      # Catch ALL type errors
npm run build         # Verify build succeeds
cd ..

# THEN build Docker image
docker build -t myapp-frontend:latest ./frontend
```

### Backend (Python)

```bash
# Run BEFORE docker build
cd backend
python -m py_compile main.py    # Syntax check
pip install -r requirements.txt # Verify deps
cd ..

# THEN build Docker image
docker build -t myapp-backend:latest ./backend
```

### Why This Matters

- TypeScript errors appear during `npm run build` inside Docker
- Each Docker build takes 2-5 minutes
- Without local checks, you might rebuild 5+ times for 5 different errors
- Local checks take 30 seconds and show ALL errors at once

## Build Time vs Runtime Environment Variables

**CRITICAL for Kubernetes deployments:**

Environment variables in Docker can be:
1. **Build-time** (ARG) - Baked into image, cannot change
2. **Runtime** (ENV) - Can be overridden at container start

```dockerfile
# Build-time variable (CANNOT change after build)
ARG NODE_ENV=production

# Runtime variable (CAN change via K8s ConfigMap)
ENV DATABASE_URL=""
```

### Next.js Specific

`NEXT_PUBLIC_*` variables are **BUILD TIME** only:
```dockerfile
# ❌ This won't work - value is baked into JS bundle at build
ENV NEXT_PUBLIC_API_URL=http://backend:8000

# ✅ For runtime configuration, use:
# 1. Server-side API routes that read env vars at request time
# 2. A runtime config endpoint that client fetches on load
```

See Next.js skill for runtime API proxy pattern.
