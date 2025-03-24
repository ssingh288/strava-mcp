import logging
from strava_mcp.server import mcp

logger = logging.getLogger(__name__)

def main():
    """Run the Strava MCP server."""
    # Use fixed port 3008
    port = 3008
    logger.info(f"Using port {port} for MCP server")
    mcp.run(port=port)


if __name__ == "__main__":
    main()
