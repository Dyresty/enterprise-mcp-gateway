from app.gateway.tool_registry import ToolRegistry


def register_tools():
    registry = ToolRegistry()

    registry.register_tool(
        name="add",
        description="Add two integers and return the result.",
        server_name="Enterprise MCP Gateway",
        input_schema={
            "type": "object",
            "properties": {
                "a": {"type": "integer"},
                "b": {"type": "integer"},
            },
            "required": ["a", "b"],
        },
        output_schema={
            "type": "integer",
        },
        required_role="analyst",
        risk_level="READ",
        timeout_seconds=5,
        rate_limit_per_minute=60,
    )

    registry.register_tool(
        name="multiply",
        description="Multiply two integers and return the result.",
        server_name="Enterprise MCP Gateway",
        input_schema={
            "type": "object",
            "properties": {
                "a": {"type": "integer"},
                "b": {"type": "integer"},
            },
            "required": ["a", "b"],
        },
        output_schema={
            "type": "integer",
        },
        required_role="analyst",
        risk_level="READ",
        timeout_seconds=5,
        rate_limit_per_minute=60,
    )

    registry.register_tool(
        name="github.get_repository",
        description="Retrieve metadata and information about a GitHub repository.",
        server_name="Enterprise MCP Gateway",
        input_schema={
            "type": "object",
            "properties": {
                "owner": {
                    "type": "string"
                },
                "repo": {
                    "type": "string"
                }
            },
            "required": ["owner", "repo"],
        },
        output_schema={
            "type": "object"
        },
        required_role="analyst",
        risk_level="READ",
        timeout_seconds=10,
        rate_limit_per_minute=30,
    )

    registry.register_tool(
        name="github.search_issues",
        description="Search GitHub issues in a repository using a text query and issue state.",
        server_name="Enterprise MCP Gateway",
        input_schema={
            "type": "object",
            "properties": {
                "owner": {
                    "type": "string"
                },
                "repo": {
                    "type": "string"
                },
                "query": {
                    "type": "string"
                },
                "state": {
                    "type": "string",
                    "enum": ["open", "closed"]
                },
                "page": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10,
                    "default": 1,
                },
                "per_page": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 20,
                }
            },
            "required": ["owner", "repo", "query"],
        },
        output_schema={
            "type": "object"
        },
        required_role="analyst",
        risk_level="READ",
        timeout_seconds=10,
        rate_limit_per_minute=30,
    )

    registry.register_tool(
        name="github.get_issue",
        description="Retrieve a specific GitHub issue by issue number.",
        server_name="Enterprise MCP Gateway",
        input_schema={
            "type": "object",
            "properties": {
                "owner": {
                    "type": "string"
                },
                "repo": {
                    "type": "string"
                },
                "issue_number": {
                    "type": "integer",
                    "minimum": 1
                }
            },
            "required": ["owner", "repo", "issue_number"],
        },
        output_schema={
            "type": "object",
        },
        required_role="analyst",
        risk_level="READ",
        timeout_seconds=10,
        rate_limit_per_minute=30,
    )


    print("Tools registered successfully.")


if __name__ == "__main__":
    register_tools()