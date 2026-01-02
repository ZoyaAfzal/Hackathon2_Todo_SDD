# Kubernetes Debugging Guide

Systematic approach to diagnosing and fixing Kubernetes deployment issues.

## Debugging Decision Tree

```
Pod Issue?
├── Pod not created?
│   └── Check: kubectl describe deployment <name>
│       └── Look for: ReplicaSet issues, quota limits
│
├── Pod stuck in Pending?
│   └── Check: kubectl describe pod <name>
│       ├── Insufficient resources → Scale down or add nodes
│       ├── No matching nodes → Check nodeSelector/affinity
│       ├── Volume not bound → Check PVC status
│       └── ImagePullSecrets → Check secret exists
│
├── Pod stuck in ContainerCreating?
│   └── Check: kubectl describe pod <name>
│       ├── Volume mount issues → Check PV/PVC
│       ├── ConfigMap/Secret missing → Create them
│       └── Image pulling → Wait or check registry
│
├── ImagePullBackOff?
│   └── Check: kubectl describe pod <name>
│       ├── Image doesn't exist → Verify image:tag
│       ├── Private registry → Add imagePullSecrets
│       └── Local image → Load into cluster
│
├── CrashLoopBackOff?
│   └── Check: kubectl logs <pod> --previous
│       ├── Missing env var → Check ConfigMap/Secret
│       ├── Database connection → Verify DATABASE_URL
│       ├── Permission denied → Check securityContext
│       └── App error → Fix application code
│
└── Running but not working?
    ├── Check logs: kubectl logs <pod>
    ├── Check service: kubectl get endpoints
    ├── Test from cluster: kubectl exec curl...
    └── Port forward: kubectl port-forward
```

## Essential Debugging Commands

### Pod Status

```bash
# List pods with details
kubectl get pods -o wide

# Watch pods in real-time
kubectl get pods -w

# Describe pod (shows events)
kubectl describe pod <pod-name>

# Get pod YAML
kubectl get pod <pod-name> -o yaml
```

### Logs

```bash
# Current logs
kubectl logs <pod-name>

# Previous container logs (after crash)
kubectl logs <pod-name> --previous

# Follow logs
kubectl logs <pod-name> -f

# All containers in pod
kubectl logs <pod-name> --all-containers

# Logs by label
kubectl logs -l app=myapp

# Last N lines
kubectl logs <pod-name> --tail=100

# Since time
kubectl logs <pod-name> --since=1h
```

### Events

```bash
# All events (sorted)
kubectl get events --sort-by='.lastTimestamp'

# Events for specific pod
kubectl get events --field-selector involvedObject.name=<pod-name>

# Watch events
kubectl get events -w
```

### Exec into Pod

```bash
# Shell access
kubectl exec -it <pod-name> -- /bin/sh

# Run specific command
kubectl exec <pod-name> -- ls -la /app

# Specific container (multi-container pod)
kubectl exec -it <pod-name> -c <container-name> -- /bin/sh
```

### Network Debugging

```bash
# Test service from within cluster
kubectl run curl --rm -it --restart=Never --image=curlimages/curl -- \
  curl http://myapp:3000/health

# DNS lookup
kubectl run dns --rm -it --restart=Never --image=busybox -- \
  nslookup myapp

# Check endpoints
kubectl get endpoints myapp

# Port forward for local testing
kubectl port-forward svc/myapp 3000:3000
kubectl port-forward pod/<pod-name> 3000:3000
```

## Common Issues and Fixes

### ImagePullBackOff

**Symptoms:**
```
NAME     READY   STATUS             RESTARTS   AGE
myapp    0/1     ImagePullBackOff   0          1m
```

**Diagnosis:**
```bash
kubectl describe pod myapp | grep -A5 "Events:"
```

**Common Causes:**

1. **Image doesn't exist:**
   ```bash
   # Verify image exists
   docker images | grep myapp

   # For local development with Minikube
   minikube image load myapp:latest
   ```

2. **Wrong image tag:**
   ```yaml
   # Fix: Use correct tag
   image: myapp:latest  # Not myapp:v1.0.0 if that doesn't exist
   ```

3. **Private registry without credentials:**
   ```yaml
   # Add imagePullSecrets
   spec:
     imagePullSecrets:
       - name: regcred
   ```

### CrashLoopBackOff

**Symptoms:**
```
NAME     READY   STATUS             RESTARTS   AGE
myapp    0/1     CrashLoopBackOff   5          5m
```

**Diagnosis:**
```bash
# Check current logs
kubectl logs myapp

# Check logs from crashed container
kubectl logs myapp --previous

# Check environment
kubectl describe pod myapp | grep -A20 "Environment:"
```

**Common Causes:**

1. **Missing environment variable:**
   ```bash
   # Error: DATABASE_URL is not set
   # Fix: Add to ConfigMap or Secret
   ```

2. **Database connection failed:**
   ```bash
   # Error: Connection refused to localhost:5432
   # Fix: Use Kubernetes service name
   DATABASE_URL: "postgresql://user:pass@postgres:5432/db"
   ```

3. **Permission denied:**
   ```yaml
   # Fix: Add writable directory
   volumeMounts:
     - name: tmp
       mountPath: /tmp
   volumes:
     - name: tmp
       emptyDir: {}
   ```

4. **Health check fails:**
   ```yaml
   # Fix: Increase initialDelaySeconds
   livenessProbe:
     initialDelaySeconds: 30  # Give app time to start
   ```

### Pending State

**Symptoms:**
```
NAME     READY   STATUS    RESTARTS   AGE
myapp    0/1     Pending   0          5m
```

**Diagnosis:**
```bash
kubectl describe pod myapp | grep -A10 "Events:"
```

**Common Causes:**

1. **Insufficient resources:**
   ```bash
   # Check node resources
   kubectl describe nodes | grep -A5 "Allocated resources"

   # Fix: Reduce requests or add nodes
   ```

2. **Node selector mismatch:**
   ```yaml
   # Remove or fix nodeSelector
   nodeSelector:
     kubernetes.io/os: linux  # Make sure nodes have this label
   ```

3. **PVC not bound:**
   ```bash
   kubectl get pvc
   # Fix: Create matching PV or use dynamic provisioning
   ```

### Service Not Accessible

**Symptoms:**
- curl times out
- Connection refused
- No route to host

**Diagnosis:**
```bash
# Check service exists
kubectl get svc myapp

# Check endpoints (should show pod IPs)
kubectl get endpoints myapp

# If no endpoints, selector doesn't match
kubectl get pods --show-labels
kubectl describe svc myapp | grep Selector
```

**Common Fixes:**

1. **Selector mismatch:**
   ```yaml
   # Service selector
   selector:
     app: myapp    # Must match pod labels

   # Pod labels
   metadata:
     labels:
       app: myapp  # Must match service selector
   ```

2. **Pod not ready:**
   ```bash
   # Check readiness probe
   kubectl describe pod myapp | grep -A5 "Readiness:"
   ```

3. **Wrong port:**
   ```yaml
   # Service
   ports:
     - port: 3000
       targetPort: 3000  # Must match container port

   # Container
   ports:
     - containerPort: 3000
   ```

### Debugging Network Issues

```bash
# 1. Verify pod is running
kubectl get pods -l app=myapp

# 2. Check service has endpoints
kubectl get endpoints myapp

# 3. Test from within cluster
kubectl run debug --rm -it --restart=Never --image=busybox -- sh

# Inside debug pod:
# DNS test
nslookup myapp
# Should return: myapp.<namespace>.svc.cluster.local

# HTTP test
wget -qO- http://myapp:3000/health

# 4. Test from outside cluster (port-forward)
kubectl port-forward svc/myapp 3000:3000
# Then: curl http://localhost:3000
```

## Resource Debugging

### Check Resource Usage

```bash
# Pod resource usage (requires metrics-server)
kubectl top pods

# Node resource usage
kubectl top nodes

# Detailed pod resources
kubectl describe pod myapp | grep -A10 "Limits:"
```

### OOMKilled

**Symptoms:**
```
State:          Terminated
Reason:         OOMKilled
```

**Fix:**
```yaml
# Increase memory limit
resources:
  limits:
    memory: 1Gi  # Increase from 512Mi
  requests:
    memory: 512Mi
```

## Debugging Checklist

### Pre-Deployment

- [ ] Image exists and is accessible
- [ ] ConfigMaps and Secrets created
- [ ] Resource limits are reasonable
- [ ] Health endpoints exist in application
- [ ] Service selectors match pod labels

### Post-Deployment

- [ ] Pods reach Running state
- [ ] No restarts in RESTARTS column
- [ ] Endpoints exist for services
- [ ] Logs show no errors
- [ ] Health probes pass
- [ ] Can reach service from within cluster

### Production Readiness

- [ ] Resource limits set
- [ ] Liveness and readiness probes configured
- [ ] Multiple replicas for HA
- [ ] PodDisruptionBudget created
- [ ] Logs being collected
- [ ] Metrics being scraped
