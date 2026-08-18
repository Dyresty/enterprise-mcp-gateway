from unittest.mock import patch

from app.gateway.tool_registry import ToolRegistry


def test_register_tool_accepts_cache_configuration():
    registry = ToolRegistry()

    with patch("app.gateway.tool_registry.get_connection") as mock_connection:
        mock_cursor = mock_connection.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value

        registry.register_tool(
            name="test.cached_tool",
            description="Test cached tool.",
            server_name="Test Server",
            required_role="analyst",
            cache_enabled=True,
            cache_ttl_seconds=120,
        )

        executed_query = mock_cursor.execute.call_args

        assert executed_query is not None
        assert "cache_enabled" in executed_query.args[0]
        assert "cache_ttl_seconds" in executed_query.args[0]

        values = executed_query.args[1]

        assert True in values
        assert 120 in values