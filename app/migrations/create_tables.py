from app.database import get_connection


CREATE_TOOL_REGISTRY_TABLE = """
CREATE TABLE IF NOT EXISTS tool_registry (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT NOT NULL,
    server_name VARCHAR(255) NOT NULL,
    input_schema JSONB,
    output_schema JSONB,
    required_role VARCHAR(100) NOT NULL DEFAULT 'analyst',
    risk_level VARCHAR(50) NOT NULL DEFAULT 'READ',
    timeout_seconds INTEGER NOT NULL DEFAULT 10,
    rate_limit_per_minute INTEGER NOT NULL DEFAULT 30,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def create_tables():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_TOOL_REGISTRY_TABLE)

        connection.commit()

    print("Tool registry table created successfully.")


if __name__ == "__main__":
    create_tables()