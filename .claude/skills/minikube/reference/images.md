# Minikube Image Management

Essential guide for working with container images in Minikube.

## Understanding Image Loading

Minikube runs its own Docker daemon inside the VM/container. **Local Docker images are NOT automatically available in Minikube**. You must explicitly load them.

```
┌─────────────────────────────────────────────┐
│ Host Machine                                │
│  ┌─────────────────────────────┐            │
│  │ Docker Desktop              │            │
│  │  - myapp:latest             │            │
│  └─────────────────────────────┘            │
│           │                                 │
│           │ minikube image load             │
│           ▼                                 │
│  ┌─────────────────────────────┐            │
│  │ Minikube VM/Container       │            │
│  │  ┌─────────────────────────┐│            │
│  │  │ Minikube Docker         ││            │
│  │  │  - myapp:latest         ││  ← K8s    │
│  │  └─────────────────────────┘│    pulls  │
│  └─────────────────────────────┘            │
└─────────────────────────────────────────────┘
```

## Loading Images

### Load Local Image (Most Common)

```powershell
# Load from local Docker
minikube image load myapp:latest

# Load multiple images
minikube image load myapp-frontend:latest
minikube image load myapp-backend:latest
```

### Verify Image Loaded

```powershell
# List images in Minikube
minikube image ls

# Filter for your image
minikube image ls | findstr myapp
```

### Build Inside Minikube

```powershell
# Build directly in Minikube's Docker
minikube image build -t myapp:latest .

# Build from specific Dockerfile
minikube image build -t myapp:latest -f Dockerfile.prod .
```

### Build Inside Minikube

```powershell
# Build image directly in Minikube's Docker daemon
minikube image build -t myapp:latest .

# Build from specific directory
minikube image build -t myapp:latest ./frontend
```

### Use Minikube's Docker Daemon

```powershell
# Point shell to Minikube's Docker
& minikube docker-env --shell powershell | Invoke-Expression

# Now docker commands use Minikube's daemon
docker build -t myapp:latest .
docker images  # Shows Minikube's images

# Reset to local Docker
& minikube docker-env -u --shell powershell | Invoke-Expression
```

## Image Pull Policy

**CRITICAL**: Set correct `imagePullPolicy` for locally loaded images.

### For Local Images

```yaml
# REQUIRED for images loaded with `minikube image load`
containers:
  - name: myapp
    image: myapp:latest
    imagePullPolicy: IfNotPresent   # Don't try to pull
```

### For Registry Images

```yaml
# For images from registries
containers:
  - name: myapp
    image: docker.io/myuser/myapp:latest
    imagePullPolicy: Always
```

### Policy Reference

| Policy | When to Use | Behavior |
|--------|-------------|----------|
| `IfNotPresent` | Local images | Uses local, only pulls if missing |
| `Always` | Registry images | Always pulls latest |
| `Never` | Debugging only | Never pulls, fails if missing |

## Workflow: Build and Deploy

### Standard Workflow

```powershell
# 1. Build image locally
docker build -t myapp-frontend:latest ./frontend
docker build -t myapp-backend:latest ./backend

# 2. Load into Minikube
minikube image load myapp-frontend:latest
minikube image load myapp-backend:latest

# 3. Verify loaded
minikube image ls | findstr myapp

# 4. Deploy (ensure imagePullPolicy: IfNotPresent)
kubectl apply -f deployment.yaml
# or
helm install myapp ./helm/myapp
```

### Rebuild and Redeploy

```powershell
# 1. Rebuild
docker build -t myapp-frontend:latest ./frontend

# 2. Reload into Minikube
minikube image load myapp-frontend:latest

# 3. Restart deployment (forces new image)
kubectl rollout restart deployment myapp-frontend

# 4. Watch rollout
kubectl rollout status deployment myapp-frontend
```

### Using Image Tags

```powershell
# Use specific tags for versioning
docker build -t myapp:v1.0.0 .
minikube image load myapp:v1.0.0

# Update deployment to use new tag
kubectl set image deployment/myapp myapp=myapp:v1.0.0
```

## Managing Images

### Remove Image

```powershell
# Remove from Minikube
minikube image rm myapp:latest

# Remove from local Docker
docker rmi myapp:latest
```

### List Images

```powershell
# All images in Minikube
minikube image ls

# With more details
minikube ssh -- docker images

# Filter
minikube ssh -- docker images | grep myapp
```

### Pull from Registry to Minikube

```powershell
# Pull directly into Minikube
minikube image pull nginx:latest
```

## Troubleshooting

### ImagePullBackOff

**Symptoms:**
```
NAME     READY   STATUS             RESTARTS   AGE
myapp    0/1     ImagePullBackOff   0          1m
```

**Solutions:**

1. **Image not loaded:**
   ```powershell
   # Check if image exists
   minikube image ls | findstr myapp

   # If not, load it
   minikube image load myapp:latest
   ```

2. **Wrong imagePullPolicy:**
   ```yaml
   # Change from:
   imagePullPolicy: Always

   # To:
   imagePullPolicy: IfNotPresent
   ```

3. **Wrong image name/tag:**
   ```powershell
   # Check exact name in Minikube
   minikube image ls

   # Update deployment with correct name
   kubectl set image deployment/myapp myapp=myapp:latest
   ```

### ErrImagePull

**Symptoms:**
```
Failed to pull image "myapp:latest": rpc error: code = Unknown
```

**Cause:** Kubernetes trying to pull from registry instead of local.

**Solution:**
```yaml
imagePullPolicy: IfNotPresent  # or Never
```

### Image Out of Date

**Symptoms:** Old code running after rebuild.

**Solution:**
```powershell
# Reload image
minikube image load myapp:latest

# Force pod recreation
kubectl rollout restart deployment myapp

# Or delete pods
kubectl delete pods -l app=myapp
```

### Image Too Large to Load

**Symptoms:** Load command hangs or fails.

**Solutions:**

1. **Increase Minikube resources:**
   ```powershell
   minikube stop
   minikube start --memory=8192 --disk-size=50g
   ```

2. **Clean up Minikube:**
   ```powershell
   minikube ssh -- docker system prune -a
   ```

3. **Reduce image size:**
   - Use multi-stage builds
   - Use slim base images
   - Remove unnecessary files

## Best Practices

1. **Always use `imagePullPolicy: IfNotPresent`** for local images
2. **Use specific tags** instead of `latest` for production
3. **Reload after every rebuild**: `minikube image load` after `docker build`
4. **Verify image loaded**: Check with `minikube image ls`
5. **Use image digests** for immutability in production
6. **Clean up regularly**: `minikube ssh -- docker system prune`

## Quick Reference

| Action | Command |
|--------|---------|
| Load image | `minikube image load myapp:latest` |
| List images | `minikube image ls` |
| Remove image | `minikube image rm myapp:latest` |
| Build in Minikube | `minikube image build -t myapp:latest .` |
| Pull to Minikube | `minikube image pull nginx:latest` |
| Use Minikube Docker | `& minikube docker-env --shell powershell \| Invoke-Expression` |
