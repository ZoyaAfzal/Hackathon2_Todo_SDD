# Kubernetes Security Best Practices

Essential security configurations for production Kubernetes deployments.

## Pod Security Context

### Non-Root User (CRITICAL)

```yaml
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1001
    runAsGroup: 1001
    fsGroup: 1001
  containers:
    - name: myapp
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop:
            - ALL
```

### Complete Secure Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  # Pod-level security
  securityContext:
    runAsNonRoot: true
    runAsUser: 1001
    runAsGroup: 1001
    fsGroup: 1001
    seccompProfile:
      type: RuntimeDefault

  # Don't mount service account token automatically
  automountServiceAccountToken: false

  containers:
    - name: app
      image: myapp:1.0.0

      # Container-level security
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop:
            - ALL

      # Resource limits (prevent DoS)
      resources:
        limits:
          cpu: 500m
          memory: 512Mi
        requests:
          cpu: 250m
          memory: 256Mi

      # Writable directories (when readOnlyRootFilesystem: true)
      volumeMounts:
        - name: tmp
          mountPath: /tmp
        - name: cache
          mountPath: /app/.cache

  volumes:
    - name: tmp
      emptyDir: {}
    - name: cache
      emptyDir: {}
```

## Secrets Management

### Never in ConfigMaps

```yaml
# WRONG - secrets in ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: myapp-config
data:
  DATABASE_URL: "postgresql://user:PASSWORD@host/db"  # NEVER!
```

```yaml
# CORRECT - use Secret
apiVersion: v1
kind: Secret
metadata:
  name: myapp-secret
type: Opaque
stringData:
  DATABASE_URL: "postgresql://user:PASSWORD@host/db"
```

### Reference Secrets in Pods

```yaml
# Method 1: envFrom (all keys)
envFrom:
  - secretRef:
      name: myapp-secret

# Method 2: Individual keys
env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: myapp-secret
        key: DATABASE_URL

# Method 3: Volume mount
volumeMounts:
  - name: secrets
    mountPath: /etc/secrets
    readOnly: true
volumes:
  - name: secrets
    secret:
      secretName: myapp-secret
```

### Secret Rotation

```yaml
# Add checksum annotation to trigger rollout on secret change
spec:
  template:
    metadata:
      annotations:
        checksum/secret: {{ include (print $.Template.BasePath "/secret.yaml") . | sha256sum }}
```

## Network Policies

### Default Deny All

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
```

### Allow Specific Traffic

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-policy
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
    - Ingress
    - Egress
  ingress:
    # Allow from frontend only
    - from:
        - podSelector:
            matchLabels:
              app: frontend
      ports:
        - protocol: TCP
          port: 8000
  egress:
    # Allow to database
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - protocol: TCP
          port: 5432
    # Allow DNS
    - to:
        - namespaceSelector: {}
          podSelector:
            matchLabels:
              k8s-app: kube-dns
      ports:
        - protocol: UDP
          port: 53
```

## RBAC (Role-Based Access Control)

### Minimal Service Account

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: myapp
  annotations:
    # Don't auto-mount token
    kubernetes.io/enforce-mountable-secrets: "true"
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: myapp-role
rules:
  # Only what's needed
  - apiGroups: [""]
    resources: ["configmaps"]
    verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: myapp-rolebinding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: myapp-role
subjects:
  - kind: ServiceAccount
    name: myapp
```

### Use Service Account in Pod

```yaml
spec:
  serviceAccountName: myapp
  automountServiceAccountToken: false  # Only mount if needed
```

## Image Security

### Pinned Versions

```yaml
# WRONG
image: nginx:latest

# CORRECT - specific version
image: nginx:1.25.3

# BEST - with digest
image: nginx:1.25.3@sha256:abc123...
```

### Private Registry

```yaml
# Create secret
kubectl create secret docker-registry regcred \
  --docker-server=registry.example.com \
  --docker-username=user \
  --docker-password=pass

# Reference in pod
spec:
  imagePullSecrets:
    - name: regcred
```

### Image Pull Policy

```yaml
# For production
imagePullPolicy: Always

# For local development
imagePullPolicy: IfNotPresent

# For debugging (never for production)
imagePullPolicy: Never
```

## Resource Limits (DoS Prevention)

```yaml
resources:
  # Guaranteed minimum
  requests:
    cpu: 250m
    memory: 256Mi
  # Maximum allowed
  limits:
    cpu: 500m
    memory: 512Mi
```

### LimitRange (Namespace Default)

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
spec:
  limits:
    - default:
        cpu: 500m
        memory: 512Mi
      defaultRequest:
        cpu: 100m
        memory: 128Mi
      type: Container
```

### ResourceQuota (Namespace Limit)

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: namespace-quota
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    pods: "20"
```

## Pod Security Standards

### Restricted (Most Secure)

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: secure-app
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/audit: restricted
```

### Baseline (Minimum Security)

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: standard-app
  labels:
    pod-security.kubernetes.io/enforce: baseline
    pod-security.kubernetes.io/warn: restricted
```

## Security Checklist

### Container Level

- [ ] Non-root user (`runAsNonRoot: true`)
- [ ] Read-only filesystem (`readOnlyRootFilesystem: true`)
- [ ] No privilege escalation (`allowPrivilegeEscalation: false`)
- [ ] All capabilities dropped (`drop: ALL`)
- [ ] Resource limits set
- [ ] Pinned image version

### Pod Level

- [ ] Security context configured
- [ ] Service account token not auto-mounted (if not needed)
- [ ] Minimal service account permissions

### Secrets

- [ ] Secrets in Secret objects, not ConfigMaps
- [ ] values-secrets.yaml in .gitignore
- [ ] No secrets in image layers
- [ ] Secrets mounted read-only

### Network

- [ ] Network policies defined
- [ ] Default deny policy in place
- [ ] Only required traffic allowed

### RBAC

- [ ] Minimal permissions
- [ ] No cluster-admin for apps
- [ ] Service accounts per application

## Verification Commands

```bash
# Check if running as root
kubectl exec <pod> -- id
# Should NOT be uid=0(root)

# Check capabilities
kubectl exec <pod> -- cat /proc/1/status | grep Cap

# Check filesystem
kubectl exec <pod> -- touch /test
# Should fail with read-only filesystem

# Check network policies
kubectl get networkpolicy

# Check resource limits
kubectl describe pod <pod> | grep -A10 "Limits:"
```
