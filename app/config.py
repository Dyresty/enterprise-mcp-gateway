import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    APP_ENV: str = os.getenv("APP_ENV", "development")

    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "mcp_gateway")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "mcp_user")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")

    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")

settings = Settings()