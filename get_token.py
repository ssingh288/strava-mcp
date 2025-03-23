#!/usr/bin/env python
"""Script to get a Strava refresh token through OAuth flow."""

import asyncio
import logging
import os
import sys

from strava_mcp.oauth_server import get_refresh_token_from_oauth

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    """Get a Strava refresh token."""
    # Check if client_id and client_secret are provided as env vars
    client_id = os.environ.get("STRAVA_CLIENT_ID")
    client_secret = os.environ.get("STRAVA_CLIENT_SECRET")

    # If not provided as env vars, check command line args
    if not client_id or not client_secret:
        if len(sys.argv) != 3:
            print("Usage: python get_token.py <client_id> <client_secret>")
            print("Or set STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET environment variables")
            sys.exit(1)
        client_id = sys.argv[1]
        client_secret = sys.argv[2]

    print("\nStarting Strava OAuth flow to get a refresh token...")

    try:
        token = await get_refresh_token_from_oauth(client_id, client_secret)
        print("\n=================================================================")
        print("SUCCESS! Add this to your environment variables:")
        print(f"export STRAVA_REFRESH_TOKEN={token}")
        print("=================================================================\n")

        # Also write to a file for easy access
        with open("strava_token.txt", "w") as f:
            f.write(f"STRAVA_REFRESH_TOKEN={token}\n")
        print("Token also saved to strava_token.txt\n")

    except Exception as e:
        logger.exception("Error getting refresh token")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
