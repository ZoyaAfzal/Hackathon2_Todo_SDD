# Docker Security Best Practices

Essential security patterns for production containers.

## Non-Root User (CRITICAL)

**Always run containers as non-root user.**

### Node.js Pattern

```dockerfile
# Create user and group
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy files with ownership
COPY --from=builder --chown=nextjs:nodejs /app/dist ./dist

# Switch to non-root user
USER nextjs
```

### Python Pattern

```dockerfile
# Create user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Change ownership
RUN chown -R appuser:appuser /app

# Switch user
USER appuser
```

### Verification

```bash
# Should NOT output "root"
docker run --rm myapp:latest whoami

# Should NOT be UID 0
docker run --rm myapp:latest id
```

## No Secrets in Images

**Never include secrets in Dockerfiles or image layers.**

### Wrong

```dockerfile
# NEVER DO THIS
ENV API_KEY=sk-1234567890
COPY .env /app/.env
```

### Correct

```dockerfile
# Declare that env var is expected at runtime
# Don't set a value
ENV DATABASE_URL=""
ENV API_KEY=""
```

```bash
# Pass secrets at runtime
docker run -e API_KEY="${API_KEY}" myapp:latest
```

### Check for Secrets

```bash
# Inspect image layers
docker history myapp:latest --no-trunc

# Look for sensitive keywords
docker history myapp:latest --no-trunc | grep -i "key\|secret\|password\|token"
```

## Minimal Base Images

Use smallest suitable base image.

| Language | Recommended Base |
|----------|------------------|
| Node.js | `node:20-alpine` |
| Python | `python:3.11-slim` |
| Go | `scratch` or `alpine` |
| Java | `eclipse-temurin:17-jre-alpine` |

### Size Comparison

```bash
# Full image
node:20          # ~1GB

# Slim image
node:20-slim     # ~200MB

# Alpine image
node:20-alpine   # ~130MB
```

## Multi-Stage Builds

Remove build dependencies from final image.

```dockerfile
# Build stage - has compilers, dev tools
FROM node:20-alpine AS builder
WORKDIR /app
COPY . .
RUN npm ci && npm run build

# Production stage - minimal
FROM node:20-alpine AS runner
WORKDIR /app
# Only copy what's needed to run
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
CMD ["node", "dist/index.js"]
```

## Pin Image Versions

Avoid `latest` tag in production.

### Wrong

```dockerfile
FROM node:latest
FROM python:latest
```

### Correct

```dockerfile
FROM node:20.10.0-alpine3.18
FROM python:3.11.7-slim-bookworm
```

### Find Exact Version

```bash
docker pull node:20-alpine
docker inspect node:20-alpine | grep -i "RepoDigests"
```

## Health Checks

Add HEALTHCHECK instructions for container health monitoring.

### Node.js/Next.js

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/api/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))" || exit 1
```

### Python/FastAPI

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1
```

### Using curl (if available)

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1
```

**Note:** Health checks help container orchestrators (Docker Compose, Kubernetes) determine if your application is ready to serve traffic.

## Security Scanning

Scan images for vulnerabilities.

### Docker Scout

```bash
docker scout cves myapp:latest
docker scout quickview myapp:latest
```

### Trivy

```bash
trivy image myapp:latest
```

### Snyk

```bash
snyk container test myapp:latest
```

## Read-Only Filesystem

Make filesystem read-only where possible.

```bash
docker run --read-only myapp:latest
```

If app needs to write temp files:

```bash
docker run --read-only --tmpfs /tmp myapp:latest
```

For Next.js applications, also mount the cache directory:

```bash
docker run --read-only --tmpfs /tmp --tmpfs /.next/cache myapp:latest
```

## Drop Capabilities

Remove unnecessary Linux capabilities.

```bash
# Drop all capabilities (recommended for most web apps)
docker run --cap-drop=ALL myapp:latest
```

Add back only what's needed (only if required):

```bash
# NET_BIND_SERVICE only needed for ports below 1024
# Most apps use ports 3000, 8000, etc. so this is rarely needed
docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE myapp:latest
```

**Note:** For typical web applications using ports above 1024 (like 3000 or 8000), `--cap-drop=ALL` alone is sufficient. `NET_BIND_SERVICE` is only required for binding to privileged ports (1-1023).

## Security Checklist

- [ ] Non-root user
- [ ] No secrets in image
- [ ] Minimal base image
- [ ] Multi-stage build
- [ ] Pinned versions
- [ ] Security scan passed
- [ ] Read-only filesystem (if possible)
- [ ] Dropped capabilities
- [ ] No unnecessary packages
- [ ] .dockerignore configured

## Kubernetes Security Context

When deploying to Kubernetes, enforce security:

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1001
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities:
    drop:
      - ALL
```
