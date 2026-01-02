# Minikube Cluster Operations

Complete reference for managing Minikube clusters.

## Cluster Lifecycle

### Start Cluster

```powershell
# Default start
minikube start

# With Docker driver (recommended for Windows)
minikube start --driver=docker

# With custom resources
minikube start --driver=docker --cpus=4 --memory=8192

# With specific Kubernetes version
minikube start --driver=docker --kubernetes-version=v1.28.0

# With container runtime
minikube start --driver=docker --container-runtime=containerd
```

### Stop Cluster

```powershell
# Stop (preserves cluster state)
minikube stop
```

### Delete Cluster

```powershell
# Delete default cluster
minikube delete

# Delete all clusters
minikube delete --all

# Delete specific profile
minikube delete -p my-cluster
```

### Restart Cluster

```powershell
minikube stop
minikube start
```

## Cluster Status

### Check Status

```powershell
# Overall status
minikube status

# Expected output:
# minikube
# type: Control Plane
# host: Running
# kubelet: Running
# apiserver: Running
# kubeconfig: Configured
```

### Get Cluster Info

```powershell
# Node IP address
minikube ip

# Kubernetes version
minikube kubectl -- version --short

# Cluster info
minikube kubectl -- cluster-info

# Node details
minikube kubectl -- get nodes -o wide
```

## Profiles (Multiple Clusters)

### Create Named Cluster

```powershell
# Create new cluster with profile name
minikube start -p dev-cluster

# Create another
minikube start -p test-cluster
```

### Switch Between Clusters

```powershell
# Set active profile
minikube profile dev-cluster

# Check current profile
minikube profile

# List all profiles
minikube profile list
```

### Delete Profile

```powershell
minikube delete -p test-cluster
```

## Configuration

### View Configuration

```powershell
# Current config
minikube config view

# Specific setting
minikube config get memory
```

### Set Defaults

```powershell
# Set default memory
minikube config set memory 8192

# Set default CPUs
minikube config set cpus 4

# Set default driver
minikube config set driver docker

# Set default Kubernetes version
minikube config set kubernetes-version v1.28.0
```

**Alternative:** Pass options directly to `minikube start`:
```powershell
minikube start --memory=8192 --cpus=4 --driver=docker
```

### Unset Configuration

```powershell
minikube config unset memory
```

## Resource Allocation

### Recommended Settings by Use Case

| Use Case | CPUs | Memory | Command |
|----------|------|--------|---------|
| Minimal testing | 2 | 2GB | `minikube start --cpus=2 --memory=2048` |
| Standard dev | 4 | 4GB | `minikube start --cpus=4 --memory=4096` |
| Full-stack app | 4 | 8GB | `minikube start --cpus=4 --memory=8192` |
| Heavy workload | 6 | 12GB | `minikube start --cpus=6 --memory=12288` |

### Check Allocated Resources

```powershell
# Memory
minikube ssh -- free -m

# Disk
minikube ssh -- df -h

# CPU
minikube ssh -- nproc
```

## Networking

### Get Node IP

```powershell
minikube ip
```

### Service Access

```powershell
# NodePort service URL
minikube service myapp --url

# Open in browser
minikube service myapp

# List all services
minikube service list
```

### Port Forwarding

```powershell
# Forward local port to service
kubectl port-forward svc/myapp 8080:80
```

### Tunnel (LoadBalancer Support)

```powershell
# Enable LoadBalancer support (run in separate terminal)
minikube tunnel

# Now LoadBalancer services get external IPs
kubectl get svc
```

## Addons

### List Available Addons

```powershell
minikube addons list
```

### Common Addons

| Addon | Purpose | Command |
|-------|---------|---------|
| dashboard | Web UI | `minikube addons enable dashboard` |
| ingress | Ingress controller | `minikube addons enable ingress` |
| ingress-dns | DNS for ingress | `minikube addons enable ingress-dns` |
| metrics-server | Resource metrics | `minikube addons enable metrics-server` |
| registry | Local registry | `minikube addons enable registry` |
| storage-provisioner | Dynamic PVs | Enabled by default |

### Enable/Disable Addons

```powershell
# Enable
minikube addons enable metrics-server

# Disable
minikube addons disable metrics-server

# Enable with configuration
minikube addons enable ingress --alsologtostderr
```

### Open Dashboard

```powershell
# Enable and open
minikube dashboard

# Just get URL
minikube dashboard --url
```

## SSH Access

### SSH into Node

```powershell
# Interactive shell
minikube ssh

# Run command
minikube ssh -- ls -la

# Check Docker
minikube ssh -- docker ps
```

### Copy Files

```powershell
# Copy to Minikube
minikube cp myfile.txt /home/docker/myfile.txt

# Copy from Minikube
minikube cp /home/docker/myfile.txt myfile.txt
```

### Mount Local Directory

```powershell
# Mount (runs in foreground)
minikube mount C:\Users\me\data:/data

# Use in pod
volumeMounts:
  - mountPath: /data
    name: host-mount
volumes:
  - name: host-mount
    hostPath:
      path: /data
```

## Logs and Debugging

### View Logs

```powershell
# All logs
minikube logs

# Follow logs
minikube logs -f

# Specific node (multi-node)
minikube logs -n minikube-m02

# Problem logs
minikube logs --problems
```

### Debug Start Issues

```powershell
# Verbose output
minikube start --alsologtostderr -v=2

# Very verbose
minikube start --alsologtostderr -v=7
```

## Multi-Node Clusters

### Create Multi-Node Cluster

```powershell
# 3 node cluster
minikube start --nodes 3

# Add node to existing cluster
minikube node add

# Delete node
minikube node delete minikube-m02

# List nodes
minikube node list
```

## Cleanup

### Free Disk Space

```powershell
# Prune Docker in Minikube
minikube ssh -- docker system prune -a

# Clear image cache
minikube ssh -- docker image prune -a
```

### Full Reset

```powershell
# Delete everything
minikube delete --all --purge

# Start fresh
minikube start --driver=docker
```

## Environment Variables

### Docker Environment

```powershell
# Get Docker env commands
minikube docker-env

# Use Minikube's Docker daemon (PowerShell)
& minikube -p minikube docker-env --shell powershell | Invoke-Expression
```

### kubectl Context

```powershell
# Verify kubectl context
kubectl config current-context

# Should show: minikube
```

## Health Checks

### Verify Cluster Health

```powershell
# Status check
minikube status

# Component health
kubectl get componentstatuses

# Node health
kubectl get nodes

# System pods
kubectl get pods -n kube-system
```

### Expected Healthy State

```
minikube status
# minikube
# type: Control Plane
# host: Running
# kubelet: Running
# apiserver: Running
# kubeconfig: Configured

kubectl get nodes
# NAME       STATUS   ROLES           AGE   VERSION
# minikube   Ready    control-plane   10m   v1.28.0
```
