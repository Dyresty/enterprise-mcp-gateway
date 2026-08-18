from datetime import datetime

from app.database import get_connection


class ExecutionLogger:

    def start_execution(
        self,
        tool_name: str,
        user_id: str,
        username: str,
        user_role: str,
    ) -> tuple[int, datetime]:

        started_at = datetime.now()

        query = """
        INSERT INTO tool_execution_logs (
            tool_name,
            user_id,
            username,
            user_role,
            status,
            started_at
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id;
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
                        "RUNNING",
                        started_at,
                    ),
                )

                execution_id = cursor.fetchone()[0]

            connection.commit()

        return execution_id, started_at

    def complete_execution(
        self,
        execution_id: int,
        started_at: datetime,
    ) -> None:

        completed_at = datetime.now()

        duration_ms = int(
            (completed_at - started_at).total_seconds() * 1000
        )

        query = """
        UPDATE tool_execution_logs
        SET
            status = %s,
            completed_at = %s,
            duration_ms = %s
        WHERE id = %s;
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        "SUCCESS",
                        completed_at,
                        duration_ms,
                        execution_id,
                    ),
                )

            connection.commit()

    def fail_execution(
        self,
        execution_id: int,
        started_at: datetime,
        error_message: str,
    ) -> None:

        completed_at = datetime.now()

        duration_ms = int(
            (completed_at - started_at).total_seconds() * 1000
        )

        query = """
        UPDATE tool_execution_logs
        SET
            status = %s,
            completed_at = %s,
            duration_ms = %s,
            error_message = %s
        WHERE id = %s;
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        "FAILED",
                        completed_at,
                        duration_ms,
                        error_message,
                        execution_id,
                    ),
                )

            connection.commit()


execution_logger = ExecutionLogger()