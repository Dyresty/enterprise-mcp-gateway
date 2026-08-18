from typing import Any

from psycopg.types.json import Jsonb

from app.database import get_connection


class ToolRegistry:

    def register_tool(
        self,
        name: str,
        description: str,
        server_name: str,
        input_schema: dict[str, Any] | None = None,
        output_schema: dict[str, Any] | None = None,
        required_role: str = "analyst",
        risk_level: str = "READ",
        timeout_seconds: int = 10,
        rate_limit_per_minute: int = 30,
        cache_enabled: bool = False,
        cache_ttl_seconds: int = 60,
    ) -> None:

        query = """
        INSERT INTO tool_registry (
            name,
            description,
            server_name,
            input_schema,
            output_schema,
            required_role,
            risk_level,
            timeout_seconds,
            rate_limit_per_minute,
            cache_enabled,
            cache_ttl_seconds
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (name)
        DO UPDATE SET
            description = EXCLUDED.description,
            server_name = EXCLUDED.server_name,
            input_schema = EXCLUDED.input_schema,
            output_schema = EXCLUDED.output_schema,
            required_role = EXCLUDED.required_role,
            risk_level = EXCLUDED.risk_level,
            timeout_seconds = EXCLUDED.timeout_seconds,
            rate_limit_per_minute = EXCLUDED.rate_limit_per_minute,
            cache_enabled = EXCLUDED.cache_enabled,
            cache_ttl_seconds = EXCLUDED.cache_ttl_seconds,
            updated_at = CURRENT_TIMESTAMP;
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        name,
                        description,
                        server_name,
                        Jsonb(input_schema)
                        if input_schema is not None
                        else None,
                        Jsonb(output_schema)
                        if output_schema is not None
                        else None,
                        required_role,
                        risk_level,
                        timeout_seconds,
                        rate_limit_per_minute,
                        cache_enabled,
                        cache_ttl_seconds,
                    ),
                )

            connection.commit()

    def list_tools(self) -> list[dict[str, Any]]:

        query = """
        SELECT
            name,
            description,
            server_name,
            input_schema,
            output_schema,
            required_role,
            risk_level,
            timeout_seconds,
            rate_limit_per_minute,
            enabled,
            cache_enabled,
            cache_ttl_seconds
        FROM tool_registry
        WHERE enabled = TRUE
        ORDER BY name;
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)

                rows = cursor.fetchall()

        return [
            {
                "name": row[0],
                "description": row[1],
                "server_name": row[2],
                "input_schema": row[3],
                "output_schema": row[4],
                "required_role": row[5],
                "risk_level": row[6],
                "timeout_seconds": row[7],
                "rate_limit_per_minute": row[8],
                "enabled": row[9],
                "cache_enabled": row[10],
                "cache_ttl_seconds": row[11],
            }
            for row in rows
        ]

    def get_tool(self, name: str) -> dict[str, Any] | None:

        query = """
        SELECT
            name,
            description,
            server_name,
            input_schema,
            output_schema,
            required_role,
            risk_level,
            timeout_seconds,
            rate_limit_per_minute,
            enabled,
            cache_enabled,
            cache_ttl_seconds
        FROM tool_registry
        WHERE name = %s
          AND enabled = TRUE;
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (name,))
                row = cursor.fetchone()

        if row is None:
            return None

        return {
            "name": row[0],
            "description": row[1],
            "server_name": row[2],
            "input_schema": row[3],
            "output_schema": row[4],
            "required_role": row[5],
            "risk_level": row[6],
            "timeout_seconds": row[7],
            "rate_limit_per_minute": row[8],
            "enabled": row[9],
            "cache_enabled": row[10],
            "cache_ttl_seconds": row[11],
        }