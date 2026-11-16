from app.database import get_connection


def main():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()

            print("Connected to PostgreSQL!")
            print(version[0])


if __name__ == "__main__":
    main()