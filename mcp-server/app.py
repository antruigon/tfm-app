from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

mcp = FastMCP("tfm-mcp-server")


@mcp.tool
def echo(message: str) -> str:
    """Devuelve el mensaje recibido (herramienta de prueba para el chatbot)."""
    return f"Echo desde MCP: {message}"


@mcp.tool
def ping() -> str:
    """Comprueba que el servidor MCP responde."""
    return "pong"


@mcp.custom_route("/health", methods=["GET"])
async def health_check(_request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok"})


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
