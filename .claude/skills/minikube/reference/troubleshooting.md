# Minikube Troubleshooting Guide

Systematic solutions for common Minikube issues.

## Diagnostic Commands

### Quick Health Check

```powershell
# 1. Minikube status
minikube status

# 2. Kubernetes nodes
kubectl get nodes

# 3. System pods
kubectl get pods -n kube-system

# 4. Recent events
kubectl get events --sort-by='.lastTimestamp'
```

### Detailed Diagnostics

```powershell
# Minikube logs
minikube logs

# Problem logs
minikube logs --problems

# Verbose logs
minikube logs -v=7
```

## Startup Issues

### Cluster Won't Start

**Symptoms:**
```
minikube start
❌  Exiting due to...
```

**Solutions:**

1. **Clean start:**
   ```powershell
   minikube delete
   minikube start --driver=docker
   ```

2. **Docker not running:**
   ```powershell
   # Check Docker status
   docker info

   # Start Docker Desktop, then retry
   minikube start --driver=docker
   ```

3. **Insufficient resources:**
   ```powershell
   # Start with minimal resources
   minikube start --driver=docker --memory=2048 --cpus=2
   ```

4. **VPN/Proxy interference:**
   ```powershell
   # Disconnect VPN, then
   minikube delete
   minikube start --driver=docker
   ```

### Timeout During Start

**Symptoms:**
```
❌  Unable to connect to the cluster
```

**Solutions:**

```powershell
# 1. Delete and restart
minikube delete
minikube start --driver=docker

# 2. With more time
minikube start --wait=10m

# 3. Check Docker resources
# Increase Docker Desktop memory/CPU in settings
```

### Docker Driver Issues (Windows)

**Symptoms:**
```
❌  Exiting due to PROVIDER_DOCKER_NOT_RUNNING
```

**Solutions:**

1. Ensure Docker Desktop is running
2. Check Docker Desktop settings → WSL 2 backend enabled
3. Restart Docker Desktop
4. Restart Windows

## Image Issues

### ImagePullBackOff

**Symptoms:**
```
NAME     STATUS             RESTARTS   AGE
myapp    ImagePullBackOff   0          2m
```

**Diagnosis:**
```powershell
kubectl describe pod <pod-name> | Select-String -Pattern "Failed|Error" -Context 0,3
```

**Solutions:**

1. **Load local image:**
   ```powershell
   minikube image load myapp:latest
   ```

2. **Fix imagePullPolicy:**
   ```yaml
   imagePullPolicy: IfNotPresent  # Not Always
   ```

3. **Verify image name:**
   ```powershell
   # Check exact name
   minikube image ls | findstr myapp

   # Must match deployment exactly
   ```

### ErrImageNeverPull

**Symptoms:**
```
Container image "myapp:latest" is not present with pull policy of Never
```

**Solution:**
```powershell
minikube image load myapp:latest
```

## Network Issues

### Service Not Accessible

**Symptoms:**
- `minikube service` returns error
- Connection refused from host

**Diagnosis:**
```powershell
# Check service exists
kubectl get svc

# Check endpoints
kubectl get endpoints

# Check pods are running
kubectl get pods
```

**Solutions:**

1. **Service type wrong:**
   ```yaml
   # Change ClusterIP to NodePort
   spec:
     type: NodePort
   ```

2. **No endpoints:**
   ```powershell
   # Check pod labels match service selector
   kubectl get pods --show-labels
   kubectl describe svc myapp | Select-String "Selector"
   ```

3. **Pods not ready:**
   ```powershell
   # Wait for pods
   kubectl get pods -w
   ```

### minikube service Hangs

**Symptoms:**
- Command never returns
- Browser doesn't open

**Solutions:**

```powershell
# 1. Get URL directly
minikube service myapp --url

# 2. Use kubectl port-forward instead
kubectl port-forward svc/myapp 3000:3000
```

### Tunnel Not Working

**Symptoms:**
- LoadBalancer stays `<pending>`
- Tunnel exits immediately

**Solutions:**

```powershell
# 1. Run tunnel with admin privileges
# Start PowerShell as Administrator
minikube tunnel

# 2. Check for port conflicts
netstat -an | findstr ":80"
```

## Resource Issues

### Out of Memory

**Symptoms:**
- Pods being evicted
- OOMKilled status
- Cluster becomes unresponsive

**Solutions:**

```powershell
# 1. Restart with more memory
minikube stop
minikube start --memory=8192

# 2. Delete and recreate
minikube delete
minikube start --driver=docker --memory=8192

# 3. Reduce pod resource requests
```

### Out of Disk Space

**Symptoms:**
- Cannot pull images
- Pods stuck in Pending

**Diagnosis:**
```powershell
minikube ssh -- df -h
```

**Solutions:**

```powershell
# 1. Prune Docker in Minikube
minikube ssh -- docker system prune -a -f

# 2. Remove unused images
minikube ssh -- docker image prune -a -f

# 3. Recreate with more disk
minikube delete
minikube start --disk-size=50g
```

## Kubectl Issues

### kubectl Not Configured

**Symptoms:**
```
Unable to connect to the server
```

**Solutions:**

```powershell
# 1. Check context
kubectl config current-context

# 2. Use minikube's kubectl
minikube kubectl -- get pods

# 3. Update kubeconfig
minikube update-context
```

### Wrong Context

**Symptoms:**
- kubectl commands affect wrong cluster
- Resources not found

**Solution:**
```powershell
# Set context to minikube
kubectl config use-context minikube

# Verify
kubectl config current-context
```

## Pod Issues

### CrashLoopBackOff

**Symptoms:**
```
NAME     STATUS             RESTARTS   AGE
myapp    CrashLoopBackOff   5          5m
```

**Diagnosis:**
```powershell
# Check logs
kubectl logs <pod-name>
kubectl logs <pod-name> --previous

# Check events
kubectl describe pod <pod-name>
```

**Common Causes:**
1. Missing environment variables
2. Database connection failed
3. Health check failing
4. Application error

### Pending State

**Symptoms:**
```
NAME     STATUS    AGE
myapp    Pending   5m
```

**Diagnosis:**
```powershell
kubectl describe pod <pod-name> | Select-String -Pattern "Warning|Error" -Context 0,2
```

**Common Causes:**
1. Insufficient resources
2. Node selector mismatch
3. PVC not bound

## Performance Issues

### Slow Cluster

**Solutions:**

1. **Increase resources:**
   ```powershell
   minikube stop
   minikube start --cpus=4 --memory=8192
   ```

2. **Disable addons not needed:**
   ```powershell
   minikube addons disable dashboard
   minikube addons disable metrics-server
   ```

3. **Clean up:**
   ```powershell
   minikube ssh -- docker system prune -a -f
   ```

### Slow Image Loading

**Solutions:**

```powershell
# 1. Build directly in Minikube
minikube image build -t myapp:latest .

# 2. Use Minikube's Docker daemon
& minikube docker-env --shell powershell | Invoke-Expression
docker build -t myapp:latest .
```

## Complete Reset

When all else fails:

```powershell
# 1. Delete everything
minikube delete --all --purge

# 2. Clean Docker (optional)
docker system prune -a -f

# 3. Fresh start
minikube start --driver=docker --cpus=4 --memory=8192

# 4. Reload images
docker build -t myapp:latest .
minikube image load myapp:latest
```

## Verification Checklist

After troubleshooting, verify:

- [ ] `minikube status` shows all Running
- [ ] `kubectl get nodes` shows Ready
- [ ] `kubectl get pods -n kube-system` all Running
- [ ] `minikube image ls | findstr myapp` shows your images
- [ ] `kubectl get pods` shows Running (not Pending/Error)
- [ ] `minikube service myapp --url` returns accessible URL
- [ ] Application responds to requests

## Quick Fixes Reference

| Issue | Quick Fix |
|-------|-----------|
| Won't start | `minikube delete && minikube start` |
| ImagePullBackOff | `minikube image load myapp:latest` |
| Service not accessible | Change to `type: NodePort` |
| Out of memory | `minikube start --memory=8192` |
| Out of disk | `minikube ssh -- docker system prune -a -f` |
| Wrong kubectl context | `kubectl config use-context minikube` |
| Tunnel not working | Run PowerShell as Administrator |
