from fastapi import FastAPI


app = FastAPI(
    title="Enterprise MCP Tool Gateway",
    description="Secure tool gateway for AI agents",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "enterprise-mcp-gateway",
        "version": "0.1.0",
    }