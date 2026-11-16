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

    AUTH_USERNAME: str = os.getenv("AUTH_USERNAME", "analyst")

    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY",
        "development-only-secret-change-me",
    )
    JWT_ALGORITHM: str = os.getenv(
        "JWT_ALGORITHM",
        "HS256",
    )
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv(
            "JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
            "30",
        )
    )

    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))

    # Research project search (enterprise-hybrid-rag service)
    RAG_API_URL: str = os.getenv("RAG_API_URL", "http://127.0.0.1:8001")

    # File system tools: everything outside this folder is unreachable
    FILES_ROOT: str = os.getenv("FILES_ROOT", "workspace")

    # Agent
    GATEWAY_URL: str = os.getenv("GATEWAY_URL", "http://127.0.0.1:8000")
    LLM_BASE_URL: str | None = os.getenv("LLM_BASE_URL") or None
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4.1-mini")
    AGENT_MAX_STEPS: int = int(os.getenv("AGENT_MAX_STEPS", "8"))

    # A2A server exposing the agent to other agents
    A2A_URL: str = os.getenv("A2A_URL", "http://127.0.0.1:9000")


settings = Settings()