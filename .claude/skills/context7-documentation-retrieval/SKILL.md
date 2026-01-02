---
name: context7-documentation-retrieval
description: Retrieve up-to-date, version-specific documentation and code examples from libraries using Context7 MCP. Use when generating code, answering API questions, or needing current library documentation. Automatically invoked for code generation tasks involving external libraries.
---

# Context7 Documentation Retrieval

## Instructions

### When to Activate
1. User requests code generation using external libraries
2. User asks about API usage, methods, or library features
3. User mentions specific frameworks (Next.js, FastAPI, Better Auth, SQLModel, etc.)
4. User needs setup instructions or configuration examples
5. User adds "use context7" to their prompt

### How to Approach
1. **Identify the library**: Extract library name from user query
2. **Resolve library ID**: Use `resolve-library-id` tool with library name to find exact ID (format: `/owner/repo`)
3. **Retrieve documentation**: Use `get-library-docs` tool with the resolved ID and relevant topics
4. **Generate response**: Use retrieved docs to provide accurate, current code examples

### Specific Workflows

**Workflow 1: Basic Code Generation**
```
User: "Create Next.js middleware for JWT auth"
→ resolve-library-id("next.js")
→ get-library-docs("/vercel/next.js", topics: ["middleware", "authentication"])
→ Generate code using retrieved docs
```

**Workflow 2: Version-Specific Query**
```
User: "Show React 18 hooks usage"
→ resolve-library-id("react 18")
→ get-library-docs("/facebook/react/v18.0.0", topics: ["hooks"])
→ Provide version-specific examples
```

**Workflow 3: Multiple Libraries**
```
User: "Set up Supabase auth with Next.js"
→ resolve-library-id("supabase")
→ resolve-library-id("next.js")
→ get-library-docs for both libraries
→ Combine documentation for integrated solution
```

### Tool Parameters

**resolve-library-id**
- Input: Library name (string)
- Returns: Array of matching libraries with IDs, descriptions, versions
- Use: Always call first to get exact library ID

**get-library-docs**
- libraryId: Exact ID from resolve-library-id (e.g., "/vercel/next.js")
- topics: Array of relevant keywords (e.g., ["routing", "api"])
- mode: "code" for examples, "info" for guides (default: "code")
- limit: Number of snippets (1-100, default: 10)
- version: Specific version if needed

### Output Format
1. Acknowledge library being used
2. Provide code examples from documentation
3. Include explanations based on retrieved docs
4. Cite source pages when relevant
5. Mention if using specific version

## Phase 2 Technology Stack Examples

### Next.js 16+ App Router Examples

**Example 1: Next.js 16 App Router Setup**
```
User: "Set up Next.js 16 with App Router and TypeScript"

Agent:
1. resolve-library-id("next.js 16")
2. get-library-docs("/vercel/next.js", topics: ["app router", "setup", "typescript"], version: "16")
3. Response: "Here's how to set up Next.js 16 with App Router based on the latest docs:
   [Provide create-next-app command with App Router flag]
   [Show basic app directory structure]
   [Include TypeScript configuration]
   Note: Next.js 16 uses proxy.ts instead of middleware.ts for request interception."
```

**Example 2: Next.js Server Components**
```
User: "How do I create a server component that fetches data in Next.js App Router?"

Agent:
1. resolve-library-id("next.js")
2. get-library-docs("/vercel/next.js", topics: ["server components", "data fetching", "app router"])
3. Response: "In Next.js App Router, server components are the default. Here's how to fetch data:
   [Show async component example with fetch]
   [Explain caching behavior with 'use cache' directive]
   [Include error handling example]
   Based on Next.js 16 documentation."
```

**Example 3: Next.js Dynamic Routes**
```
User: "Create dynamic routes with Next.js 16 App Router use context7"

Agent:
1. resolve-library-id("next.js")
2. get-library-docs("/vercel/next.js", topics: ["dynamic routes", "params", "app router"], version: "16")
3. Response: "Here's how to create dynamic routes in Next.js 16 App Router:
   [Show [slug] folder structure]
   [Demonstrate params prop usage with await]
   [Include generateStaticParams for static generation]
   Example from Next.js 16 routing documentation."
```

**Example 4: Next.js API Routes in App Router**
```
User: "How do I create API endpoints in Next.js 16 App Router?"

Agent:
1. resolve-library-id("next.js")
2. get-library-docs("/vercel/next.js", topics: ["route handlers", "api routes", "app router"])
3. Response: "In Next.js 16 App Router, use Route Handlers in the app directory:
   [Show route.ts file structure]
   [Demonstrate GET, POST, PUT, DELETE handlers]
   [Include request/response handling with NextRequest/NextResponse]
   Documentation source: Next.js App Router API Routes."
```

### FastAPI Backend Examples

**Example 5: FastAPI Basic Setup**
```
User: "Set up a FastAPI project with async endpoints"

Agent:
1. resolve-library-id("fastapi")
2. get-library-docs("/fastapi/fastapi", topics: ["setup", "async", "getting started"])
3. Response: "Here's how to set up FastAPI with async support:
   [Show FastAPI app initialization]
   [Demonstrate async def endpoints]
   [Include uvicorn startup command]
   Based on FastAPI official documentation."
```

**Example 6: FastAPI with Pydantic Models**
```
User: "Create FastAPI request/response models with Pydantic"

Agent:
1. resolve-library-id("fastapi")
2. get-library-docs("/fastapi/fastapi", topics: ["pydantic", "request body", "response model"])
3. Response: "Here's how to use Pydantic models in FastAPI:
   [Show BaseModel class definition]
   [Demonstrate request body validation]
   [Include response_model parameter]
   Example from FastAPI data validation docs."
```

**Example 7: FastAPI JWT Authentication**
```
User: "Implement JWT authentication in FastAPI use context7"

Agent:
1. resolve-library-id("fastapi")
2. get-library-docs("/fastapi/fastapi", topics: ["jwt", "security", "authentication"])
3. Response: "Here's how to implement JWT authentication in FastAPI:
   [Show JWT token creation with python-jose]
   [Demonstrate dependency injection for auth]
   [Include protected endpoint example]
   Source: FastAPI security documentation."
```

### SQLModel + Neon PostgreSQL Examples

**Example 8: SQLModel Setup with PostgreSQL**
```
User: "Set up SQLModel with Neon PostgreSQL database"

Agent:
1. resolve-library-id("sqlmodel")
2. get-library-docs("/fastapi/sqlmodel", topics: ["setup", "postgresql", "engine"])
3. Response: "Here's how to configure SQLModel with Neon PostgreSQL:
   [Show create_engine with psycopg connection string]
   [Demonstrate pool_recycle for serverless databases]
   [Include SSL mode configuration]
   Based on SQLModel database setup documentation."
```

**Example 9: SQLModel Database Models**
```
User: "Create SQLModel models with relationships"

Agent:
1. resolve-library-id("sqlmodel")
2. get-library-docs("/fastapi/sqlmodel", topics: ["models", "relationships", "fields"])
3. Response: "Here's how to define SQLModel models with relationships:
   [Show table=True model definition]
   [Demonstrate Field() for primary keys and foreign keys]
   [Include relationship definitions]
   Example from SQLModel models documentation."
```

**Example 10: SQLModel CRUD Operations**
```
User: "Implement CRUD operations with SQLModel use context7"

Agent:
1. resolve-library-id("sqlmodel")
2. get-library-docs("/fastapi/sqlmodel", topics: ["session", "select", "crud"])
3. Response: "Here's how to implement CRUD operations with SQLModel:
   [Show Session usage with context manager]
   [Demonstrate select() statements]
   [Include insert, update, delete operations]
   Documentation source: SQLModel CRUD operations guide."
```

### Better Auth Integration Examples

**Example 11: Better Auth Setup in Next.js**
```
User: "Set up Better Auth in Next.js 16 project"

Agent:
1. resolve-library-id("better-auth")
2. get-library-docs("/better-auth/better-auth", topics: ["next.js", "setup", "installation"])
3. Response: "Here's how to integrate Better Auth with Next.js 16:
   [Show auth.ts configuration file]
   [Demonstrate toNextJsHandler setup in API route]
   [Include client creation with createAuthClient]
   Based on Better Auth Next.js integration docs."
```

**Example 12: Better Auth JWT Plugin**
```
User: "Enable JWT tokens in Better Auth for FastAPI backend"

Agent:
1. resolve-library-id("better-auth")
2. get-library-docs("/better-auth/better-auth", topics: ["jwt", "plugin", "tokens"])
3. Response: "Here's how to enable JWT plugin in Better Auth:
   [Show jwt() plugin configuration]
   [Demonstrate JWT token generation on login]
   [Include token expiration settings]
   Example from Better Auth JWT plugin documentation."
```

**Example 13: Better Auth Session Management**
```
User: "Implement session management with Better Auth use context7"

Agent:
1. resolve-library-id("better-auth")
2. get-library-docs("/better-auth/better-auth", topics: ["session", "hooks", "client"])
3. Response: "Here's how to manage sessions with Better Auth:
   [Show useSession() hook usage]
   [Demonstrate session refresh patterns]
   [Include logout functionality]
   Source: Better Auth session management guide."
```

### Full-Stack Integration Examples

**Example 14: Next.js + FastAPI Integration**
```
User: "Connect Next.js frontend to FastAPI backend"

Agent:
1. resolve-library-id("next.js")
2. resolve-library-id("fastapi")
3. get-library-docs("/vercel/next.js", topics: ["api client", "fetch"])
4. get-library-docs("/fastapi/fastapi", topics: ["cors", "api"])
5. Response: "Here's how to integrate Next.js with FastAPI:
   [Show CORS configuration in FastAPI]
   [Demonstrate Next.js API client with fetch]
   [Include error handling and TypeScript types]
   Combining Next.js and FastAPI documentation."
```

**Example 15: Better Auth + FastAPI JWT Verification**
```
User: "Verify Better Auth JWT tokens in FastAPI endpoints"

Agent:
1. resolve-library-id("better-auth")
2. get-library-docs("/better-auth/better-auth", topics: ["jwt", "verification"])
3. Response: "Here's how to verify JWT tokens in FastAPI:
   [Show python-jose JWT verification]
   [Demonstrate dependency for protected routes]
   [Include JWKS endpoint fetching for public key]
   Based on Better Auth JWT verification docs."
```

**Example 16: SQLModel + FastAPI with User Filtering**
```
User: "Filter database queries by authenticated user in FastAPI use context7"

Agent:
1. resolve-library-id("sqlmodel")
2. resolve-library-id("fastapi")
3. get-library-docs("/fastapi/sqlmodel", topics: ["select", "where"])
4. get-library-docs("/fastapi/fastapi", topics: ["depends", "security"])
5. Response: "Here's how to filter queries by user in FastAPI with SQLModel:
   [Show dependency to extract user_id from JWT]
   [Demonstrate .where() clause with user_id]
   [Include type-safe query building]
   Combining SQLModel and FastAPI security patterns."
```

**Example 17: Monorepo with Shared Types**
```
User: "Share TypeScript types between Next.js frontend and FastAPI backend"

Agent:
1. resolve-library-id("next.js")
2. get-library-docs("/vercel/next.js", topics: ["typescript", "types"])
3. Response: "Here's how to share types in a monorepo:
   [Show shared types directory structure]
   [Demonstrate type generation from OpenAPI schema]
   [Include type imports in both frontend and backend]
   Documentation from Next.js TypeScript guide."
```

**Example 18: Docker Compose for Full Stack**
```
User: "Create Docker Compose setup for Next.js, FastAPI, and Neon PostgreSQL"

Agent:
1. resolve-library-id("next.js")
2. resolve-library-id("fastapi")
3. get-library-docs("/vercel/next.js", topics: ["docker", "deployment"])
4. get-library-docs("/fastapi/fastapi", topics: ["docker", "deployment"])
5. Response: "Here's a Docker Compose configuration:
   [Show multi-service docker-compose.yml]
   [Demonstrate environment variable management]
   [Include health checks and dependencies]
   Based on Next.js and FastAPI deployment docs."
```

## Best Practices

### Do's
- Always resolve library ID before fetching docs
- Use specific topics to get relevant documentation
- Specify versions when user mentions them (e.g., "Next.js 16", "Python 3.11")
- Cache library IDs for repeated queries in same session
- Combine multiple library docs for integration tasks
- Cite documentation sources in responses
- Prioritize official documentation over third-party sources
- Check for latest API changes when dealing with rapidly evolving libraries

### Don'ts
- Don't guess library IDs - always use resolve-library-id
- Don't use outdated APIs - always fetch fresh docs
- Don't skip documentation retrieval for known libraries
- Don't ignore version specifications from user
- Don't provide generic answers when docs are available
- Don't mix incompatible versions (e.g., Next.js 16 patterns with middleware.ts)

### Phase 2 Specific Best Practices
- For Next.js 16+: Use proxy.ts instead of middleware.ts
- For Better Auth: Always mention JWT plugin for backend integration
- For SQLModel: Include pool_recycle for serverless databases like Neon
- For FastAPI: Demonstrate async/await patterns by default
- For monorepo: Show both frontend and backend code when relevant

### Error Handling
- If library not found: Suggest similar libraries or ask for clarification
- If no docs available: Inform user and offer alternatives
- If rate limited: Inform user to add API key for higher limits
- If ambiguous library name: Present options from resolve-library-id results
- If version mismatch: Warn user about potential compatibility issues

### Constraints
- Rate limit: 60 requests/hour (free), higher with API key
- Max 100 snippets per request
- Documentation reflects latest indexed version unless specified
- Private repos require Pro plan and authentication

### Performance Tips
- Use specific library IDs (e.g., `/vercel/next.js`) to skip resolution
- Filter by topics to reduce irrelevant results
- Request appropriate limit (5-10 for quick answers, more for comprehensive docs)
- Leverage pagination for extensive documentation needs
- Batch related queries when building full-stack examples

---

Want to learn more? Check the [Context7 documentation](https://docs.context7.com)