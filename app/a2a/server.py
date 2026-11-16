"""
A2A (Agent2Agent) server for the gateway agent.

MCP connects the agent to its tools; A2A lets other agents discover this agent
(via its agent card) and delegate tasks to it over JSON-RPC.

    uvicorn app.a2a.server:app --port 9000
    curl http://127.0.0.1:9000/.well-known/agent-card.json
"""

from a2a.helpers.proto_helpers import new_text_message
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import (
    add_a2a_routes_to_fastapi,
    create_agent_card_routes,
    create_jsonrpc_routes,
)
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentInterface,
    AgentSkill,
)
from a2a.utils.constants import PROTOCOL_VERSION_CURRENT, TransportProtocol
from fastapi import FastAPI

from app.agent.runner import run_agent
from app.agent.tracing import flush
from app.config import settings


# Remote agents are not authenticated users of the gateway yet,
# so they get the least-privileged role (read-only tools).
A2A_AGENT_ROLE = "analyst"


def build_agent_card() -> AgentCard:
    return AgentCard(
        name="Enterprise Gateway Agent",
        description=(
            "Answers questions about EU-funded research projects and "
            "engineering resources using tools behind a secured MCP gateway."
        ),
        version="0.2.0",
        supported_interfaces=[
            AgentInterface(
                url=f"{settings.A2A_URL}/",
                protocol_binding=TransportProtocol.JSONRPC.value,
                protocol_version=PROTOCOL_VERSION_CURRENT,
            )
        ],
        capabilities=AgentCapabilities(streaming=False),
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        skills=[
            AgentSkill(
                id="research_projects",
                name="EU research project search",
                description="Finds Horizon Europe projects by topic, partner, acronym or grant ID.",
                tags=["research", "cordis", "funding"],
                examples=["Which projects with Paderborn University work on quantum photonics?"],
            ),
            AgentSkill(
                id="engineering_lookup",
                name="Repository and database lookup",
                description="Reads GitHub repositories and issues and inspects PostgreSQL schemas.",
                tags=["github", "postgres"],
                examples=["List the tables in the gateway database."],
            ),
        ],
    )


class GatewayAgentExecutor(AgentExecutor):

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:

        result = await run_agent(
            context.get_user_input(),
            username=A2A_AGENT_ROLE,
        )
        flush()

        await event_queue.enqueue_event(
            new_text_message(
                result["answer"],
                context_id=context.context_id,
                task_id=context.task_id,
            )
        )

    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        raise NotImplementedError("Cancelling a running agent task is not supported.")


agent_card = build_agent_card()

request_handler = DefaultRequestHandler(
    agent_executor=GatewayAgentExecutor(),
    task_store=InMemoryTaskStore(),
    agent_card=agent_card,
)

app = FastAPI(
    title="Enterprise Gateway Agent (A2A)",
    version="0.2.0",
)

add_a2a_routes_to_fastapi(
    app,
    agent_card_routes=create_agent_card_routes(agent_card),
    jsonrpc_routes=create_jsonrpc_routes(request_handler, rpc_url="/"),
)
