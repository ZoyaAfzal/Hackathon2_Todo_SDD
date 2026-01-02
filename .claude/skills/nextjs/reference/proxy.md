# Next.js 16 proxy.ts Reference

## Overview

Next.js 16 introduces `proxy.ts` to replace `middleware.ts`. The proxy runs on Node.js runtime (not Edge), providing access to Node.js APIs.

## Key Differences from middleware.ts

| Feature | middleware.ts (old) | proxy.ts (new) |
|---------|---------------------|----------------|
| Runtime | Edge | Node.js |
| Function name | `middleware()` | `proxy()` |
| Node.js APIs | Limited | Full access |
| File location | Root or src/ | app/ directory |

## Basic proxy.ts

```typescript
// app/proxy.ts
import { NextRequest, NextResponse } from "next/server";

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Your proxy logic here
  return NextResponse.next();
}

export const config = {
  matcher: [
    // Match all paths except static files
    "/((?!_next/static|_next/image|favicon.ico).*)",
  ],
};
```

## Authentication Proxy

```typescript
// app/proxy.ts
import { NextRequest, NextResponse } from "next/server";

const publicPaths = ["/", "/login", "/register", "/api/auth"];
const protectedPaths = ["/dashboard", "/settings", "/api/tasks"];

function isPublicPath(pathname: string): boolean {
  return publicPaths.some(
    (path) => pathname === path || pathname.startsWith(`${path}/`)
  );
}

function isProtectedPath(pathname: string): boolean {
  return protectedPaths.some(
    (path) => pathname === path || pathname.startsWith(`${path}/`)
  );
}

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Get session token from cookies
  const sessionToken = request.cookies.get("better-auth.session_token");

  // Redirect authenticated users away from auth pages
  if (sessionToken && (pathname === "/login" || pathname === "/register")) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  // Redirect unauthenticated users to login
  if (!sessionToken && isProtectedPath(pathname)) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("callbackUrl", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/settings/:path*",
    "/login",
    "/register",
    "/api/tasks/:path*",
  ],
};
```

## Adding Headers

```typescript
export function proxy(request: NextRequest) {
  const response = NextResponse.next();

  // Add security headers
  response.headers.set("X-Frame-Options", "DENY");
  response.headers.set("X-Content-Type-Options", "nosniff");
  response.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");

  return response;
}
```

## Geolocation & IP

```typescript
export function proxy(request: NextRequest) {
  const geo = request.geo;
  const ip = request.ip;

  console.log(`Request from ${geo?.country} (${ip})`);

  // Block certain countries
  if (geo?.country === "XX") {
    return new NextResponse("Access denied", { status: 403 });
  }

  return NextResponse.next();
}
```

## Rate Limiting Pattern

```typescript
import { NextRequest, NextResponse } from "next/server";

const rateLimit = new Map<string, { count: number; timestamp: number }>();
const WINDOW_MS = 60 * 1000; // 1 minute
const MAX_REQUESTS = 100;

export function proxy(request: NextRequest) {
  if (request.nextUrl.pathname.startsWith("/api/")) {
    const ip = request.ip ?? "anonymous";
    const now = Date.now();
    const record = rateLimit.get(ip);

    if (record && now - record.timestamp < WINDOW_MS) {
      if (record.count >= MAX_REQUESTS) {
        return new NextResponse("Too many requests", { status: 429 });
      }
      record.count++;
    } else {
      rateLimit.set(ip, { count: 1, timestamp: now });
    }
  }

  return NextResponse.next();
}
```

## Rewrite & Redirect

```typescript
export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Rewrite (internal - URL doesn't change)
  if (pathname === "/old-page") {
    return NextResponse.rewrite(new URL("/new-page", request.url));
  }

  // Redirect (external - URL changes)
  if (pathname === "/blog") {
    return NextResponse.redirect(new URL("https://blog.example.com"));
  }

  return NextResponse.next();
}
```

## Conditional Proxy

```typescript
export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Only run for specific paths
  if (!pathname.startsWith("/api/") && !pathname.startsWith("/dashboard/")) {
    return NextResponse.next();
  }

  // Your logic here
  return NextResponse.next();
}
```

## Matcher Patterns

```typescript
export const config = {
  matcher: [
    // Match single path
    "/dashboard",

    // Match with wildcard
    "/dashboard/:path*",

    // Match multiple paths
    "/api/:path*",

    // Exclude static files
    "/((?!_next/static|_next/image|favicon.ico).*)",

    // Match specific file types
    "/(.*)\\.json",
  ],
};
```

## Reading Request Body

```typescript
export async function proxy(request: NextRequest) {
  if (request.method === "POST") {
    const body = await request.json();
    console.log("Request body:", body);
  }

  return NextResponse.next();
}
```

## Setting Cookies

```typescript
export function proxy(request: NextRequest) {
  const response = NextResponse.next();

  response.cookies.set("visited", "true", {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    maxAge: 60 * 60 * 24 * 7, // 1 week
  });

  return response;
}
```

## CRITICAL: Runtime API Proxy for Kubernetes

### The Problem

**DO NOT use `rewrites()` in `next.config.js` for Kubernetes deployments!**

`rewrites()` reads environment variables at **BUILD TIME**, not runtime. This means:
- When you build the Docker image, `BACKEND_URL` gets baked into the image
- Kubernetes ConfigMaps inject env vars at **runtime** (pod startup)
- The rewrite rules are already frozen from build time

```javascript
// ❌ WRONG - This reads env vars at BUILD TIME
async rewrites() {
  const backendUrl = process.env.BACKEND_INTERNAL_URL; // Read during `npm run build`
  return [{ source: '/api/backend/:path*', destination: `${backendUrl}/api/:path*` }];
}
```

### The Solution: Runtime API Route Handler

Create a catch-all API route that reads env vars at **request time**:

```typescript
// app/api/backend/[...path]/route.ts

import { NextRequest, NextResponse } from 'next/server';

// Read env var at RUNTIME (every request), not build time
function getBackendUrl(): string {
  return process.env.BACKEND_INTERNAL_URL || 'http://localhost:8000';
}

type Props = {
  params: Promise<{ path: string[] }>;
};

async function proxyRequest(
  request: NextRequest,
  params: { path: string[] }
): Promise<NextResponse> {
  const backendUrl = getBackendUrl();
  const path = params.path.join('/');
  const url = new URL(request.url);

  // Handle different path patterns
  // uploads/* → /uploads/* (static files)
  // tasks/* → /api/tasks/* (API endpoints)
  const backendPath = path.startsWith('uploads/')
    ? `/${path}`
    : `/api/${path}`;

  const targetUrl = `${backendUrl}${backendPath}${url.search}`;

  try {
    // Forward the request with all headers
    const headers = new Headers();
    request.headers.forEach((value, key) => {
      // Skip host header (use backend's host)
      if (key.toLowerCase() !== 'host') {
        headers.set(key, value);
      }
    });

    const response = await fetch(targetUrl, {
      method: request.method,
      headers,
      body: request.body,
      // @ts-expect-error - duplex is required for streaming request bodies
      duplex: 'half',
    });

    // Create response with original headers
    const responseHeaders = new Headers();
    response.headers.forEach((value, key) => {
      // Skip transfer-encoding (Next.js handles this)
      if (key.toLowerCase() !== 'transfer-encoding') {
        responseHeaders.set(key, value);
      }
    });

    return new NextResponse(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: responseHeaders,
    });
  } catch (error) {
    console.error(`Proxy error for ${targetUrl}:`, error);
    return NextResponse.json(
      { error: 'Backend service unavailable' },
      { status: 502 }
    );
  }
}

export async function GET(request: NextRequest, { params }: Props) {
  return proxyRequest(request, await params);
}

export async function POST(request: NextRequest, { params }: Props) {
  return proxyRequest(request, await params);
}

export async function PUT(request: NextRequest, { params }: Props) {
  return proxyRequest(request, await params);
}

export async function PATCH(request: NextRequest, { params }: Props) {
  return proxyRequest(request, await params);
}

export async function DELETE(request: NextRequest, { params }: Props) {
  return proxyRequest(request, await params);
}
```

### Usage

Frontend code calls the proxy path:
```typescript
// Instead of: fetch('http://backend:8000/api/tasks')
// Use:
fetch('/api/backend/tasks')  // Proxied through Next.js server
```

### Kubernetes Configuration

Set `BACKEND_INTERNAL_URL` in your ConfigMap:
```yaml
# helm/myapp/templates/configmap.yaml
data:
  BACKEND_INTERNAL_URL: "http://myapp-backend:8000"  # K8s internal DNS
```

### Why This Works

1. Browser sends request to `/api/backend/tasks` (relative URL)
2. Next.js server receives request
3. Route handler reads `BACKEND_INTERNAL_URL` from ConfigMap (runtime)
4. Proxies to `http://myapp-backend:8000/api/tasks` (K8s internal DNS)
5. Browser cannot use K8s DNS directly, but Next.js server can

### Key Points

- **Build time vs Runtime**: `rewrites()` = build time, API routes = runtime
- **K8s DNS**: Only server-side code can resolve K8s service names
- **Browser limitation**: Browsers cannot use K8s internal DNS
- **ConfigMap injection**: Env vars from ConfigMaps are available at pod startup
