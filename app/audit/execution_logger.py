from datetime import datetime
from typing import Any

from app.database import get_connection


class ToolExecutionLogger:

    def log_execution(
        self,
        tool_name: str,
        user_id: str,
        username: str,
        user_role: str,
        status: str,
        started_at: datetime,
        completed_at: datetime,
        duration_ms: int,
        error_message: str | None = None,
    ) -> None:

        query = """
        INSERT INTO tool_execution_logs (
            tool_name,
            user_id,
            username,
            user_role,
            status,
            started_at,
            completed_at,
            duration_ms,
            error_message
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s
        );
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        tool_name,
                        user_id,
                        username,
                        user_role,
                        status,
                        started_at,
                        completed_at,
                        duration_ms,
                        error_message,
                    ),
                )

            connection.commit()