from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode


SYSTEM_PROMPT = """You are a research and engineering assistant connected to an enterprise tool gateway.

Use the available tools to answer. Rules:
- Use research__search_projects for any question about EU research projects, grants, partners or topics.
- Base every factual statement on tool results. Name the project and its CORDIS URL when you use one.
- If a tool returns an error (for example missing permissions or a rate limit), explain it to the user. Do not retry the same call more than once.
- If the tools cannot answer the question, say so instead of guessing.
- Keep answers short and structured."""


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


def build_agent_graph(llm, tools):
    """
    ReAct-style tool loop:

        START -> agent --(tool calls?)--> tools -> agent -> ... -> END

    The agent node decides which gateway tool to call; the tools node executes
    the calls through MCP, where authentication, RBAC, rate limiting, caching
    and audit logging are enforced.
    """

    llm_with_tools = llm.bind_tools(tools)

    async def call_model(state: AgentState) -> dict:
        response = await llm_with_tools.ainvoke(
            [SystemMessage(SYSTEM_PROMPT), *state["messages"]]
        )
        return {"messages": [response]}

    def route_after_model(state: AgentState) -> str:
        last_message = state["messages"][-1]
        return "tools" if getattr(last_message, "tool_calls", None) else END

    graph = StateGraph(AgentState)
    graph.add_node("agent", call_model)
    graph.add_node("tools", ToolNode(tools))

    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", route_after_model, ["tools", END])
    graph.add_edge("tools", "agent")

    return graph.compile()
