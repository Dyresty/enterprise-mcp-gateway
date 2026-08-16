from mcp.server.fastmcp import FastMCP

from app.gateway.tool_registry import ToolRegistry
from app.tools.calculator import add, multiply

from app.tools.github import get_repository

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




if __name__ == "__main__":
    mcp.run()