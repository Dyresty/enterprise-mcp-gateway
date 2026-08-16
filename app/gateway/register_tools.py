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

    print("Tools registered successfully.")


if __name__ == "__main__":
    register_tools()