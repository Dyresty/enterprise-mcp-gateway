import asyncio

import httpx
import pytest
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from pydantic import ValidationError

from app.a2a import server as a2a_server
from app.agent.graph import build_agent_graph
from app.agent.runner import to_llm_tool_name
from app.mcp import server
from app.tools import research


class ScriptedLLM:
    """Returns pre-defined responses so the graph can be tested without an LLM."""

    def __init__(self, responses):
        self.responses = list(responses)

    def bind_tools(self, tools):
        return self

    async def ainvoke(self, messages):
        return self.responses.pop(0)


@tool
def research__search_projects(query: str) -> str:
    """Search research projects."""
    return f"ENEXA matches '{query}'"


def test_agent_calls_tool_then_answers():
    llm = ScriptedLLM(
        [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "research__search_projects",
                        "args": {"query": "knowledge graphs"},
                        "id": "call-1",
                    }
                ],
            ),
            AIMessage(content="ENEXA is the project."),
        ]
    )

    graph = build_agent_graph(llm, [research__search_projects])
    result = asyncio.run(
        graph.ainvoke({"messages": [HumanMessage("Which project?")]})
    )

    messages = result["messages"]
    tool_messages = [m for m in messages if isinstance(m, ToolMessage)]

    assert tool_messages[0].content == "ENEXA matches 'knowledge graphs'"
    assert messages[-1].content == "ENEXA is the project."


def test_agent_answers_directly_without_tool_calls():
    llm = ScriptedLLM([AIMessage(content="Hello.")])

    graph = build_agent_graph(llm, [research__search_projects])
    result = asyncio.run(graph.ainvoke({"messages": [HumanMessage("Hi")]}))

    assert len(result["messages"]) == 2
    assert result["messages"][-1].content == "Hello."


def test_tool_names_are_valid_for_openai():
    assert to_llm_tool_name("github.get_issue") == "github__get_issue"
    assert to_llm_tool_name("add") == "add"


def test_research_search_validates_input():
    with pytest.raises(ValidationError):
        research.search_projects(query="ai")

    with pytest.raises(ValidationError):
        research.search_projects(query="quantum networks", top_k=50)


def test_research_client_maps_rag_response(monkeypatch):
    def fake_get(url, params, timeout):
        assert url.endswith("/search")
        assert params == {"q": "knowledge graphs", "top_k": 3}
        return httpx.Response(
            200,
            json=[
                {
                    "title": "ENEXA - Efficient Explainable Learning on Knowledge Graphs",
                    "document_id": "101070305",
                    "rerank_score": 0.99912,
                    "text": "Objective ...",
                }
            ],
            request=httpx.Request("GET", url),
        )

    monkeypatch.setattr(httpx, "get", fake_get)

    results = research.search_projects("knowledge graphs", top_k=3)

    assert results == [
        {
            "title": "ENEXA - Efficient Explainable Learning on Knowledge Graphs",
            "grant_id": "101070305",
            "url": "https://cordis.europa.eu/project/id/101070305",
            "relevance": 0.999,
            "excerpt": "Objective ...",
        }
    ]


def test_denied_tool_call_is_audited(monkeypatch, capture_audit_log):
    server.AUTH_CONTEXT = server.create_authentication_context("analyst")

    monkeypatch.setattr(
        server.registry,
        "get_tool",
        lambda name: {
            "name": "github.create_issue",
            "required_role": "developer",
        },
    )

    with pytest.raises(ValueError, match="not authorized"):
        server.execute_tool(
            tool_name="github.create_issue",
            arguments={},
            execute_function=lambda: "should not run",
        )

    assert capture_audit_log[-1]["status"] == "DENIED"
    assert capture_audit_log[-1]["user_role"] == "analyst"
    assert "Required role: 'developer'" in capture_audit_log[-1]["error_message"]


def test_a2a_agent_card_is_published():
    client = TestClient(a2a_server.app)

    card = client.get("/.well-known/agent-card.json").json()

    assert card["name"] == "Enterprise Gateway Agent"
    assert card["supportedInterfaces"][0]["protocolBinding"] == "JSONRPC"
    assert {skill["id"] for skill in card["skills"]} == {
        "research_projects",
        "engineering_lookup",
    }
