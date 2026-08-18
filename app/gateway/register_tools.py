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
        cache_enabled=True,
        cache_ttl_seconds=60,
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
                    "enum": ["open", "closed", "all"],
                    "default": "open",
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
        cache_enabled=True,
        cache_ttl_seconds=30,
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
        cache_enabled=True,
        cache_ttl_seconds=60,
    )

    registry.register_tool(
        name="github.list_repositories",
        description="List repositories accessible to the authenticated GitHub account.",
        server_name="Enterprise MCP Gateway",
        input_schema={
            "type": "object",
            "properties": {
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
                    "default": 30,
                },
            },
        },
        output_schema={
            "type": "object",
        },
        required_role="analyst",
        risk_level="READ",
        timeout_seconds=10,
        rate_limit_per_minute=30,
        cache_enabled=True,
        cache_ttl_seconds=60,
    )

    registry.register_tool(
        name="github.create_issue",
        description="Create a new GitHub issue in a repository.",
        server_name="Enterprise MCP Gateway",
        input_schema={
            "type": "object",
            "properties": {
                "owner": {
                    "type": "string",
                    "minLength": 1,
                },
                "repo": {
                    "type": "string",
                    "minLength": 1,
                },
                "title": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 256,
                },
                "body": {
                    "type": ["string", "null"],
                    "maxLength": 10000,
                },
            },
            "required": ["owner", "repo", "title"],
        },
        output_schema={
            "type": "object",
        },
        required_role="developer",
        risk_level="WRITE",
        timeout_seconds=10,
        rate_limit_per_minute=10,
    )

    registry.register_tool(
        name="github.update_issue",
        description="Update an existing GitHub issue.",
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
                },
                "title": {
                    "type": "string",
                    "minLength": 1
                },
                "body": {
                    "type": "string"
                },
                "state": {
                    "type": "string",
                    "enum": ["open", "closed"]
                }
            },
            "required": [
                "owner",
                "repo",
                "issue_number"
            ],
        },
        output_schema={
            "type": "object"
        },
        required_role="developer",
        risk_level="WRITE",
        timeout_seconds=10,
        rate_limit_per_minute=10,
    )

    registry.register_tool(
        name="github.add_issue_comment",
        description="Add a comment to an existing GitHub issue.",
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
                },
                "body": {
                    "type": "string",
                    "minLength": 1
                }
            },
            "required": ["owner", "repo", "issue_number", "body"],
        },
        output_schema={
            "type": "object"
        },
        required_role="developer",
        risk_level="WRITE",
        timeout_seconds=10,
        rate_limit_per_minute=10,
    )

    registry.register_tool(
        name="github.delete_issue_comment",
        description="Delete a comment from a GitHub issue.",
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
                },
                "comment_id": {
                    "type": "integer",
                    "minimum": 1
                }
            },
            "required": [
                "owner",
                "repo",
                "issue_number",
                "comment_id"
            ],
        },
        output_schema={
            "type": "object"
        },
        required_role="developer",
        risk_level="WRITE",
        timeout_seconds=10,
        rate_limit_per_minute=10,
    )

    print("Tools registered successfully.")


if __name__ == "__main__":
    register_tools()