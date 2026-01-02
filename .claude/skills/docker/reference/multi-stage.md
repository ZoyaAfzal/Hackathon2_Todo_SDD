# Docker Multi-Stage Builds

Reduce image size by separating build and runtime environments.

## Concept

```
┌─────────────────────────────────────────────────────────┐
│ Stage 1: Build                                          │
│   - Full Node/Python image                              │
│   - Dev dependencies                                    │
│   - Build tools, compilers                              │
│   - Source code                                         │
│   → Output: Compiled application                        │
└─────────────────────────────────────────────────────────┘
                    │
                    │ COPY --from=builder
                    ▼
┌─────────────────────────────────────────────────────────┐
│ Stage 2: Production                                     │
│   - Minimal runtime image                               │
│   - Only production dependencies                        │
│   - Compiled application                                │
│   - NO source code, build tools                         │
│   → Output: Optimized production image                  │
└─────────────────────────────────────────────────────────┘
```

## Basic Pattern

```dockerfile
# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Production
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
CMD ["node", "dist/index.js"]
```

## Three-Stage Pattern

Separate dependencies installation for better caching:

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

# Copy only what's needed
COPY --from=builder --chown=appuser:nodejs /app/dist ./dist
COPY --from=builder --chown=appuser:nodejs /app/node_modules ./node_modules

USER appuser
CMD ["node", "dist/index.js"]
```

## Next.js Standalone Pattern

Optimized for Next.js standalone output:

```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app
COPY package*.json ./
RUN npm ci

# Stage 2: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# Stage 3: Production
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy static assets
COPY --from=builder /app/public ./public

# Set up Next.js cache directory
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Copy standalone build
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

## Python Pattern

```dockerfile
# Stage 1: Build
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production
FROM python:3.11-slim AS runner

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Non-root user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --uid "${UID}" \
    appuser

# Copy application code
COPY . .
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Go Pattern (Minimal)

```dockerfile
# Stage 1: Build
FROM golang:1.21-alpine AS builder

WORKDIR /app

# Dependencies
COPY go.mod go.sum ./
RUN go mod download

# Build
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /app/main .

# Stage 2: Production (scratch = empty base)
FROM scratch AS runner

# Copy binary
COPY --from=builder /app/main /main

# Copy CA certificates for HTTPS
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

USER 1001

EXPOSE 8080
ENTRYPOINT ["/main"]
```

## Copying Between Stages

```dockerfile
# Name stages with AS
FROM node:20-alpine AS builder
# ...

FROM node:20-alpine AS runner

# Copy from named stage
COPY --from=builder /app/dist ./dist

# Copy with ownership
COPY --from=builder --chown=appuser:appuser /app/dist ./dist

# Copy specific files
COPY --from=builder /app/package.json ./

# Copy from external image
COPY --from=nginx:alpine /etc/nginx/nginx.conf /etc/nginx/
```

## Build Specific Stage

```bash
# Build only builder stage
docker build --target builder -t myapp:builder .

# Build full production image
docker build -t myapp:latest .
```

## Size Comparison

| Application | Without Multi-Stage | With Multi-Stage | Reduction |
|-------------|--------------------:|------------------:|----------:|
| Next.js | 1.5GB | 200MB | 87% |
| FastAPI | 1.2GB | 300MB | 75% |
| Go | 800MB | 20MB | 97% |
| Express | 1GB | 150MB | 85% |

## Best Practices

### 1. Order Layers by Change Frequency

```dockerfile
# Less frequent changes first
COPY package*.json ./
RUN npm ci

# More frequent changes last
COPY . .
RUN npm run build
```

### 2. Use .dockerignore

```
node_modules
.next
dist
build
*.log
.git
.env*
```

### 3. Minimize Final Stage

```dockerfile
# Only copy what's absolutely needed
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package.json ./
# NOT: COPY --from=builder /app ./
```

### 4. Pin Base Image Versions

```dockerfile
# Good
FROM node:20.10.0-alpine3.18

# Avoid
FROM node:latest
```

### 5. Clean Up in Same Layer

```dockerfile
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*  # Clean in same RUN
```

## Debugging Multi-Stage Builds

```bash
# Build with all stages visible
docker build --target builder -t myapp:debug .

# Run intermediate stage
docker run -it myapp:debug sh

# Check sizes
docker images myapp
```
