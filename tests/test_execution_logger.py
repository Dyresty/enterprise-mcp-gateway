from datetime import datetime

from app.audit.execution_logger import ToolExecutionLogger
from app.database import get_connection


def test_execution_logger_writes_to_postgresql():
    logger = ToolExecutionLogger()

    started_at = datetime.now()
    completed_at = datetime.now()

    logger.log_execution(
        tool_name="test.tool",
        user_id="test-user-001",
        username="test-user",
        user_role="analyst",
        status="SUCCESS",
        started_at=started_at,
        completed_at=completed_at,
        duration_ms=25,
    )

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    tool_name,
                    user_id,
                    username,
                    user_role,
                    status,
                    duration_ms,
                    error_message
                FROM tool_execution_logs
                WHERE tool_name = %s
                  AND user_id = %s
                ORDER BY id DESC
                LIMIT 1;
                """,
                ("test.tool", "test-user-001"),
            )

            row = cursor.fetchone()

    assert row is not None
    assert row[0] == "test.tool"
    assert row[1] == "test-user-001"
    assert row[2] == "test-user"
    assert row[3] == "analyst"
    assert row[4] == "SUCCESS"
    assert row[5] == 25
    assert row[6] is None