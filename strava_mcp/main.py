import logging

from strava_mcp.server import mcp

logger = logging.getLogger(__name__)


def main():
    """Run the Strava MCP server."""
    logger.info("Starting MCP server")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
