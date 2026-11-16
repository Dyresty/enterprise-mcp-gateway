import os


def langfuse_enabled() -> bool:
    return bool(
        os.getenv("LANGFUSE_PUBLIC_KEY")
        and os.getenv("LANGFUSE_SECRET_KEY")
    )


def get_callbacks() -> list:
    """
    Langfuse callback handler for LangChain/LangGraph runs.
    Tracing is optional: without Langfuse keys the agent runs untraced.
    """

    if not langfuse_enabled():
        return []

    from langfuse.langchain import CallbackHandler

    return [CallbackHandler()]


def flush() -> None:
    # Traces are sent in the background; flush before a short-lived process exits.
    if langfuse_enabled():
        from langfuse import get_client

        get_client().flush()
