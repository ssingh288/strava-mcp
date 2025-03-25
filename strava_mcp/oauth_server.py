"""A standalone local server for handling Strava OAuth flow."""

import asyncio
import logging
import os
import webbrowser
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from strava_mcp.auth import REDIRECT_HOST, REDIRECT_PORT, StravaAuthenticator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class StravaOAuthServer:
    """A standalone server for handling Strava OAuth flow."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        host: str = REDIRECT_HOST,
        port: int = REDIRECT_PORT,
    ):
        """Initialize the OAuth server.

        Args:
            client_id: Strava API client ID
            client_secret: Strava API client secret
            host: Host for the server
            port: Port for the server
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.host = host
        self.port = port
        self.authenticator = None
        self.app = None
        self.server_thread = None
        self.token_future = asyncio.Future()
        self.server_task = None
        self.server = None

    async def get_token(self) -> str:
        """Get a refresh token by starting the OAuth flow.

        Returns:
            The refresh token

        Raises:
            Exception: If the OAuth flow fails
        """
        # Initialize the server if it hasn't been done yet
        if not self.app:
            await self._initialize_server()

        # Open browser to start authorization
        if self.authenticator is None:
            raise Exception("Authenticator not initialized")
        auth_url = self.authenticator.get_authorization_url()
        logger.info(f"Opening browser to authorize with Strava: {auth_url}")
        webbrowser.open(auth_url)

        # Wait for the token
        try:
            refresh_token = await self.token_future
            logger.info("Successfully obtained refresh token")
            return refresh_token
        except asyncio.CancelledError as err:
            logger.error("Token request was cancelled")
            raise Exception("OAuth flow was cancelled") from err
        except Exception as e:
            logger.exception("Error during OAuth flow")
            raise Exception(f"OAuth flow failed: {str(e)}") from e
        finally:
            # Stop the server once we have the token
            await self._stop_server()

    async def _initialize_server(self):
        """Initialize the FastAPI server for OAuth flow."""

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            yield
            # Cleanup resources if needed
            logger.info("OAuth server shutting down")

        # Create FastAPI app
        self.app = FastAPI(
            title="Strava OAuth",
            description="OAuth server for Strava authentication",
            lifespan=lifespan,
        )

        # Initialize authenticator
        self.authenticator = StravaAuthenticator(
            client_id=self.client_id,
            client_secret=self.client_secret,
            app=self.app,
            host=self.host,
            port=self.port,
        )

        # Store our token future in the authenticator
        self.authenticator.token_future = self.token_future

        # Set up routes
        self.authenticator.setup_routes(self.app)

        # Start server in a separate task
        self.server_task = asyncio.create_task(self._run_server())

        # Wait a moment for the server to start
        await asyncio.sleep(0.5)

    async def _run_server(self):
        """Run the uvicorn server."""
        # Ensure app is not None before passing to uvicorn
        if not self.app:
            raise ValueError("FastAPI app not initialized")

        # Use fixed port 3008
        try:
            config = uvicorn.Config(
                app=self.app,
                host=self.host,
                port=self.port,
                log_level="info",
            )

            self.server = uvicorn.Server(config)
            await self.server.serve()
        except Exception as e:
            logger.exception("Error running OAuth server")
            if not self.token_future.done():
                self.token_future.set_exception(e)

    async def _stop_server(self):
        """Stop the uvicorn server."""
        if self.server:
            self.server.should_exit = True
            if self.server_task:
                try:
                    await asyncio.wait_for(self.server_task, timeout=5.0)
                except TimeoutError:
                    logger.warning("Server shutdown timed out")


async def get_refresh_token_from_oauth(client_id: str, client_secret: str) -> str:
    """Get a refresh token by starting a standalone OAuth server.

    Args:
        client_id: Strava API client ID
        client_secret: Strava API client secret

    Returns:
        The refresh token

    Raises:
        Exception: If the OAuth flow fails
    """
    server = StravaOAuthServer(client_id, client_secret)
    return await server.get_token()


if __name__ == "__main__":
    # This allows running this file directly to get a refresh token
    import sys

    # Check if client_id and client_secret are provided as env vars
    client_id = os.environ.get("STRAVA_CLIENT_ID")
    client_secret = os.environ.get("STRAVA_CLIENT_SECRET")

    # If not provided as env vars, check command line args
    if not client_id or not client_secret:
        if len(sys.argv) != 3:
            print("Usage: python -m strava_mcp.oauth_server <client_id> <client_secret>")
            print("Or set STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET environment variables")
            sys.exit(1)
        client_id = sys.argv[1]
        client_secret = sys.argv[2]

    # Ensure we have non-None values
    if client_id is None or client_secret is None:
        print("Error: Missing client_id or client_secret")
        sys.exit(1)

    async def main():
        try:
            # We've verified these aren't None above
            assert client_id is not None and client_secret is not None
            token = await get_refresh_token_from_oauth(client_id, client_secret)
            print(f"\nSuccessfully obtained refresh token: {token}")
            print("\nYou can add this to your environment variables:")
            print(f"export STRAVA_REFRESH_TOKEN={token}")
        except Exception as e:
            logger.exception("Error getting refresh token")
            print(f"Error: {str(e)}")

    asyncio.run(main())
