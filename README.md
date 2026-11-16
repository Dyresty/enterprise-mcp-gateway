# Enterprise MCP Tool Gateway & Agent Platform

A secured **Model Context Protocol (MCP)** gateway that gives AI agents controlled access to enterprise tools (GitHub, PostgreSQL and a research-project search engine), plus a **LangGraph** agent that uses it and an **A2A** endpoint so other agents can delegate tasks to that agent.

```
 other agents ──A2A (JSON-RPC)──► Gateway Agent (LangGraph) ──MCP (streamable HTTP + JWT)──► MCP Gateway ──► GitHub API
                                        │                                                       │    ├──► PostgreSQL
                                        └── Langfuse traces                                     │    └──► Hybrid RAG service
                                                                                                │         (EU research projects)
                                              JWT auth · RBAC · rate limit · cache · retry · timeout · audit log
                                                        (PostgreSQL registry + audit, Redis cache/limits)
```

**MCP vs A2A:** MCP connects an agent to its *tools*. A2A connects agents to *other agents*. They complement each other: the gateway is the MCP layer, and the agent is published over A2A.

## Tool execution pipeline

Every tool call goes through one pipeline in `app/mcp/server.py`:

1. **Lookup.** The tool must exist and be enabled in the PostgreSQL `tool_registry`.
2. **Authentication.** A JWT bearer token is verified by the MCP token verifier.
3. **RBAC.** The user's role (`analyst < developer < admin`) is checked against the tool's `required_role`. Write tools require `developer`.
4. **Rate limit.** Requests per user, per tool, per minute are counted in Redis.
5. **Cache.** Results of read-only tools are stored in Redis under a SHA-256 hash of the arguments. Write tools are never cached.
6. **Retry and timeout.** Each tool has its own retry count, backoff and timeout.
7. **Audit log.** Every call is written to `tool_execution_logs`: user, role, status (`SUCCESS` / `FAILED` / `DENIED`), duration and error.

Policies live in the registry, not in code, so a tool can be disabled or rate-limited without a deploy.

| Tool | Role | Risk | Notes |
|---|---|---|---|
| `research.search_projects` | analyst | READ | Hybrid search over 1,479 Horizon Europe projects, cached 5 min |
| `github.get_repository`, `github.get_issue`, `github.search_issues`, `github.list_repositories` | analyst | READ | |
| `github.create_issue`, `github.update_issue`, `github.add_issue_comment`, `github.delete_issue_comment` | developer | WRITE | |
| `postgres.list_tables`, `postgres.describe_table` | analyst | READ | Schema inspection only |

## Agent (LangGraph)

`app/agent/graph.py` builds an explicit ReAct loop:

```
START ─► agent ──tool calls?──► tools ─► agent ─► ... ─► END
```

- **Tool discovery.** Tools are discovered at runtime from the gateway over MCP (`langchain-mcp-adapters`), so new gateway tools need no agent changes.
- **JWT identity.** The agent logs in and sends a JWT, so it acts *as a user*: the gateway applies that user's role to every call. An `analyst` agent asked to create an issue gets a permission error from the gateway, and explains it instead of retrying.
- **Tool names.** Gateway names such as `github.get_issue` are mapped to OpenAI-compatible names (`github__get_issue`). Only the name the LLM sees changes.
- **Step limit.** `AGENT_MAX_STEPS` bounds the loop through LangGraph's `recursion_limit`.
- **Tracing.** Langfuse traces every LLM call and tool call when `LANGFUSE_*` keys are set.
- **LLM endpoint.** Any OpenAI-compatible endpoint works (`LLM_BASE_URL`), including vLLM and Ollama.

Example:

```
$ python -m app.agent.cli "Which EU projects with Paderborn University work on explainable ML on knowledge graphs, and how much funding did they get?"
[tool] research__search_projects {'query': 'explainable machine learning knowledge graphs Paderborn University'}

ENEXA - Efficient Explainable Learning on Knowledge Graphs
  Grant ID: 101070305 | EU contribution: €3,991,269.5 | Coordinator: Universität Paderborn (DE)
  https://cordis.europa.eu/project/id/101070305
```

## A2A

`app/a2a/server.py` publishes the agent with the `a2a-sdk`:

- an **agent card** at `/.well-known/agent-card.json`, listing name, skills, examples and the JSON-RPC interface
- a **JSON-RPC endpoint** that runs the agent for each incoming message

Remote agents are not gateway users yet, so they run with the least-privileged role (`analyst`, read-only tools).

```bash
uvicorn app.a2a.server:app --port 9000
python -m app.a2a.client "Which projects work on networks secured by quantum key distribution?"
```

## Setup

```bash
docker compose up -d                       # PostgreSQL + Redis
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                       # GitHub token, OpenAI key, optional Langfuse keys

python -m app.migrations.create_tables
python -m app.migrations.create_execution_logs
python -m app.migrations.add_cache_columns
python -m app.gateway.register_tools

uvicorn app.main:app --port 8000           # MCP gateway at /mcp, login at /auth/login
# research search needs enterprise-hybrid-rag on port 8001:
#   uvicorn app.main:app --port 8001   (in the RAG project)

python -m app.agent.cli "List the tables in the gateway database"
python -m pytest                           # 76 tests
```

Raw JSON-RPC request examples for the MCP endpoint are in `examples/jsonrpc/`.

## Limitations / next steps

- `/auth/login` issues tokens for fixed development users without a password. A real deployment would put an identity provider (OIDC/Keycloak) in front.
- A2A requests are not authenticated yet. The agent card supports security schemes, so OAuth2 between agents is the next step.
- Human approval for WRITE tools (a LangGraph interrupt before the tools node) is not implemented. Today, write access is controlled by role only.

A detailed walkthrough of every gateway feature (registry, auth, RBAC, rate limiting, caching, retries, audit log, integrations) is in [docs/implementation-notes.md](docs/implementation-notes.md).
