from flask import app

from mcp.server.fastmcp import FastMCP

from app.gateway.tool_registry import ToolRegistry
from app.tools.calculator import add, multiply

from app.tools.github import (
    get_repository,
    get_issue,
    search_issues,
)

mcp = FastMCP("Enterprise MCP Gateway")

registry = ToolRegistry()


@mcp.tool(name="add")
def add_tool(a: int, b: int) -> int:
    """
    Add two integers and return the result.
    """
    tool = registry.get_tool("add")

    if tool is None:
        raise ValueError("Tool 'add' is not registered or is disabled.")

    return add(a, b)

@mcp.tool(name="multiply")
def multiply_tool(a: int, b: int) -> int:
    """
    Multiply two integers and return the result.
    """
    tool = registry.get_tool("multiply")

    if tool is None:
        raise ValueError("Tool 'multiply' is not registered or is disabled.")

    return multiply(a, b)



@mcp.tool(name="github.get_repository")
def github_get_repository(owner: str, repo: str) -> dict:
    """
    Retrieve metadata and information about a GitHub repository.
    """
    tool = registry.get_tool("github.get_repository")

    if tool is None:
        raise ValueError(
            "Tool 'github.get_repository' is not registered or is disabled."
        )

    return get_repository(owner, repo)

@mcp.tool(name="github.get_issue")
def github_get_issue(
    owner: str,
    repo: str,
    issue_number: int,
) -> dict:
    """
    Retrieve a specific GitHub issue by issue number.
    """

    tool = registry.get_tool("github.get_issue")

    if tool is None:
        raise ValueError(
            "Tool 'github.get_issue' is not registered or is disabled."
        )

    return get_issue(
        owner=owner,
        repo=repo,
        issue_number=issue_number,
    )

@mcp.tool(name="github.search_issues")
def github_search_issues(
    owner: str,
    repo: str,
    query: str,
    state: str = "open",
    page: int = 1,
    per_page: int = 20,
) -> dict:
    """
    Search GitHub issues in a repository.
    """

    tool = registry.get_tool("github.search_issues")

    if tool is None:
        raise ValueError(
            "Tool 'github.search_issues' is not registered or is disabled."
        )

    return search_issues(
        owner=owner,
        repo=repo,
        query=query,
        state=state,
        page=page,
        per_page=per_page,
    )

if __name__ == "__main__":
    mcp.run()