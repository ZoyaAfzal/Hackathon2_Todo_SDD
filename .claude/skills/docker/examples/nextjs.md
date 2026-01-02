# Next.js Docker Pattern

Production-ready Dockerfile for Next.js applications using standalone output.

## Prerequisites

**CRITICAL**: Add `output: 'standalone'` to `next.config.js`:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  // ... other config
};

module.exports = nextConfig;
```

## Complete Dockerfile

```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./
RUN npm ci

# Stage 2: Build
FROM node:20-alpine AS builder
WORKDIR /app

# Copy dependencies
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build application
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# Stage 3: Production
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy built application
COPY --from=builder /app/public ./public

# Set correct permissions for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Copy standalone output
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

## .dockerignore

```
.git
.gitignore
node_modules
.next
.env*
*.log
.DS_Store
.vscode
coverage
Dockerfile*
docker-compose*
README.md
```

## Build and Run

```bash
# Build image
docker build -t myapp-frontend:latest .

# Run container
docker run -d \
  -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://localhost:8000 \
  --name frontend \
  myapp-frontend:latest

# Verify
curl http://localhost:3000
```

## Environment Variables

Pass at runtime, not build time for flexibility:

```bash
docker run -d \
  -p 3000:3000 \
  -e NEXT_PUBLIC_APP_URL=http://localhost:3000 \
  -e NEXT_PUBLIC_API_URL=http://backend:8000 \
  myapp-frontend:latest
```

**Note**: `NEXT_PUBLIC_*` variables are embedded at build time. For runtime config, use server-side environment variables.

## Size Optimization

Target: **< 500MB**

Tips:
- Use multi-stage builds
- Don't copy node_modules (rebuild in container)
- Use alpine base image
- Standalone output excludes unused dependencies

## Verification

```bash
# Check image size
docker images myapp-frontend

# Verify non-root user
docker run --rm myapp-frontend:latest whoami
# Should output: nextjs

# Check health
docker run -d -p 3000:3000 myapp-frontend:latest
curl -I http://localhost:3000
```

## Common Issues

### Build fails with "standalone not found"

**Cause**: Missing `output: 'standalone'` in next.config.js

**Fix**: Add the config and rebuild

### Image too large (> 500MB)

**Cause**: Including dev dependencies or source files

**Fix**:
- Verify .dockerignore excludes node_modules
- Use multi-stage build
- Check for unnecessary COPY commands

### Static assets not loading

**Cause**: Missing static file copy

**Fix**: Ensure both copies are present:
```dockerfile
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
```
