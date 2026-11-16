import httpx
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI

from app.agent.graph import build_agent_graph
from app.agent.tracing import get_callbacks
from app.config import settings


async def login(username: str) -> str:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            f"{settings.GATEWAY_URL}/auth/login",
            json={"username": username},
        )
        response.raise_for_status()
        return response.json()["access_token"]


async def load_gateway_tools(token: str) -> list:
    """
    Discover tools from the gateway over MCP (streamable HTTP).
    The JWT identifies the user, so the gateway applies that user's role
    to every tool call the agent makes.
    """

    client = MultiServerMCPClient(
        {
            "gateway": {
                "transport": "streamable_http",
                "url": f"{settings.GATEWAY_URL}/mcp/",
                "headers": {"Authorization": f"Bearer {token}"},
            }
        }
    )
    tools = await client.get_tools()

    # OpenAI function names only allow [a-zA-Z0-9_-]; the gateway uses
    # namespaced names like "github.get_issue". Only the LLM-facing name
    # changes, the MCP call still uses the original tool name.
    for tool in tools:
        tool.name = to_llm_tool_name(tool.name)

    return tools


def to_llm_tool_name(name: str) -> str:
    return name.replace(".", "__")


def create_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.LLM_MODEL,
        base_url=settings.LLM_BASE_URL,
        temperature=0,
    )


async def run_agent(
    question: str,
    username: str = "analyst",
) -> dict:

    token = await login(username)
    tools = await load_gateway_tools(token)
    graph = build_agent_graph(create_llm(), tools)

    result = await graph.ainvoke(
        {"messages": [HumanMessage(question)]},
        config={
            # each step is one agent call plus one tool call
            "recursion_limit": 2 * settings.AGENT_MAX_STEPS + 1,
            "callbacks": get_callbacks(),
            "metadata": {"langfuse_user_id": username},
        },
    )

    messages = result["messages"]

    return {
        "answer": messages[-1].content,
        "tool_calls": [
            {"tool": call["name"], "args": call["args"]}
            for message in messages
            if isinstance(message, AIMessage)
            for call in message.tool_calls
        ],
        "tool_errors": [
            message.content
            for message in messages
            if isinstance(message, ToolMessage) and message.status == "error"
        ],
    }
