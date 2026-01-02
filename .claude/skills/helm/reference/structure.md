# Helm Chart Structure

Complete guide to Helm chart directory layout and file purposes.

## Directory Layout

```
myapp/
├── Chart.yaml           # Required: Chart metadata
├── Chart.lock           # Generated: Dependency lock file
├── values.yaml          # Required: Default configuration
├── values-secrets.yaml  # Optional: Secrets (gitignored)
├── values.schema.json   # Optional: JSON Schema for values validation
├── .helmignore          # Optional: Files to exclude from packaging
├── charts/              # Optional: Dependency charts
├── crds/                # Optional: Custom Resource Definitions
├── templates/           # Required: Kubernetes manifest templates
│   ├── NOTES.txt        # Optional: Post-install notes
│   ├── _helpers.tpl     # Required: Template helper functions
│   ├── deployment.yaml  # Deployment resources
│   ├── service.yaml     # Service resources
│   ├── configmap.yaml   # ConfigMap resources
│   ├── secret.yaml      # Secret resources
│   ├── ingress.yaml     # Ingress resources
│   ├── hpa.yaml         # HorizontalPodAutoscaler
│   └── tests/           # Helm test hooks
│       └── test-connection.yaml
└── .helmignore          # Files to exclude from package
```

## Chart.yaml

The chart manifest file.

```yaml
# Required fields
apiVersion: v2                    # v2 for Helm 3
name: myapp                       # Chart name
version: 0.1.0                    # SemVer chart version

# Recommended fields
description: A Helm chart for MyApp
type: application                 # application or library
appVersion: "1.0.0"              # App version (informational)

# Optional fields
kubeVersion: ">=1.21.0"          # Required K8s version
keywords:
  - webapp
  - fullstack
home: https://github.com/org/myapp
sources:
  - https://github.com/org/myapp
maintainers:
  - name: Your Name
    email: you@example.com
    url: https://yoursite.com
icon: https://example.com/icon.png
deprecated: false

# Dependencies (optional)
dependencies:
  - name: postgresql
    version: "12.x.x"
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled
```

## values.yaml

Default configuration values.

```yaml
# Naming
nameOverride: ""
fullnameOverride: ""

# Global settings (inherited by subcharts)
global:
  imageTag: latest
  imagePullPolicy: IfNotPresent
  storageClass: ""

# Component: Frontend
frontend:
  enabled: true
  replicaCount: 1

  image:
    repository: myapp-frontend
    tag: ""                       # Empty uses global.imageTag
    pullPolicy: ""                # Empty uses global.imagePullPolicy

  service:
    type: NodePort
    port: 3000
    nodePort: 30000               # Only for NodePort type

  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 250m
      memory: 256Mi

  env:
    NEXT_PUBLIC_API_URL: ""       # Set at deploy time

  nodeSelector: {}
  tolerations: []
  affinity: {}

# Component: Backend
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

  env:
    DATABASE_URL: ""              # REQUIRED: Set in values-secrets.yaml
    BETTER_AUTH_SECRET: ""        # REQUIRED: Set in values-secrets.yaml
    CORS_ORIGINS: ""

# Service Account
serviceAccount:
  create: true
  annotations: {}
  name: ""

# Ingress (optional)
ingress:
  enabled: false
  className: ""
  annotations: {}
  hosts:
    - host: myapp.local
      paths:
        - path: /
          pathType: Prefix
  tls: []
```

## templates/_helpers.tpl

Reusable template functions.

```yaml
{{/*
Expand the name of the chart.
*/}}
{{- define "myapp.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "myapp.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "myapp.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "myapp.labels" -}}
helm.sh/chart: {{ include "myapp.chart" . }}
{{ include "myapp.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "myapp.selectorLabels" -}}
app.kubernetes.io/name: {{ include "myapp.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "myapp.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "myapp.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Get image tag, defaulting to global or Chart.AppVersion
*/}}
{{- define "myapp.imageTag" -}}
{{- .tag | default .global.imageTag | default $.Chart.AppVersion }}
{{- end }}
```

## templates/NOTES.txt

Post-installation instructions shown to user.

```
Thank you for installing {{ .Chart.Name }}!

Your release is named: {{ .Release.Name }}

{{- if .Values.frontend.enabled }}

=== Frontend ===

{{- if contains "NodePort" .Values.frontend.service.type }}
  Access the frontend at:

  export NODE_PORT=$(kubectl get --namespace {{ .Release.Namespace }} -o jsonpath="{.spec.ports[0].nodePort}" services {{ include "myapp.fullname" . }}-frontend)
  export NODE_IP=$(kubectl get nodes --namespace {{ .Release.Namespace }} -o jsonpath="{.items[0].status.addresses[0].address}")
  echo http://$NODE_IP:$NODE_PORT

  Or with Minikube:
  minikube service {{ include "myapp.fullname" . }}-frontend --url
{{- end }}
{{- end }}

{{- if .Values.backend.enabled }}

=== Backend ===

  Backend is accessible within the cluster at:
  http://{{ include "myapp.fullname" . }}-backend:{{ .Values.backend.service.port }}

  To test the health endpoint from within the cluster:
  kubectl run curl --rm -it --restart=Never --image=curlimages/curl -- \
    curl http://{{ include "myapp.fullname" . }}-backend:{{ .Values.backend.service.port }}/health
{{- end }}

=== Useful Commands ===

  # Check pod status
  kubectl get pods -l "app.kubernetes.io/instance={{ .Release.Name }}"

  # View logs
  kubectl logs -l "app.kubernetes.io/instance={{ .Release.Name }}" --all-containers

  # Uninstall
  helm uninstall {{ .Release.Name }}
```

## .helmignore

Files to exclude from chart package.

```
# Patterns to ignore when building packages.
.git
.gitignore
.DS_Store

# IDE
.vscode/
.idea/

# CI/CD
.github/
.gitlab-ci.yml
Jenkinsfile

# Testing
*.test.yaml
tests/

# Documentation (optional - include if needed)
README.md
docs/

# Secrets
*-secrets.yaml
*.secret
.env*

# Build artifacts
*.tgz
```

## File Naming Conventions

| File | Purpose |
|------|---------|
| `deployment.yaml` | Main Deployment resource |
| `frontend-deployment.yaml` | Frontend-specific Deployment |
| `backend-deployment.yaml` | Backend-specific Deployment |
| `service.yaml` | Service resources |
| `configmap.yaml` | ConfigMap resources |
| `secret.yaml` | Secret resources |
| `ingress.yaml` | Ingress resources |
| `hpa.yaml` | HorizontalPodAutoscaler |
| `pdb.yaml` | PodDisruptionBudget |
| `networkpolicy.yaml` | NetworkPolicy |
| `serviceaccount.yaml` | ServiceAccount |
| `role.yaml` | RBAC Role |
| `rolebinding.yaml` | RBAC RoleBinding |
