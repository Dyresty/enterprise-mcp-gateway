from app.database import get_connection


CREATE_TOOL_EXECUTION_LOGS_TABLE = """
CREATE TABLE IF NOT EXISTS tool_execution_logs (
    id SERIAL PRIMARY KEY,
    tool_name VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL,
    user_role VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    duration_ms INTEGER,
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def create_execution_logs_table():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_TOOL_EXECUTION_LOGS_TABLE)

        connection.commit()

    print("Tool execution logs table created successfully.")


if __name__ == "__main__":
    create_execution_logs_table()