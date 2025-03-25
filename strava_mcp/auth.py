import asyncio
import logging
import os
import webbrowser
from urllib.parse import urlencode

import httpx
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Constants
AUTHORIZE_URL = "https://www.strava.com/oauth/authorize"
TOKEN_URL = "https://www.strava.com/oauth/token"
REDIRECT_PORT = 3008
REDIRECT_HOST = "127.0.0.1"


class TokenResponse(BaseModel):
    """Response model for Strava token exchange."""

    access_token: str
    refresh_token: str
    expires_at: int
    expires_in: int
    token_type: str


class StravaAuthenticator:
    """Helper class to get a Strava refresh token via OAuth flow."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        app: FastAPI | None = None,
        redirect_path: str = "/exchange_token",
        host: str = REDIRECT_HOST,
        port: int = REDIRECT_PORT,
    ):
        """Initialize the authenticator.

        Args:
            client_id: Strava API client ID
            client_secret: Strava API client secret
            app: Existing FastAPI app to add routes to (optional)
            redirect_path: Path for the redirect URI
            host: Host for the redirect URI
            port: Port for the redirect URI
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_path = redirect_path
        self.host = host
        self.port = port
        self.redirect_uri = f"http://{host}:{port}{redirect_path}"
        self.refresh_token = None
        self.token_future = None
        self.app = app

    async def exchange_token(self, code: str = Query(...)):
        """Exchange the authorization code for a refresh token.

        Args:
            code: The authorization code from Strava

        Returns:
            HTML response indicating success or failure
        """
        try:
            # Exchange the code for tokens
            token_data = await self._exchange_code_for_token(code)

            # If we have a token future (waiting for token), set the result
            if self.token_future and not self.token_future.done():
                self.token_future.set_result(token_data.refresh_token)

            return HTMLResponse(
                "<h1>Authorization successful!</h1><p>You can close this tab and return to the application.</p>"
            )
        except Exception as e:
            logger.exception("Error during token exchange")

            # If we have a token future (waiting for token), set the exception
            if self.token_future and not self.token_future.done():
                self.token_future.set_exception(e)

            return HTMLResponse("<h1>Authorization failed!</h1><p>An error occurred. Please check the logs.</p>")

    async def _exchange_code_for_token(self, code: str) -> TokenResponse:
        """Exchange the authorization code for tokens.

        Args:
            code: The authorization code from Strava

        Returns:
            The token response

        Raises:
            Exception: If the token exchange fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                TOKEN_URL,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                },
            )

            if response.status_code != 200:
                error_msg = f"Failed to exchange token: {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)

            data = response.json()
            token_data = TokenResponse(**data)
            self.refresh_token = token_data.refresh_token
            return token_data

    def get_authorization_url(self):
        """Generate the authorization URL.

        Returns:
            The authorization URL to redirect the user to
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "approval_prompt": "force",
            "scope": "read_all,activity:read,activity:read_all,profile:read_all",
        }
        return f"{AUTHORIZE_URL}?{urlencode(params)}"

    def setup_routes(self, app: FastAPI | None = None):
        """Set up the routes for authentication.

        Args:
            app: The FastAPI app to add routes to
        """
        target_app = app or self.app
        if not target_app:
            raise ValueError("No FastAPI app provided")

        # Make sure we have a valid FastAPI app
        if not hasattr(target_app, "add_api_route"):
            raise ValueError("Provided app does not appear to be a valid FastAPI instance")

        # Add route for the token exchange
        target_app.add_api_route(self.redirect_path, self.exchange_token, methods=["GET"])

        # Add route to start the auth flow
        target_app.add_api_route("/auth", self.start_auth_flow, methods=["GET"])

    async def start_auth_flow(self):
        """Start the OAuth flow by redirecting to Strava.

        Returns:
            Redirect response to Strava authorization URL
        """
        auth_url = self.get_authorization_url()
        logger.info(f"Starting auth flow with URL: {auth_url}")
        return RedirectResponse(auth_url)

    async def get_refresh_token(self, open_browser: bool = True) -> str:
        """Start the OAuth flow and wait for the token.

        Args:
            open_browser: Whether to automatically open the browser

        Returns:
            The refresh token

        Raises:
            Exception: If the authentication process fails
        """
        # Create a future to wait for the token
        self.token_future = asyncio.Future()

        # Open the browser for authorization if requested
        auth_url = self.get_authorization_url()
        if open_browser:
            logger.info(f"Opening browser to authorize: {auth_url}")
            browser_opened = webbrowser.open(auth_url)
            if not browser_opened:
                logger.warning("Failed to open browser automatically. Please open the URL manually.")
                logger.info(f"Authorization URL: {auth_url}")
        else:
            logger.info(f"Please open this URL to authorize: {auth_url}")

        # Wait for the token
        return await self.token_future


async def get_strava_refresh_token(client_id: str, client_secret: str, app: FastAPI | None = None) -> str:
    """Get a Strava refresh token via OAuth flow.

    Args:
        client_id: Strava API client ID
        client_secret: Strava API client secret
        app: Existing FastAPI app to add routes to (optional)

    Returns:
        The refresh token

    Raises:
        Exception: If the authentication process fails
    """
    authenticator = StravaAuthenticator(client_id, client_secret, app)
    if app:
        authenticator.setup_routes(app)
    return await authenticator.get_refresh_token()


if __name__ == "__main__":
    # This allows running this file directly to get a refresh token
    import sys

    import uvicorn

    logging.basicConfig(level=logging.INFO)

    # Check if client_id and client_secret are provided as env vars
    client_id = os.environ.get("STRAVA_CLIENT_ID")
    client_secret = os.environ.get("STRAVA_CLIENT_SECRET")

    # If not provided as env vars, check command line args
    if not client_id or not client_secret:
        if len(sys.argv) != 3:
            print("Usage: python -m strava_mcp.auth <client_id> <client_secret>")
            print("Or set STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET environment variables")
            sys.exit(1)
        client_id = sys.argv[1]
        client_secret = sys.argv[2]

    # Create a FastAPI app for standalone operation
    app = FastAPI(title="Strava Auth")
    authenticator = StravaAuthenticator(client_id, client_secret, app)
    authenticator.setup_routes(app)

    # Add a root route that redirects to the auth flow
    @app.get("/")
    async def root():
        return RedirectResponse("/auth")

    async def main():
        # Start the server
        server = uvicorn.Server(
            config=uvicorn.Config(
                app=app,
                host=REDIRECT_HOST,
                port=REDIRECT_PORT,
                log_level="info",
            )
        )

        # For standalone operation, we'll print instructions
        print("\nStrava Authentication Server")
        print(f"Open http://{REDIRECT_HOST}:{REDIRECT_PORT}/ in your browser to start authentication")

        # Run the server (this will block until stopped)
        await server.serve()

    asyncio.run(main())
