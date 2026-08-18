from app.database import get_connection

c = get_connection()
cur = c.cursor()

cur.execute("""
    SELECT
        name,
        risk_level,
        cache_enabled,
        cache_ttl_seconds
    FROM tool_registry
    ORDER BY name;
""")

for row in cur.fetchall():
    print(row)

c.close()