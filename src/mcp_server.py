# src/mcp_server.py
import logging
import os
from datetime import datetime

from mcp.server.fastmcp import FastMCP


def configure_logging() -> None:
    log_level_name = os.getenv("MCP_LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


logger = logging.getLogger("mcp_server")

server = FastMCP(
    "test-mcp",
    host=os.getenv("MCP_HOST", "127.0.0.1"),
    port=int(os.getenv("MCP_PORT", "8010")),
    log_level=os.getenv("MCP_LOG_LEVEL", "INFO").upper(),
)


@server.tool(description="Echo de teruggegeven tekst")
def echo(message: str) -> str:
    logger.info("echo called with length=%d", len(message))
    return f"Echo: {message}"


@server.tool(description="Geeft de lokale datum en tijd terug")
def get_time() -> str:
    now = datetime.now().isoformat(timespec="seconds")
    logger.info("get_time returning current local datetime")
    return now

if __name__ == "__main__":
    configure_logging()
    transport = os.getenv("MCP_TRANSPORT", "streamable-http")
    logger.info("Starting MCP server '%s' with transport=%s", "test-mcp", transport)
    server.run(transport=transport)