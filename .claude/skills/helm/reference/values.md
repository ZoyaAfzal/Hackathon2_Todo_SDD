# Helm Values Design

Best practices for structuring values.yaml for maintainable Helm charts.

## Values Hierarchy

```yaml
# Global settings (inherited by all components)
global:
  imageTag: latest
  imagePullPolicy: IfNotPresent
  storageClass: ""

# Component-specific settings
frontend:
  enabled: true
  image:
    repository: myapp-frontend
    tag: ""  # Falls back to global.imageTag

backend:
  enabled: true
  image:
    repository: myapp-backend
    tag: ""
```

## Complete values.yaml Template

```yaml
# =============================================================================
# Global Configuration
# =============================================================================
global:
  # Default image tag for all components
  imageTag: latest

  # Default image pull policy
  imagePullPolicy: IfNotPresent

  # Storage class for PVCs (empty = default)
  storageClass: ""

# =============================================================================
# Frontend (Next.js)
# =============================================================================
frontend:
  # Enable/disable this component
  enabled: true

  # Number of replicas
  replicaCount: 1

  # Image configuration
  image:
    repository: myapp-frontend
    tag: ""                        # Uses global.imageTag if empty
    pullPolicy: ""                 # Uses global.imagePullPolicy if empty

  # Service configuration
  service:
    type: NodePort                 # ClusterIP, NodePort, LoadBalancer
    port: 3000
    nodePort: 30000                # Only for NodePort (30000-32767)

  # Resource limits
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 250m
      memory: 256Mi

  # Environment variables (non-sensitive)
  env:
    NEXT_PUBLIC_API_URL: ""

  # Health probes
  probes:
    liveness:
      enabled: true
      path: /
      initialDelaySeconds: 15
      periodSeconds: 20
    readiness:
      enabled: true
      path: /
      initialDelaySeconds: 5
      periodSeconds: 10

  # Node placement
  nodeSelector: {}
  tolerations: []
  affinity: {}

# =============================================================================
# Backend (FastAPI)
# =============================================================================
backend:
  enabled: true
  replicaCount: 1

  image:
    repository: myapp-backend
    tag: ""
    pullPolicy: ""

  service:
    type: ClusterIP
    port: 8000

  resources:
    limits:
      cpu: 1000m
      memory: 1Gi
    requests:
      cpu: 500m
      memory: 512Mi

  # Environment variables (configure in values-secrets.yaml)
  env:
    DATABASE_URL: ""               # REQUIRED
    BETTER_AUTH_SECRET: ""         # REQUIRED
    GROQ_API_KEY: ""              # Optional
    CORS_ORIGINS: ""

  probes:
    liveness:
      enabled: true
      path: /health
      initialDelaySeconds: 15
      periodSeconds: 20
    readiness:
      enabled: true
      path: /health
      initialDelaySeconds: 5
      periodSeconds: 10

  nodeSelector: {}
  tolerations: []
  affinity: {}

# =============================================================================
# Common Configuration
# =============================================================================

# Naming overrides
nameOverride: ""
fullnameOverride: ""

# Image pull secrets for private registries
imagePullSecrets: []
# - name: regcred

# Service account
serviceAccount:
  create: true
  annotations: {}
  name: ""

# Pod security context
podSecurityContext:
  runAsNonRoot: true
  runAsUser: 1001
  fsGroup: 1001

# Container security context
securityContext:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop:
      - ALL

# =============================================================================
# Ingress (Optional)
# =============================================================================
ingress:
  enabled: false
  className: ""
  annotations: {}
    # kubernetes.io/ingress.class: nginx
    # cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: myapp.local
      paths:
        - path: /
          pathType: Prefix
          service: frontend
        - path: /api
          pathType: Prefix
          service: backend
  tls: []
  # - secretName: myapp-tls
  #   hosts:
  #     - myapp.local
```

## Secrets Management

### values-secrets.yaml (gitignored)

```yaml
# This file should NEVER be committed to git
# Copy from values-secrets.yaml.example

backend:
  env:
    DATABASE_URL: "postgresql://user:password@host:5432/db?sslmode=require"
    BETTER_AUTH_SECRET: "your-32-character-secret-here"
    GROQ_API_KEY: "gsk_your_api_key_here"
```

### values-secrets.yaml.example (committed)

```yaml
# Copy this file to values-secrets.yaml and fill in values
# DO NOT commit values-secrets.yaml to git

backend:
  env:
    DATABASE_URL: ""           # PostgreSQL connection string
    BETTER_AUTH_SECRET: ""     # 32+ character secret
    GROQ_API_KEY: ""          # Groq API key (optional)
```

### .gitignore Entry

```
# Helm secrets
values-secrets.yaml
*-secrets.yaml
```

## Accessing Values in Templates

### Direct Access

```yaml
replicas: {{ .Values.frontend.replicaCount }}
```

### With Default

```yaml
image: {{ .Values.frontend.image.repository }}:{{ .Values.frontend.image.tag | default .Values.global.imageTag }}
```

### Conditional

```yaml
{{- if .Values.frontend.enabled }}
# ... frontend resources
{{- end }}
```

### Iteration

```yaml
env:
{{- range $key, $value := .Values.backend.env }}
{{- if $value }}
  - name: {{ $key }}
    value: {{ $value | quote }}
{{- end }}
{{- end }}
```

### Required Values

```yaml
# Fail if not provided
DATABASE_URL: {{ required "backend.env.DATABASE_URL is required" .Values.backend.env.DATABASE_URL | quote }}
```

## Environment-Specific Values

### values-dev.yaml

```yaml
global:
  imageTag: dev

frontend:
  replicaCount: 1
  service:
    type: NodePort
    nodePort: 30000

backend:
  replicaCount: 1
```

### values-prod.yaml

```yaml
global:
  imageTag: v1.0.0

frontend:
  replicaCount: 3
  service:
    type: LoadBalancer

backend:
  replicaCount: 3
  resources:
    limits:
      cpu: 2000m
      memory: 2Gi
```

### Usage

```bash
# Development
helm install myapp ./helm/myapp -f values-dev.yaml -f values-secrets.yaml

# Production
helm install myapp ./helm/myapp -f values-prod.yaml -f values-secrets.yaml
```

## Value Override Order

1. `values.yaml` (default)
2. Parent chart's values
3. `-f values-override.yaml`
4. `--set key=value`

Later overrides win:

```bash
helm install myapp ./helm/myapp \
  -f values.yaml \           # Base defaults
  -f values-prod.yaml \      # Production overrides
  -f values-secrets.yaml \   # Secrets
  --set frontend.replicaCount=5  # CLI override (highest priority)
```

## Validation

### Schema (values.schema.json)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["backend"],
  "properties": {
    "backend": {
      "type": "object",
      "required": ["env"],
      "properties": {
        "env": {
          "type": "object",
          "required": ["DATABASE_URL", "BETTER_AUTH_SECRET"],
          "properties": {
            "DATABASE_URL": {
              "type": "string",
              "minLength": 1
            },
            "BETTER_AUTH_SECRET": {
              "type": "string",
              "minLength": 32
            }
          }
        }
      }
    }
  }
}
```

### Test Values

```bash
# Lint with values
helm lint ./helm/myapp -f values-secrets.yaml

# Dry-run template
helm template myapp ./helm/myapp -f values-secrets.yaml

# Debug output
helm template myapp ./helm/myapp -f values-secrets.yaml --debug
```

## Best Practices

1. **Document all values** - Add comments explaining each option
2. **Provide sensible defaults** - Chart should work with minimal config
3. **Use required()** - For mandatory values without defaults
4. **Separate secrets** - Keep in gitignored values-secrets.yaml
5. **Provide examples** - Create values-secrets.yaml.example
6. **Validate with schema** - Add values.schema.json
7. **Test all combinations** - Verify enabled/disabled flags work
