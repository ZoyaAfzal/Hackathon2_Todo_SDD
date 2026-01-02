# Helm Template Functions

Essential template patterns for Kubernetes manifest generation.

## Template Basics

### Accessing Values

```yaml
# Direct access
image: {{ .Values.frontend.image.repository }}

# With default
image: {{ .Values.frontend.image.repository | default "nginx" }}

# Nested with default
tag: {{ .Values.frontend.image.tag | default .Values.global.imageTag | default "latest" }}
```

### Including Templates

```yaml
# Include helper template
labels:
  {{- include "myapp.labels" . | nindent 4 }}

# Include with modified context
{{- include "myapp.frontend.labels" (dict "Chart" .Chart "Release" .Release "Values" .Values.frontend) | nindent 4 }}
```

### Control Flow

```yaml
# if/else
{{- if .Values.frontend.enabled }}
# ... frontend resources
{{- end }}

# if/else if/else
{{- if eq .Values.service.type "NodePort" }}
nodePort: {{ .Values.service.nodePort }}
{{- else if eq .Values.service.type "LoadBalancer" }}
# LoadBalancer config
{{- else }}
# ClusterIP (default)
{{- end }}

# with (changes scope)
{{- with .Values.frontend.resources }}
resources:
  {{- toYaml . | nindent 2 }}
{{- end }}
```

### Iteration

```yaml
# range over list
{{- range .Values.frontend.env }}
- name: {{ .name }}
  value: {{ .value | quote }}
{{- end }}

# range over map
{{- range $key, $value := .Values.frontend.env }}
- name: {{ $key }}
  value: {{ $value | quote }}
{{- end }}

# range with index
{{- range $index, $host := .Values.ingress.hosts }}
- host: {{ $host }}
  index: {{ $index }}
{{- end }}
```

## Common Patterns

### Deployment Template

```yaml
{{- if .Values.frontend.enabled -}}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "myapp.fullname" . }}-frontend
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
    app.kubernetes.io/component: frontend
spec:
  replicas: {{ .Values.frontend.replicaCount }}
  selector:
    matchLabels:
      {{- include "myapp.frontend.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "myapp.frontend.selectorLabels" . | nindent 8 }}
    spec:
      {{- with .Values.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
      containers:
        - name: frontend
          image: "{{ .Values.frontend.image.repository }}:{{ .Values.frontend.image.tag | default .Values.global.imageTag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.frontend.image.pullPolicy | default .Values.global.imagePullPolicy | default "IfNotPresent" }}
          ports:
            - name: http
              containerPort: {{ .Values.frontend.service.port }}
              protocol: TCP
          {{- if .Values.frontend.env }}
          env:
            {{- range $key, $value := .Values.frontend.env }}
            - name: {{ $key }}
              value: {{ $value | quote }}
            {{- end }}
          {{- end }}
          livenessProbe:
            httpGet:
              path: /
              port: http
            initialDelaySeconds: 10
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /
              port: http
            initialDelaySeconds: 5
            periodSeconds: 5
          {{- with .Values.frontend.resources }}
          resources:
            {{- toYaml . | nindent 12 }}
          {{- end }}
      {{- with .Values.frontend.nodeSelector }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
{{- end }}
```

### Service Template

```yaml
{{- if .Values.frontend.enabled -}}
apiVersion: v1
kind: Service
metadata:
  name: {{ include "myapp.fullname" . }}-frontend
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
    app.kubernetes.io/component: frontend
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
    {{- include "myapp.frontend.selectorLabels" . | nindent 4 }}
{{- end }}
```

### ConfigMap Template

```yaml
{{- if .Values.frontend.enabled -}}
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "myapp.fullname" . }}-frontend-config
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
data:
  {{- range $key, $value := .Values.frontend.config }}
  {{ $key }}: {{ $value | quote }}
  {{- end }}
{{- end }}
```

### Secret Template

```yaml
{{- if .Values.backend.enabled -}}
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "myapp.fullname" . }}-backend-secret
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
type: Opaque
data:
  {{- range $key, $value := .Values.backend.secrets }}
  {{ $key }}: {{ $value | b64enc | quote }}
  {{- end }}
stringData:
  {{- range $key, $value := .Values.backend.env }}
  {{- if $value }}
  {{ $key }}: {{ $value | quote }}
  {{- end }}
  {{- end }}
{{- end }}
```

## Useful Functions

### String Functions

```yaml
# Quote string
value: {{ .Values.key | quote }}

# Trim whitespace
value: {{ .Values.key | trim }}

# Lowercase/Uppercase
value: {{ .Values.key | lower }}
value: {{ .Values.key | upper }}

# Replace
value: {{ .Values.key | replace "old" "new" }}

# Truncate
name: {{ .Values.name | trunc 63 | trimSuffix "-" }}

# Printf
value: {{ printf "%s-%s" .Release.Name .Chart.Name }}
```

### Encoding Functions

```yaml
# Base64 encode
data:
  password: {{ .Values.password | b64enc }}

# Base64 decode
value: {{ .Values.encoded | b64dec }}

# SHA256 hash
checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
```

### Type Conversion

```yaml
# To YAML (preserves structure)
resources:
  {{- toYaml .Values.resources | nindent 2 }}

# To JSON
config: {{ .Values.config | toJson | quote }}

# To int
replicas: {{ .Values.replicas | int }}

# To string
value: {{ .Values.number | toString }}
```

### Indentation

```yaml
# nindent - newline + indent
labels:
  {{- include "myapp.labels" . | nindent 4 }}

# indent - just indent (no newline)
labels: {{ include "myapp.labels" . | indent 4 }}
```

### Lists

```yaml
# First/Last element
first: {{ first .Values.hosts }}
last: {{ last .Values.hosts }}

# Append/Prepend
{{- $list := append .Values.hosts "new.host.com" }}

# Has (contains)
{{- if has "admin" .Values.roles }}
# ...
{{- end }}

# Without (remove)
{{- $filtered := without .Values.all "excluded" }}
```

### Dictionaries

```yaml
# Create dict
{{- $ctx := dict "key1" "value1" "key2" "value2" }}

# Merge dicts
{{- $merged := merge .Values.defaults .Values.overrides }}

# Get value with default
value: {{ get .Values.map "key" | default "fallback" }}

# Keys
{{- range $key := keys .Values.map }}
- {{ $key }}
{{- end }}
```

## Whitespace Control

```yaml
# Remove leading whitespace
{{- if .Values.enabled }}

# Remove trailing whitespace
{{ if .Values.enabled -}}

# Remove both
{{- if .Values.enabled -}}

# Example: Clean YAML output
metadata:
  name: {{ .Release.Name }}
  {{- if .Values.annotations }}
  annotations:
    {{- toYaml .Values.annotations | nindent 4 }}
  {{- end }}
```

## Debug Techniques

```yaml
# Print value for debugging
{{ .Values.frontend | toYaml }}

# Print type
{{ printf "%T" .Values.frontend }}

# Fail with message
{{ required "DATABASE_URL is required" .Values.backend.env.DATABASE_URL }}

# Debug template
helm template myapp ./myapp --debug
```

## Best Practices

1. **Always quote strings**: Use `{{ .Values.key | quote }}`
2. **Use required for mandatory values**: `{{ required "msg" .Values.key }}`
3. **Provide sensible defaults**: `{{ .Values.key | default "default" }}`
4. **Use nindent for clean YAML**: `{{- toYaml .Values.x | nindent 4 }}`
5. **Define reusable helpers in _helpers.tpl**
6. **Use consistent naming in helpers**
7. **Test with `helm template --debug`**
