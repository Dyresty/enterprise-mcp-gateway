from app.database import get_connection


def list_tables() -> list[dict]:
    """
    List user tables available in the PostgreSQL database.
    """

    query = """
        SELECT
            table_schema,
            table_name
        FROM information_schema.tables
        WHERE table_type = 'BASE TABLE'
          AND table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY table_schema, table_name;
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

    return [
        {
            "schema": row[0],
            "table": row[1],
        }
        for row in rows
    ]


def describe_table(
    schema: str,
    table: str,
) -> list[dict]:
    """
    Return column metadata for a PostgreSQL table.
    """

    query = """
        SELECT
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_schema = %s
          AND table_name = %s
        ORDER BY ordinal_position;
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (schema, table))
            rows = cursor.fetchall()

    return [
        {
            "column": row[0],
            "data_type": row[1],
            "nullable": row[2],
            "default": row[3],
        }
        for row in rows
    ]