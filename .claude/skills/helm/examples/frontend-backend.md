# Frontend + Backend Helm Pattern

Complete Helm chart for deploying a Next.js frontend with FastAPI backend.

## Chart Structure

```
lifestepsai/
├── Chart.yaml
├── values.yaml
├── values-secrets.yaml      # gitignored
├── templates/
│   ├── _helpers.tpl
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── backend-secret.yaml
│   └── NOTES.txt
└── .helmignore
```

## Chart.yaml

```yaml
apiVersion: v2
name: lifestepsai
description: LifeStepsAI - AI-powered todo application
type: application
version: 0.1.0
appVersion: "1.0.0"
```

## values.yaml

```yaml
# Global settings
global:
  imageTag: latest
  imagePullPolicy: IfNotPresent

# Frontend (Next.js)
frontend:
  enabled: true
  replicaCount: 1

  image:
    repository: lifestepsai-frontend
    tag: ""

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

  env:
    NEXT_PUBLIC_API_URL: "http://lifestepsai-backend:8000"

# Backend (FastAPI)
backend:
  enabled: true
  replicaCount: 1

  image:
    repository: lifestepsai-backend
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
    DATABASE_URL: ""           # Set in values-secrets.yaml
    BETTER_AUTH_SECRET: ""     # Set in values-secrets.yaml
    GROQ_API_KEY: ""           # Set in values-secrets.yaml
    CORS_ORIGINS: "http://localhost:30000"
```

## values-secrets.yaml (gitignored)

```yaml
backend:
  env:
    DATABASE_URL: "postgresql://user:password@neon-host/dbname?sslmode=require"
    BETTER_AUTH_SECRET: "your-32-char-secret-here"
    GROQ_API_KEY: "gsk_your_groq_api_key"
```

## templates/_helpers.tpl

```yaml
{{/*
Expand the name of the chart.
*/}}
{{- define "lifestepsai.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "lifestepsai.fullname" -}}
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
{{- define "lifestepsai.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "lifestepsai.labels" -}}
helm.sh/chart: {{ include "lifestepsai.chart" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
{{- end }}

{{/*
Frontend selector labels
*/}}
{{- define "lifestepsai.frontend.selectorLabels" -}}
app.kubernetes.io/name: {{ include "lifestepsai.name" . }}-frontend
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
Backend selector labels
*/}}
{{- define "lifestepsai.backend.selectorLabels" -}}
app.kubernetes.io/name: {{ include "lifestepsai.name" . }}-backend
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/component: backend
{{- end }}

{{/*
Get image tag with fallbacks
*/}}
{{- define "lifestepsai.imageTag" -}}
{{- .tag | default .global.imageTag | default $.Chart.AppVersion | default "latest" }}
{{- end }}
```

## templates/frontend-deployment.yaml

```yaml
{{- if .Values.frontend.enabled -}}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "lifestepsai.fullname" . }}-frontend
  labels:
    {{- include "lifestepsai.labels" . | nindent 4 }}
    {{- include "lifestepsai.frontend.selectorLabels" . | nindent 4 }}
spec:
  replicas: {{ .Values.frontend.replicaCount }}
  selector:
    matchLabels:
      {{- include "lifestepsai.frontend.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "lifestepsai.frontend.selectorLabels" . | nindent 8 }}
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
        fsGroup: 1001
      containers:
        - name: frontend
          image: "{{ .Values.frontend.image.repository }}:{{ .Values.frontend.image.tag | default .Values.global.imageTag | default "latest" }}"
          imagePullPolicy: {{ .Values.global.imagePullPolicy }}
          ports:
            - name: http
              containerPort: 3000
              protocol: TCP
          env:
            {{- range $key, $value := .Values.frontend.env }}
            {{- if $value }}
            - name: {{ $key }}
              value: {{ $value | quote }}
            {{- end }}
            {{- end }}
          livenessProbe:
            httpGet:
              path: /
              port: http
            initialDelaySeconds: 15
            periodSeconds: 20
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /
              port: http
            initialDelaySeconds: 5
            periodSeconds: 10
            timeoutSeconds: 3
            failureThreshold: 3
          resources:
            {{- toYaml .Values.frontend.resources | nindent 12 }}
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
      {{- with .Values.frontend.nodeSelector }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
{{- end }}
```

## templates/frontend-service.yaml

```yaml
{{- if .Values.frontend.enabled -}}
apiVersion: v1
kind: Service
metadata:
  name: {{ include "lifestepsai.fullname" . }}-frontend
  labels:
    {{- include "lifestepsai.labels" . | nindent 4 }}
    {{- include "lifestepsai.frontend.selectorLabels" . | nindent 4 }}
spec:
  type: {{ .Values.frontend.service.type }}
  ports:
    - port: {{ .Values.frontend.service.port }}
      targetPort: http
      protocol: TCP
      name: http
      {{- if and (eq .Values.frontend.service.type "NodePort") .Values.frontend.service.nodePort }}
      nodePort: {{ .Values.frontend.service.nodePort }}
      {{- end }}
  selector:
    {{- include "lifestepsai.frontend.selectorLabels" . | nindent 4 }}
{{- end }}
```

## templates/backend-deployment.yaml

```yaml
{{- if .Values.backend.enabled -}}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "lifestepsai.fullname" . }}-backend
  labels:
    {{- include "lifestepsai.labels" . | nindent 4 }}
    {{- include "lifestepsai.backend.selectorLabels" . | nindent 4 }}
spec:
  replicas: {{ .Values.backend.replicaCount }}
  selector:
    matchLabels:
      {{- include "lifestepsai.backend.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "lifestepsai.backend.selectorLabels" . | nindent 8 }}
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 10001
        fsGroup: 10001
      containers:
        - name: backend
          image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag | default .Values.global.imageTag | default "latest" }}"
          imagePullPolicy: {{ .Values.global.imagePullPolicy }}
          ports:
            - name: http
              containerPort: 8000
              protocol: TCP
          envFrom:
            - secretRef:
                name: {{ include "lifestepsai.fullname" . }}-backend-secret
          env:
            - name: CORS_ORIGINS
              value: {{ .Values.backend.env.CORS_ORIGINS | quote }}
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
          resources:
            {{- toYaml .Values.backend.resources | nindent 12 }}
          securityContext:
            allowPrivilegeEscalation: false
            capabilities:
              drop:
                - ALL
      {{- with .Values.backend.nodeSelector }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
{{- end }}
```

## templates/backend-service.yaml

```yaml
{{- if .Values.backend.enabled -}}
apiVersion: v1
kind: Service
metadata:
  name: {{ include "lifestepsai.fullname" . }}-backend
  labels:
    {{- include "lifestepsai.labels" . | nindent 4 }}
    {{- include "lifestepsai.backend.selectorLabels" . | nindent 4 }}
spec:
  type: {{ .Values.backend.service.type }}
  ports:
    - port: {{ .Values.backend.service.port }}
      targetPort: http
      protocol: TCP
      name: http
  selector:
    {{- include "lifestepsai.backend.selectorLabels" . | nindent 4 }}
{{- end }}
```

## templates/backend-secret.yaml

```yaml
{{- if .Values.backend.enabled -}}
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "lifestepsai.fullname" . }}-backend-secret
  labels:
    {{- include "lifestepsai.labels" . | nindent 4 }}
type: Opaque
stringData:
  DATABASE_URL: {{ required "backend.env.DATABASE_URL is required" .Values.backend.env.DATABASE_URL | quote }}
  BETTER_AUTH_SECRET: {{ required "backend.env.BETTER_AUTH_SECRET is required" .Values.backend.env.BETTER_AUTH_SECRET | quote }}
  {{- if .Values.backend.env.GROQ_API_KEY }}
  GROQ_API_KEY: {{ .Values.backend.env.GROQ_API_KEY | quote }}
  {{- end }}
{{- end }}
```

## templates/NOTES.txt

```
=================================================================
  LifeStepsAI has been deployed!
=================================================================

Release: {{ .Release.Name }}
Namespace: {{ .Release.Namespace }}

{{- if .Values.frontend.enabled }}

FRONTEND:
---------
{{- if eq .Values.frontend.service.type "NodePort" }}
  Access URL: http://<node-ip>:{{ .Values.frontend.service.nodePort }}

  With Minikube:
    minikube service {{ include "lifestepsai.fullname" . }}-frontend --url
{{- else if eq .Values.frontend.service.type "LoadBalancer" }}
  Get the LoadBalancer IP:
    kubectl get svc {{ include "lifestepsai.fullname" . }}-frontend -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
{{- end }}
{{- end }}

{{- if .Values.backend.enabled }}

BACKEND:
--------
  Internal URL: http://{{ include "lifestepsai.fullname" . }}-backend:{{ .Values.backend.service.port }}

  Test health endpoint:
    kubectl run curl --rm -it --restart=Never --image=curlimages/curl -- \
      curl http://{{ include "lifestepsai.fullname" . }}-backend:{{ .Values.backend.service.port }}/health
{{- end }}

USEFUL COMMANDS:
----------------
  # Check pod status
  kubectl get pods -l "app.kubernetes.io/instance={{ .Release.Name }}"

  # View frontend logs
  kubectl logs -l "app.kubernetes.io/component=frontend"

  # View backend logs
  kubectl logs -l "app.kubernetes.io/component=backend"

  # Port-forward backend (for debugging)
  kubectl port-forward svc/{{ include "lifestepsai.fullname" . }}-backend 8000:8000

=================================================================
```

## Deployment Commands

```bash
# Build Docker images first
docker build -t lifestepsai-frontend:latest ./frontend
docker build -t lifestepsai-backend:latest ./backend

# Load into Minikube
minikube image load lifestepsai-frontend:latest
minikube image load lifestepsai-backend:latest

# Install chart
helm install lifestepsai ./helm/lifestepsai -f ./helm/lifestepsai/values-secrets.yaml

# Get frontend URL
minikube service lifestepsai-frontend --url

# Upgrade after changes
helm upgrade lifestepsai ./helm/lifestepsai -f ./helm/lifestepsai/values-secrets.yaml

# Uninstall
helm uninstall lifestepsai
```

## Verification

```bash
# Check all resources
kubectl get all -l "app.kubernetes.io/instance=lifestepsai"

# Watch pods start
kubectl get pods -w

# Check pod logs
kubectl logs -l "app.kubernetes.io/component=backend" -f

# Test backend from cluster
kubectl run curl --rm -it --restart=Never --image=curlimages/curl -- \
  curl http://lifestepsai-backend:8000/health
```
