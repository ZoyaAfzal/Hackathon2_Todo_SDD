---
name: helm
description: Helm chart development patterns for Kubernetes deployments. Covers chart structure, values configuration, templates, multi-component applications, and local development with Minikube.
---

# Helm Skill

Production-ready Helm chart patterns for deploying multi-component applications to Kubernetes.

## Quick Start

### Create Chart

```bash
helm create myapp
```

### Install Chart

```bash
helm install myapp ./helm/myapp
```

### Upgrade Release

```bash
helm upgrade myapp ./helm/myapp -f values-secrets.yaml
```

### Uninstall

```bash
helm uninstall myapp
```

## Key Concepts

| Concept | Guide |
|---------|-------|
| **Chart Structure** | [reference/structure.md](reference/structure.md) |
| **Values Design** | [reference/values.md](reference/values.md) |
| **Template Functions** | [reference/templates.md](reference/templates.md) |

## Examples

| Pattern | Guide |
|---------|-------|
| **Multi-Component App** | [examples/multi-component.md](examples/multi-component.md) |
| **Frontend + Backend** | [examples/frontend-backend.md](examples/frontend-backend.md) |

## Chart Structure

```
myapp/
├── Chart.yaml           # Chart metadata
├── values.yaml          # Default configuration
├── values-secrets.yaml  # Secrets (gitignored)
├── templates/
│   ├── _helpers.tpl     # Template helpers
│   ├── deployment.yaml  # Deployment resources
│   ├── service.yaml     # Service resources
│   ├── configmap.yaml   # ConfigMap resources
│   ├── secret.yaml      # Secret resources
│   ├── ingress.yaml     # Optional ingress
│   └── NOTES.txt        # Post-install notes
└── .helmignore          # Files to exclude
```

## Essential Commands

### Development

```bash
# Lint chart
helm lint ./helm/myapp

# Dry-run template rendering
helm template myapp ./helm/myapp

# Dry-run install
helm install myapp ./helm/myapp --dry-run

# Debug template issues
helm template myapp ./helm/myapp --debug
```

### Deployment

```bash
# Install with custom values
helm install myapp ./helm/myapp -f values-secrets.yaml

# Upgrade existing release
helm upgrade myapp ./helm/myapp -f values-secrets.yaml

# Install or upgrade (idempotent)
helm upgrade --install myapp ./helm/myapp -f values-secrets.yaml

# List releases
helm list

# Get release status
helm status myapp
```

### Debugging

```bash
# View rendered templates
helm get manifest myapp

# View release history
helm history myapp

# Rollback to previous
helm rollback myapp 1
```

## Chart.yaml Template

```yaml
apiVersion: v2
name: myapp
description: A Helm chart for MyApp
type: application
version: 0.1.0
appVersion: "1.0.0"

maintainers:
  - name: Your Name
    email: you@example.com

keywords:
  - webapp
  - fullstack
```

## Values.yaml Pattern

```yaml
# Global settings
global:
  imageTag: latest
  imagePullPolicy: IfNotPresent

# Frontend configuration
frontend:
  enabled: true
  replicaCount: 1
  image:
    repository: myapp-frontend
    tag: ""  # Uses global.imageTag if empty
  service:
    type: NodePort
    port: 3000
    nodePort: 30000
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 250m
      memory: 256Mi

# Backend configuration
backend:
  enabled: true
  replicaCount: 1
  image:
    repository: myapp-backend
    tag: ""
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
  env:
    DATABASE_URL: ""  # Set in values-secrets.yaml
```

## Helper Functions (_helpers.tpl)

```yaml
{{/*
Expand the name of the chart.
*/}}
{{- define "myapp.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version for labels.
*/}}
{{- define "myapp.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "myapp.labels" -}}
helm.sh/chart: {{ include "myapp.chart" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels for frontend
*/}}
{{- define "myapp.frontend.selectorLabels" -}}
app.kubernetes.io/name: {{ include "myapp.name" . }}-frontend
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Selector labels for backend
*/}}
{{- define "myapp.backend.selectorLabels" -}}
app.kubernetes.io/name: {{ include "myapp.name" . }}-backend
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

## Secrets Management

### values-secrets.yaml (gitignored)

```yaml
backend:
  env:
    DATABASE_URL: "postgresql://user:pass@host:5432/db"
    BETTER_AUTH_SECRET: "your-secret-here"
    GROQ_API_KEY: "your-api-key"
```

### .gitignore entry

```
values-secrets.yaml
*-secrets.yaml
```

## Chart Validation

```bash
# Lint chart for errors
helm lint ./helm/myapp

# Render templates locally (dry-run)
helm template myapp ./helm/myapp

# Dry-run install with debug
helm install myapp ./helm/myapp --dry-run --debug

# Validate against cluster (requires connection)
helm install myapp ./helm/myapp --dry-run --debug --validate
```

## Verification Checklist

- [ ] `helm lint` passes
- [ ] `helm template` renders correctly
- [ ] No hardcoded secrets in templates
- [ ] values-secrets.yaml in .gitignore
- [ ] NOTES.txt provides useful post-install info
- [ ] Resource limits defined
- [ ] Health checks configured
- [ ] Labels follow Kubernetes conventions

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Template syntax error | Missing quotes or brackets | Use `helm template --debug` |
| Values not applied | Wrong path in template | Check `{{ .Values.path }}` |
| Release stuck | Previous failed install | `helm uninstall myapp` first |
| Secrets in git | Missing gitignore | Add `values-secrets.yaml` |
