from app.database import get_connection


def set_tool_enabled(tool_name: str, enabled: bool):
    query = """
    UPDATE tool_registry
    SET enabled = %s,
        updated_at = CURRENT_TIMESTAMP
    WHERE name = %s;
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (enabled, tool_name))

            if cursor.rowcount == 0:
                print(f"Tool '{tool_name}' was not found.")
                return

        connection.commit()

    status = "enabled" if enabled else "disabled"
    print(f"Tool '{tool_name}' {status}.")


if __name__ == "__main__":
    set_tool_enabled("add", True)