# Kubernetes Resources Reference

Complete reference for essential Kubernetes resource types.

## Deployment

Full-featured Deployment manifest:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  labels:
    app: myapp
    app.kubernetes.io/name: myapp
    app.kubernetes.io/instance: myapp
    app.kubernetes.io/version: "1.0.0"
    app.kubernetes.io/component: frontend
    app.kubernetes.io/managed-by: helm
spec:
  replicas: 2
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "3000"
    spec:
      # Security context (pod-level)
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
        runAsGroup: 1001
        fsGroup: 1001

      # Service account
      serviceAccountName: myapp

      # Init containers (run before main containers)
      initContainers:
        - name: wait-for-db
          image: busybox:1.36
          command: ['sh', '-c', 'until nc -z db 5432; do sleep 2; done']

      # Main containers
      containers:
        - name: myapp
          image: myapp:1.0.0
          imagePullPolicy: IfNotPresent

          # Ports
          ports:
            - name: http
              containerPort: 3000
              protocol: TCP

          # Environment variables
          env:
            - name: NODE_ENV
              value: "production"
            - name: POD_NAME
              valueFrom:
                fieldRef:
                  fieldPath: metadata.name

          # Environment from ConfigMap/Secret
          envFrom:
            - configMapRef:
                name: myapp-config
            - secretRef:
                name: myapp-secret

          # Resource limits
          resources:
            requests:
              cpu: 250m
              memory: 256Mi
            limits:
              cpu: 500m
              memory: 512Mi

          # Health probes
          livenessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 15
            periodSeconds: 20
            timeoutSeconds: 5
            failureThreshold: 3

          readinessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 5
            periodSeconds: 10
            timeoutSeconds: 3
            failureThreshold: 3

          # Startup probe - for slow-starting containers
          # Supports same types as liveness/readiness: httpGet, tcpSocket, exec
          startupProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 10
            periodSeconds: 5
            failureThreshold: 30

          # Container security context
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL

          # Volume mounts
          volumeMounts:
            - name: tmp
              mountPath: /tmp
            - name: config
              mountPath: /app/config
              readOnly: true

      # Volumes
      volumes:
        - name: tmp
          emptyDir: {}
        - name: config
          configMap:
            name: myapp-config

      # Node selection
      nodeSelector:
        kubernetes.io/os: linux

      # Tolerations
      tolerations:
        - key: "dedicated"
          operator: "Equal"
          value: "app"
          effect: "NoSchedule"

      # Affinity
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchLabels:
                    app: myapp
                topologyKey: kubernetes.io/hostname
```

## Service

### ClusterIP (Internal)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp
  labels:
    app: myapp
spec:
  type: ClusterIP
  ports:
    - name: http
      port: 3000
      targetPort: http
      protocol: TCP
  selector:
    app: myapp
```

### NodePort (External via Node)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  type: NodePort
  ports:
    - name: http
      port: 3000
      targetPort: http
      nodePort: 30000    # Range: 30000-32767
      protocol: TCP
  selector:
    app: myapp
```

### LoadBalancer (Cloud)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
spec:
  type: LoadBalancer
  ports:
    - name: http
      port: 80
      targetPort: http
      protocol: TCP
  selector:
    app: myapp
```

### Headless Service (StatefulSet)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-headless
spec:
  clusterIP: None
  ports:
    - port: 3000
      targetPort: 3000
  selector:
    app: myapp
```

## ConfigMap

### From Literal Values

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: myapp-config
data:
  API_URL: "http://backend:8000"
  LOG_LEVEL: "info"
  FEATURE_FLAGS: |
    {
      "darkMode": true,
      "newUI": false
    }
```

### From File Content

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: myapp-config
data:
  config.yaml: |
    server:
      port: 3000
      host: 0.0.0.0
    logging:
      level: info
      format: json
```

### Binary Data

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: myapp-binary
binaryData:
  certificate.pem: <base64-encoded-content>
```

## Secret

### Opaque (Generic)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: myapp-secret
type: Opaque
stringData:
  DATABASE_URL: "postgresql://user:pass@host/db"
  API_KEY: "secret-api-key"
```

### Docker Registry

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: regcred
type: kubernetes.io/dockerconfigjson
data:
  .dockerconfigjson: <base64-encoded-docker-config>
```

### TLS Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: tls-secret
type: kubernetes.io/tls
data:
  tls.crt: <base64-encoded-cert>
  tls.key: <base64-encoded-key>
```

## Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
    - hosts:
        - myapp.example.com
      secretName: myapp-tls
  rules:
    - host: myapp.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend
                port:
                  number: 3000
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: backend
                port:
                  number: 8000
```

## HorizontalPodAutoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

## PodDisruptionBudget

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: myapp-pdb
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: myapp
```

## ServiceAccount

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: myapp
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789012:role/myapp-role
```

## NetworkPolicy

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: myapp-network-policy
spec:
  podSelector:
    matchLabels:
      app: myapp
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend
      ports:
        - protocol: TCP
          port: 3000
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: database
      ports:
        - protocol: TCP
          port: 5432
```

## Resource Quantity Reference

### CPU

| Value | Meaning |
|-------|---------|
| 1 | 1 CPU core |
| 1000m | 1 CPU core (millicores) |
| 500m | 0.5 CPU core |
| 100m | 0.1 CPU core |

### Memory

| Value | Meaning |
|-------|---------|
| 1Gi | 1 gibibyte (1024 MiB = 1,073,741,824 bytes) |
| 1G | 1 gigabyte (1000 MB = 1,000,000,000 bytes) |
| 512Mi | 512 mebibytes |
| 256Mi | 256 mebibytes |

**Note:** Binary units (Ki, Mi, Gi) are preferred for Kubernetes as they match how memory is actually allocated. `1Gi` ≠ `1G` (difference of ~7%).

## Label Conventions

### Recommended Labels

```yaml
metadata:
  labels:
    app.kubernetes.io/name: myapp
    app.kubernetes.io/instance: myapp-prod
    app.kubernetes.io/version: "1.0.0"
    app.kubernetes.io/component: frontend
    app.kubernetes.io/part-of: myapp-suite
    app.kubernetes.io/managed-by: helm
```

### Common Custom Labels

```yaml
metadata:
  labels:
    app: myapp
    component: frontend
    environment: production
    tier: web
    team: platform
```
