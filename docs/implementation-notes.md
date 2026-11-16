# Enterprise MCP Gateway

A secure, extensible MCP gateway for enabling AI agents to discover and execute enterprise tools through a centralized policy and execution layer.

The gateway separates **enterprise integrations** from cross-cutting concerns such as authentication, authorization, rate limiting, caching, retries, timeouts, and audit logging.

---

# Current Project Status

The gateway currently provides a working enterprise tool execution architecture with:

- MCP server using FastMCP
- JWT authentication
- MCP SDK token verification
- Role-Based Access Control (RBAC)
- PostgreSQL-backed tool registry
- Redis-backed caching
- Redis-backed rate limiting
- Configurable retries
- Configurable execution timeouts
- PostgreSQL audit logging
- GitHub enterprise tooling
- PostgreSQL schema inspection tooling
- Centralized tool execution pipeline
- Development authentication fallback
- Comprehensive automated test coverage

The current implementation has **69 automated tests passing**.

```text
69 passed
0 failed
```

Run the test suite with:

```bash
python -m pytest -v
```

---

# Architecture

The gateway follows a centralized execution architecture.

```text
                    ┌──────────────────────┐
                    │       AI Agent       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    MCP Gateway       │
                    │      FastMCP         │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
        Authentication       RBAC          Rate Limiting
             JWT               │                │
              │                │                │
              └────────────────┼────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Tool Execution      │
                    │      Pipeline        │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
            Cache            Retry           Timeout
              │                │                │
              └────────────────┼────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Enterprise Tools     │
                    ├──────────────────────┤
                    │ GitHub               │
                    │ PostgreSQL           │
                    │ Calculator           │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Audit Logging      │
                    │     PostgreSQL       │
                    └──────────────────────┘
```

The key architectural principle is that enterprise integrations should not independently implement authentication, RBAC, rate limiting, retries, timeouts, caching, or audit logging.
These concerns are handled centrally by the gateway.

## Tool Execution Pipeline

Every enterprise tool is routed through the common execution pipeline.

```text
Tool Request
     │
     ▼
Tool Registry Lookup
     │
     ▼
Authentication
     │
     ▼
RBAC Authorization
     │
     ▼
Rate Limiting
     │
     ▼
Cache Lookup
     │
     ├──────── Cache Hit ────────► Return Result
     │
     ▼
Retry Execution
     │
     ▼
Timeout Enforcement
     │
     ▼
Enterprise Tool
     │
     ▼
Cache Write
     │
     ▼
Audit Logging
     │
     ▼
Return Result
```

The pipeline is implemented centrally in:

`app/mcp/server.py`

This prevents individual tools from bypassing gateway-level security and reliability policies.

---

# Implemented Features

### 1. MCP Gateway
The gateway is built using the MCP Python SDK and FastMCP.
Current capabilities include:

- FastMCP server
- MCP tool registration
- Centralized tool execution
- Tool registry integration
- Authentication integration
- Authorization enforcement
- Rate limiting
- Redis caching
- Retry handling
- Timeout enforcement
- Audit logging

The main MCP server is:

`app/mcp/server.py`

### 2. Tool Registry
Tools are registered in PostgreSQL and contain metadata controlling how the gateway executes them.
The registry stores information such as:

- `name`
- `description`
- `server_name`
- `input_schema`
- `output_schema`
- `required_role`
- `risk_level`
- `timeout_seconds`
- `rate_limit_per_minute`
- `cache_enabled`
- `cache_ttl_seconds`
- `max_retries`
- `retry_backoff_seconds`
- `enabled`

The registry allows execution policies to be configured without embedding those policies directly into individual tool implementations.

Main implementation:
- `app/gateway/tool_registry.py`

Tool registration:
- `app/gateway/register_tools.py`

### 3. Authentication
The gateway currently supports JWT-based authentication.
Implemented:

- JWT access token creation
- JWT signature verification
- JWT expiration validation
- Required claim validation
- Invalid-token rejection
- Authentication context creation
- MCP SDK AccessToken integration
- MCP JWT token verification

The authentication layer produces an authenticated identity containing:

- `user_id`
- `username`
- `role`

Key files:
- Authentication models: `app/auth/models.py`
- Authentication logic: `app/auth/authentication.py`
- JWT implementation: `app/auth/jwt.py`

#### MCP JWT Integration
The gateway includes an adapter between the gateway JWT implementation and the MCP SDK authentication system.

```text
Client
  │
  │ Bearer JWT
  ▼
MCP Authentication
  │
  ▼
MCPJWTTokenVerifier
  │
  ▼
Gateway JWT Decoder
  │
  ▼
Authenticated User
  │
  ├── user_id
  ├── username
  └── role
```

Implementation:
- `app/auth/mcp_token_verifier.py`

The MCP token verifier converts the gateway JWT into an MCP SDK `AccessToken` containing:

- `token`
- `client_id`
- `scopes`
- `subject`
- `claims`

The role and username are preserved in the token claims so that the gateway execution layer can use the authenticated MCP identity.

### 4. Role-Based Access Control
RBAC is enforced centrally before a tool is executed.
Current development roles:

- `analyst`
- `developer`
- `admin`

The authorization model is based on the tool's registered `required_role`:

```text
analyst
   │
   └── analyst-level tools

developer
   │
   ├── analyst-level tools
   └── developer-level tools

admin
   │
   └── all supported tools
```

Authorization occurs inside the gateway execution path.

Implementation:
- `app/auth/rbac.py`

The gateway does not rely on individual tools to enforce their own permissions.

### 5. Rate Limiting
The gateway implements Redis-backed rate limiting.
Rate limits are configured per tool through the tool registry.

Example:
```python
rate_limit_per_minute = 30
```

The rate limiter provides:
- Per-user limits
- Per-tool limits
- Independent limits between users
- Independent limits between tools
- Redis-backed expiration
- Rate-limit rejection

Implementation:
- `app/rate_limit/limiter.py`

The identity used for rate limiting comes from the authenticated MCP user.

### 6. Redis Caching
Read-oriented tools can use Redis caching through the centralized execution pipeline.
Implemented:

- Deterministic cache keys
- Argument-aware cache keys
- Redis storage
- Configurable TTL
- Cache lookup
- Cache write
- Cache hit handling

Cache keys use:
```text
mcp:tool:<tool_name>:<argument_hash>
```

The argument hash is generated using SHA-256 over a deterministic JSON representation of the tool arguments.

Example:
```text
mcp:tool:github.get_repository:<sha256>
```

Implementation:
- `app/cache/redis_cache.py`

#### Write Tool Cache Protection
Write operations are not cached.
For example:
- `github.create_issue`
- `github.update_issue`
- `github.add_issue_comment`
- `github.delete_issue_comment`

do not use the cache. This prevents stale or incorrect results from being returned for state-changing operations. Caching is therefore treated as a read-oriented optimization, not a generic execution feature.

### 7. Retry Handling
The gateway provides configurable retry behavior.
Tools can define:

- `max_retries`
- `retry_backoff_seconds`

Example:
```python
max_retries = 2
retry_backoff_seconds = 0.5
```

The retry layer handles:
- Immediate success
- Temporary failures
- Multiple retry attempts
- Retry exhaustion
- Configurable backoff
- Zero retries

Implementation:
- `app/retry/retry.py`

### 8. Timeout Enforcement
Every tool can define a timeout through the tool registry.

Example:
```python
timeout_seconds = 10
```

The gateway executes the tool through a controlled executor and rejects executions that exceed the configured timeout.

Implementation is part of the centralized execution pipeline in:
- `app/mcp/server.py`

### 9. Audit Logging
Tool executions are logged centrally.
Each execution can record:

- `tool_name`
- `user_id`
- `username`
- `user_role`
- `status`
- `started_at`
- `completed_at`
- `duration_ms`
- `error_message`

The audit logger persists execution records to PostgreSQL.

Implementation:
- `app/audit/execution_logger.py`

Both successful and failed executions are recorded, providing an enterprise audit trail for tool usage.

---

# Enterprise Integrations

### 10. GitHub Integration
GitHub is the first major enterprise integration implemented in the gateway.
The GitHub API logic is isolated in:
- `app/integrations/github/client.py`

The MCP-facing tools are exposed through:
- `app/mcp/server.py`

#### GitHub Read Tools
Currently implemented:
- `github.get_repository`
- `github.get_issue`
- `github.search_issues`
- `github.list_repositories`

These provide read-oriented GitHub functionality to the MCP client.

#### GitHub Write Tools
Currently implemented:
- `github.create_issue`
- `github.update_issue`
- `github.add_issue_comment`
- `github.delete_issue_comment`

These operations are protected by the gateway's RBAC layer. Write tools require the appropriate developer-level authorization according to their registered tool metadata.

The architecture separates:

```text
Read Operations
      │
      └── lower-risk access

Write Operations
      │
      └── elevated RBAC requirements
```

The GitHub client itself is responsible for communicating with the GitHub API.
The gateway remains responsible for:
- Authentication
- Authorization
- Rate Limiting
- Retries
- Timeouts
- Caching Policy
- Audit Logging

### 11. PostgreSQL Integration
The first PostgreSQL enterprise tooling layer has been implemented, focusing on schema discovery and inspection.

Implementation:
- `app/integrations/postgres/client.py`

MCP tool exposure:
- `app/mcp/server.py`

#### PostgreSQL Schema Discovery

`postgres.list_tables`  
Lists the user tables available in the PostgreSQL database.  
Usage:
```python
postgres.list_tables()
```
*No arguments are required.*

`postgres.describe_table`  
Inspects the schema and column metadata of a specific table.  
Arguments:
- `schema`
- `table`

Example:
```python
postgres.describe_table(
    schema="public",
    table="customers"
)
```

This provides the foundation for future database-aware agent workflows:

```text
postgres.list_tables
        │
        ▼
Discover available tables
        │
        ▼
postgres.describe_table
        │
        ▼
Understand database schema
        │
        ▼
Future database query tools
```

> Arbitrary SQL execution has not yet been implemented. A future SQL execution layer should be introduced only after appropriate controls for authorization, query safety, database scope, resource limits, and auditing are designed.

### 12. Calculator Tools
The gateway also contains basic calculator tools used as simple MCP examples and execution-pipeline tests.

Current tools:
- `add`
- `multiply`

Implementation:
- `app/tools/calculator.py`

These tools demonstrate how a tool is routed through the same centralized gateway execution architecture.

---

# Project Structure

```text
enterprise-mcp-gateway/
│
├── app/
│   │
│   ├── auth/
│   │   ├── authentication.py
│   │   ├── jwt.py
│   │   ├── models.py
│   │   ├── rbac.py
│   │   └── mcp_token_verifier.py
│   │
│   ├── audit/
│   │   └── execution_logger.py
│   │
│   ├── cache/
│   │   └── redis_cache.py
│   │
│   ├── gateway/
│   │   ├── tool_registry.py
│   │   └── register_tools.py
│   │
│   ├── integrations/
│   │   ├── github/
│   │   │   └── client.py
│   │   │
│   │   └── postgres/
│   │       └── client.py
│   │
│   ├── mcp/
│   │   └── server.py
│   │
│   ├── rate_limit/
│   │   └── limiter.py
│   │
│   ├── retry/
│   │   └── retry.py
│   │
│   └── tools/
│       ├── calculator.py
│       └── github.py
│
├── tests/
│   ├── test_auth_routes.py
│   ├── test_authentication.py
│   ├── test_execution_logger.py
│   ├── test_execution_pipeline.py
│   ├── test_jwt.py
│   ├── test_mcp_authorization.py
│   ├── test_mcp_cache.py
│   ├── test_mcp_cache_integration.py
│   ├── test_mcp_jwt_authentication.py
│   ├── test_mcp_rate_limit.py
│   ├── test_mcp_token_verifier.py
│   ├── test_rbac.py
│   ├── test_redis_cache.py
│   ├── test_retry.py
│   ├── test_timeout.py
│   ├── test_tool_registry_cache.py
│   └── test_write_tools_not_cached.py
│
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

# Testing

The project currently contains tests covering the major gateway layers.

### Authentication
- User authentication
- Unknown-user rejection
- JWT creation
- JWT decoding
- Invalid JWT rejection
- Wrong-secret rejection
- Expired-token rejection
- Missing-claim rejection
- MCP JWT token verification
- MCP authentication context creation

### Authorization
- Analyst permissions
- Developer permissions
- Admin permissions
- Analyst rejection of developer tools
- Unknown roles
- Invalid required roles
- Unknown tools

### Rate Limiting
- First request
- Requests within limits
- Rate-limit rejection
- Per-user limits
- Per-tool limits
- Redis expiration
- Invalid rate-limit configuration

### Caching
- Redis set/get
- Missing cache keys
- Cache existence
- Deterministic cache keys
- Argument-dependent cache keys
- Cache integration
- Write-tool cache prevention

### Reliability
- Successful execution
- Retry after failure
- Retry exhaustion
- Zero retries
- Invalid retry configuration
- Successful timeout execution
- Timeout failure

### Audit Logging
- Execution persistence to PostgreSQL

### Current Test Result

```text
69 passed
0 failed
```

Run:

```bash
python -m pytest -v
```

---

# Development Principles

The project is intentionally being developed as an enterprise gateway, rather than as a collection of unrelated MCP tools. The following architectural principles should be maintained as the project grows:

1. **Centralize Cross-Cutting Concerns**: Authentication, authorization, rate limiting, caching, retries, timeouts, and audit logging belong in the gateway execution layer. New integrations should not duplicate these mechanisms.
2. **Keep Integrations Modular**: Enterprise API/database logic belongs in `app/integrations/`. The MCP server should expose tools and route them through the gateway pipeline rather than containing large amounts of integration-specific implementation logic.
3. **Use the Tool Registry as the Policy Layer**: Tool metadata should define execution policy where appropriate (`required_role`, `risk_level`, `timeout_seconds`, `rate_limit_per_minute`, `cache_enabled`, `cache_ttl_seconds`, `max_retries`, `retry_backoff_seconds`, `enabled`).
4. **Treat Read and Write Operations Differently**: Read operations may be cached when appropriate. Write operations should not be cached and should normally require stronger authorization. This distinction is especially important for integrations such as GitHub, PostgreSQL, Filesystem, and Slack.
5. **Preserve the Existing Execution Pipeline**: New tools should enter through:

```text
Tool Registry ─► Authentication ─► RBAC ─► Rate Limiting ─► Cache ─► Retry ─► Timeout ─► Tool Execution ─► Audit Logging
```

The gateway should not develop separate execution paths for individual integrations unless there is a strong architectural reason.

---

# Roadmap

The project will continue toward a complete enterprise agent platform.

### PostgreSQL
- Additional database inspection tools
- Controlled SQL querying
- Query safety and validation
- Database access policies
- Query resource limits
- Query auditing

### Enterprise Knowledge / Files
- Filesystem tools
- Internal knowledge sources
- Document discovery
- Controlled file access

### Gateway Infrastructure
- Centralized tool dispatcher
- More advanced tool discovery
- Improved policy enforcement
- Production authentication backend
- Security hardening

### Agent Layer
- LangGraph-based agent
- Tool discovery
- Multi-step reasoning workflows
- Multi-tool execution
- Stateful agent workflows

Example future workflow:

```text
User
 │
 ▼
Agent
 │
 ▼
Discover Available Tools
 │
 ▼
Select Tools
 │
 ├───────────────┐
 ▼               ▼
PostgreSQL      GitHub
 │               │
 ▼               ▼
Retrieve        Modify
Data            Resource
 │               │
 └───────┬───────┘
         ▼
     Agent Result
```

### Observability
- Langfuse integration
- Tracing
- Tool-level latency metrics
- Agent execution traces
- Error analysis
- Token/LLM observability

### Production Readiness
- Security hardening
- Expanded integration tests
- End-to-end tests
- Dockerization
- Production configuration
- Evaluation framework
- Agent/tool performance evaluation

---

# Current Position in the Project

The project has moved beyond a basic MCP server and is now a functioning enterprise tool gateway.

```text
                    Enterprise MCP Gateway
                             │
             ┌───────────────┼───────────────┐
             │               │               │
             ▼               ▼               ▼
       Authentication       RBAC        Tool Registry
             │               │               │
             └───────────────┼───────────────┘
                             ▼
                    Execution Pipeline
                             │
       ┌─────────────┬───────┼────────┬─────────────┐
       │             │       │        │             │
       ▼             ▼       ▼        ▼             ▼
     Redis         Retry   Timeout  GitHub      PostgreSQL
     Cache
       │
       └──────────────────────┬───────────────────────┘
                              ▼
                       Audit Logging
                              │
                              ▼
                         PostgreSQL
```

The core gateway architecture is established. Future work should focus on expanding enterprise capabilities and building the agent layer on top of this foundation, rather than replacing the existing architecture.
