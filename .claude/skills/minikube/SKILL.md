---
name: minikube
description: Minikube local Kubernetes cluster operations. Covers cluster management, image loading, service access, troubleshooting, and local development workflows for testing Kubernetes deployments.
---

# Minikube Skill

Local Kubernetes development with Minikube for testing deployments before production.

## Quick Start

### Start Cluster

```powershell
minikube start --driver=docker
```

### Check Status

```powershell
minikube status
```

### Access Dashboard

```powershell
minikube dashboard
```

## Key Concepts

| Concept | Guide |
|---------|-------|
| **Cluster Operations** | [reference/cluster.md](reference/cluster.md) |
| **Image Management** | [reference/images.md](reference/images.md) |
| **Troubleshooting** | [reference/troubleshooting.md](reference/troubleshooting.md) |

## Essential Commands

### Cluster Lifecycle

```powershell
# Start cluster
minikube start --driver=docker

# Stop cluster (preserves state)
minikube stop

# Delete cluster
minikube delete

# Restart cluster
minikube stop
minikube start

# Check status
minikube status
```

### Image Management (CRITICAL)

```powershell
# Load local image into Minikube (REQUIRED for local images)
minikube image load myapp:latest

# List images in Minikube
minikube image ls

# Build image directly in Minikube
minikube image build -t myapp:latest .

# Remove image from Minikube
minikube image rm myapp:latest
```

### Service Access

```powershell
# Get service URL (NodePort services)
minikube service myapp-frontend --url

# Open service in browser
minikube service myapp-frontend

# List all services with URLs
minikube service list

# Tunnel for LoadBalancer services
minikube tunnel
```

### SSH and Filesystem

```powershell
# SSH into Minikube VM
minikube ssh

# Copy file to Minikube
minikube cp local-file.txt /home/docker/file.txt

# Mount local directory
minikube mount /local/path:/minikube/path
```

### Addons

```powershell
# List addons
minikube addons list

# Enable addon
minikube addons enable ingress
minikube addons enable metrics-server
minikube addons enable dashboard

# Disable addon
minikube addons disable ingress
```

## Configuration

### Recommended Settings

```powershell
# Start with custom resources
minikube start --driver=docker --cpus=4 --memory=8192

# With specific Kubernetes version
minikube start --kubernetes-version=v1.28.0
```

### Multiple Profiles

```powershell
# Create named cluster
minikube start -p dev-cluster

# Switch between clusters
minikube profile dev-cluster

# List profiles
minikube profile list

# Delete specific profile
minikube delete -p dev-cluster
```

## Local Development Workflow

### Standard Workflow

```powershell
# 1. Start Minikube
minikube start --driver=docker

# 2. Build Docker images
docker build -t myapp-frontend:latest ./frontend
docker build -t myapp-backend:latest ./backend

# 3. Load images into Minikube (CRITICAL!)
minikube image load myapp-frontend:latest
minikube image load myapp-backend:latest

# 4. Deploy with Helm
helm install myapp ./helm/myapp -f values-secrets.yaml

# 5. Get service URL
minikube service myapp-frontend --url

# 6. Test application
curl $(minikube service myapp-frontend --url)
```

### Rebuild and Redeploy

```powershell
# Rebuild image
docker build -t myapp-frontend:latest ./frontend

# Reload into Minikube
minikube image load myapp-frontend:latest

# Restart deployment to pick up new image
kubectl rollout restart deployment myapp-frontend

# Watch pods restart
kubectl get pods -w
```

## ImagePullPolicy Settings

```yaml
# For local images loaded with `minikube image load`
imagePullPolicy: IfNotPresent   # REQUIRED

# For registry images
imagePullPolicy: Always

# Never pull (for debugging)
imagePullPolicy: Never
```

**CRITICAL**: Use `imagePullPolicy: IfNotPresent` for locally loaded images, otherwise Kubernetes will try to pull from registry.

## Service Types for Minikube

| Type | Use | Access Command |
|------|-----|----------------|
| **NodePort** | External access | `minikube service <name> --url` |
| **ClusterIP** | Internal only | `kubectl port-forward` |
| **LoadBalancer** | With tunnel | `minikube tunnel` |

### NodePort Configuration

```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend
spec:
  type: NodePort
  ports:
    - port: 3000
      targetPort: 3000
      nodePort: 30000   # Fixed port for consistency
  selector:
    app: frontend
```

### LoadBalancer with Tunnel

```powershell
# In separate terminal, keep running
minikube tunnel

# Service will get external IP
kubectl get svc
```

## Useful Information

### Get Cluster Info

```powershell
# Node IP
minikube ip

# Kubernetes version
minikube kubectl -- version

# Docker environment
minikube docker-env
```

### Resource Usage

```powershell
# Check Minikube resources
minikube ssh -- df -h
minikube ssh -- free -m

# Metrics (with metrics-server addon)
kubectl top nodes
kubectl top pods
```

## Debugging

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| ImagePullBackOff | Image not in Minikube | `minikube image load myapp:latest` |
| Service not accessible | Wrong service type | Use NodePort + `minikube service` |
| Cluster won't start | Docker issues | `minikube delete` and restart |
| Out of disk space | Too many images | `minikube ssh -- docker system prune` |

### Check Minikube Logs

```powershell
# Minikube logs
minikube logs

# Follow logs
minikube logs -f

# Specific component
minikube logs --problems
```

### Reset Cluster

```powershell
# Full reset
minikube delete
minikube start --driver=docker

# Just restart (preserves config)
minikube stop
minikube start
```

## Verification Checklist

- [ ] Minikube status shows Running
- [ ] Images loaded (`minikube image ls | grep myapp`)
- [ ] Pods are Running (`kubectl get pods`)
- [ ] Services have endpoints (`kubectl get endpoints`)
- [ ] Service URL works (`minikube service myapp --url`)
- [ ] Application responds to requests

## Integration with Helm

```powershell
# Deploy
helm install myapp ./helm/myapp -f values-secrets.yaml

# Check deployment
kubectl get all

# Get frontend URL
minikube service myapp-frontend --url

# Upgrade after changes
helm upgrade myapp ./helm/myapp -f values-secrets.yaml

# Uninstall
helm uninstall myapp
```

## CRITICAL: CoreDNS External DNS Fix

**Problem**: Pods cannot resolve external hostnames (like Neon PostgreSQL `*.neon.tech`).

**Error**: `getaddrinfo EAI_AGAIN` or DNS lookup timeouts

**Root Cause**: Minikube with Docker driver uses Docker's internal DNS which cannot resolve external hostnames from inside pods.

**Diagnosis**:
```powershell
# This works (from Minikube VM):
minikube ssh "nslookup google.com"

# This fails (from inside pods):
kubectl run dns-test --rm -it --image=busybox -- nslookup google.com
```

**Solution**: Patch CoreDNS to use Google's public DNS (8.8.8.8):

```powershell
# Patch CoreDNS ConfigMap
kubectl patch configmap/coredns -n kube-system --type merge -p '{"data":{"Corefile":".:53 {\n    log\n    errors\n    health {\n       lameduck 5s\n    }\n    ready\n    kubernetes cluster.local in-addr.arpa ip6.arpa {\n       pods insecure\n       fallthrough in-addr.arpa ip6.arpa\n       ttl 30\n    }\n    prometheus :9153\n    hosts {\n       192.168.65.254 host.minikube.internal\n       fallthrough\n    }\n    forward . 8.8.8.8 8.8.4.4 {\n       max_concurrent 1000\n    }\n    cache 30 {\n       disable success cluster.local\n       disable denial cluster.local\n    }\n    loop\n    reload\n    loadbalance\n}\n"}}'

# Restart CoreDNS
kubectl rollout restart deployment/coredns -n kube-system

# Restart application pods to use new DNS
kubectl rollout restart deployment/myapp-frontend deployment/myapp-backend

# Verify DNS works
kubectl run dns-test --rm -it --image=busybox -- nslookup google.com
```

**ALWAYS APPLY THIS FIX** when:
- Using external databases (Neon PostgreSQL, AWS RDS, etc.)
- Connecting to external APIs
- Any external hostname resolution needed

---

## Best Practices

1. **Always load local images**: `minikube image load` before deploying
2. **Use imagePullPolicy: IfNotPresent**: For locally loaded images
3. **Use NodePort for external access**: Most reliable in Minikube
4. **Start fresh when debugging**: `minikube delete && minikube start`
5. **Use profiles for multiple projects**: `minikube start -p myproject`
6. **Enable metrics-server**: For resource monitoring
7. **Fix CoreDNS for external services**: Patch to use 8.8.8.8 (see above)
