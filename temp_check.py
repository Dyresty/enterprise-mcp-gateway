from app.database import get_connection


connection = get_connection()
cursor = connection.cursor()

cursor.execute("""
    SELECT
        column_name,
        data_type,
        column_default
    FROM information_schema.columns
    WHERE table_name = 'tool_execution_logs'
    ORDER BY ordinal_position;
""")

for row in cursor.fetchall():
    print(row)

cursor.close()
connection.close()