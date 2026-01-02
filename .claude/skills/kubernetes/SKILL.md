---
name: kubernetes
description: Kubernetes deployment patterns and operations. Covers resource manifests, debugging, monitoring, and production best practices for deploying containerized applications.
---

# Kubernetes Skill

Essential Kubernetes patterns for deploying and managing containerized applications.

## Quick Start

### Apply Resources

```bash
kubectl apply -f deployment.yaml
```

### Check Status

```bash
kubectl get pods
kubectl get services
```

### View Logs

```bash
kubectl logs <pod-name>
kubectl logs -l app=myapp
```

## Key Concepts

| Concept | Guide |
|---------|-------|
| **Resources** | [reference/resources.md](reference/resources.md) |
| **Debugging** | [reference/debugging.md](reference/debugging.md) |
| **Security** | [reference/security.md](reference/security.md) |

## Essential Resources

### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  labels:
    app: myapp
spec:
  replicas: 1
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
        - name: myapp
          image: myapp:latest
          ports:
            - containerPort: 3000
          resources:
            limits:
              cpu: 500m
              memory: 512Mi
            requests:
              cpu: 250m
              memory: 256Mi
```

### Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  type: ClusterIP
  ports:
    - port: 3000
      targetPort: 3000
  selector:
    app: myapp
```

### ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: myapp-config
data:
  API_URL: "http://backend:8000"
  LOG_LEVEL: "info"
```

### Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: myapp-secret
type: Opaque
stringData:
  DATABASE_URL: "postgresql://user:pass@host/db"
  API_KEY: "secret-key"
```

## Service Types

| Type | Use Case | Access |
|------|----------|--------|
| **ClusterIP** | Internal services | Within cluster only |
| **NodePort** | Local dev/testing | `<node-ip>:<node-port>` |
| **LoadBalancer** | Cloud production | External IP |

### NodePort Example

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
      nodePort: 30000    # 30000-32767
  selector:
    app: frontend
```

## Health Probes

```yaml
containers:
  - name: myapp
    image: myapp:latest
    livenessProbe:
      httpGet:
        path: /health
        port: 3000
      initialDelaySeconds: 15
      periodSeconds: 20
    readinessProbe:
      httpGet:
        path: /health
        port: 3000
      initialDelaySeconds: 5
      periodSeconds: 10
```

## Essential Commands

### Pods

```bash
# List pods
kubectl get pods
kubectl get pods -o wide
kubectl get pods -w              # Watch

# Describe pod
kubectl describe pod <pod-name>

# Logs
kubectl logs <pod-name>
kubectl logs <pod-name> -f       # Follow
kubectl logs -l app=myapp        # By label

# Execute in pod
kubectl exec -it <pod-name> -- /bin/sh
```

### Deployments

```bash
# List deployments
kubectl get deployments

# Scale
kubectl scale deployment myapp --replicas=3

# Restart
kubectl rollout restart deployment myapp

# Rollback
kubectl rollout undo deployment myapp
```

### Services

```bash
# List services
kubectl get services
kubectl get svc

# Describe service
kubectl describe svc myapp

# Get endpoints
kubectl get endpoints myapp
```

### Debugging

```bash
# Get all resources
kubectl get all

# Events
kubectl get events --sort-by='.lastTimestamp'

# Test DNS from pod
kubectl run curl --rm -it --restart=Never --image=curlimages/curl -- \
  curl http://myapp:3000/health

# Port forward
kubectl port-forward svc/myapp 3000:3000
```

## Labels and Selectors

### Apply Labels

```yaml
metadata:
  labels:
    app: myapp
    component: frontend
    environment: production
```

### Select by Label

```bash
kubectl get pods -l app=myapp
kubectl get pods -l "app=myapp,component=frontend"
kubectl delete pods -l app=myapp
```

## Resource Limits Guidelines

| Component | CPU Request | CPU Limit | Memory Request | Memory Limit |
|-----------|-------------|-----------|----------------|--------------|
| Frontend | 250m | 500m | 256Mi | 512Mi |
| Backend | 500m | 1000m | 512Mi | 1Gi |
| Worker | 100m | 500m | 128Mi | 256Mi |

## Common Patterns

### Environment from Secret

```yaml
envFrom:
  - secretRef:
      name: myapp-secret
```

### Environment from ConfigMap

```yaml
envFrom:
  - configMapRef:
      name: myapp-config
```

### Mixed Environment

```yaml
env:
  - name: API_URL
    valueFrom:
      configMapKeyRef:
        name: myapp-config
        key: API_URL
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: myapp-secret
        key: DATABASE_URL
```

## Verification Checklist

- [ ] Pods reach Running state
- [ ] No restarts (check RESTARTS column)
- [ ] Health probes pass
- [ ] Service endpoints exist
- [ ] Logs show no errors
- [ ] Can reach service from within cluster
- [ ] External access works (if applicable)

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| ImagePullBackOff | Image not found | Check image name/tag, load locally |
| CrashLoopBackOff | App crashes | Check logs, env vars, config |
| Pending | No resources | Check node resources |
| No endpoints | Selector mismatch | Compare pod labels to service selector |
