from app.database import get_connection


ADD_CACHE_COLUMNS = """
ALTER TABLE tool_registry
    ADD COLUMN IF NOT EXISTS cache_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS cache_ttl_seconds INTEGER NOT NULL DEFAULT 60;
"""


def migrate():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(ADD_CACHE_COLUMNS)

        connection.commit()

    print("Cache columns added successfully.")


if __name__ == "__main__":
    migrate()