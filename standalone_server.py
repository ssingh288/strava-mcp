"""A standalone web server for testing the Strava OAuth flow."""

import asyncio
import logging
import webbrowser
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from strava_mcp.auth import StravaAuthenticator
from strava_mcp.config import StravaSettings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Set up and tear down the application.

    Args:
        app: The FastAPI app
    """
    # Load settings from environment variables
    try:
        settings = StravaSettings()
        logger.info("Loaded Strava API settings")
    except Exception as e:
        logger.error(f"Failed to load Strava API settings: {str(e)}")
        raise

    # Set up the Strava authenticator
    authenticator = StravaAuthenticator(
        client_id=settings.client_id,
        client_secret=settings.client_secret,
        app=app,
    )
    authenticator.setup_routes(app)

    # Store settings and authenticator in app state
    app.state.settings = settings
    app.state.authenticator = authenticator

    # Log the current state of the refresh token
    if settings.refresh_token:
        logger.info("Refresh token is already set")
    else:
        logger.info("No refresh token set, you will need to authenticate")

    yield

    # Clean up resources
    logger.info("Shutting down")


# Create the FastAPI app
app = FastAPI(
    title="Strava OAuth Tester",
    description="A standalone web server for testing the Strava OAuth flow",
    lifespan=lifespan,
)


# Define the root route
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Root endpoint."""
    settings = request.app.state.settings

    # Check if we have a refresh token
    if settings.refresh_token:
        return HTMLResponse(
            f"""
            <html>
                <head>
                    <title>Strava OAuth Tester</title>
                </head>
                <body>
                    <h1>Strava OAuth Tester</h1>
                    <p>You already have a refresh token.</p>
                    <p>Your refresh token: <code>{settings.refresh_token}</code></p>
                    <p><a href="/auth">Reauthenticate</a></p>
                </body>
            </html>
            """
        )
    else:
        return HTMLResponse(
            """
            <html>
                <head>
                    <title>Strava OAuth Tester</title>
                </head>
                <body>
                    <h1>Strava OAuth Tester</h1>
                    <p>You need to authenticate with Strava.</p>
                    <p><a href="/auth">Authenticate</a></p>
                </body>
            </html>
            """
        )


# Define a route to get the refresh token manually
@app.get("/get_token", response_class=HTMLResponse)
async def get_token(request: Request):
    """Get a refresh token manually."""
    settings = request.app.state.settings
    authenticator = request.app.state.authenticator

    # Start the auth flow
    auth_future = asyncio.Future()

    # Store the old token future and replace it with our own
    old_token_future = authenticator.token_future
    authenticator.token_future = auth_future

    try:
        # Open the browser for authorization
        auth_url = authenticator.get_authorization_url()
        logger.info(f"Opening browser to authorize: {auth_url}")
        webbrowser.open(auth_url)

        # Wait for the token with a timeout
        try:
            refresh_token = await asyncio.wait_for(
                auth_future, timeout=300
            )  # 5 minutes timeout
            settings.refresh_token = refresh_token
            return HTMLResponse(
                f"""
                <html>
                    <head>
                        <title>Strava OAuth Tester</title>
                        <meta http-equiv="refresh" content="5;url=/" />
                    </head>
                    <body>
                        <h1>Strava OAuth Tester</h1>
                        <p>Successfully obtained refresh token!</p>
                        <p>Your refresh token: <code>{refresh_token}</code></p>
                        <p>You will be redirected to the home page in 5 seconds...</p>
                    </body>
                </html>
                """
            )
        except TimeoutError:
            return HTMLResponse(
                """
                <html>
                    <head>
                        <title>Strava OAuth Tester</title>
                    </head>
                    <body>
                        <h1>Strava OAuth Tester</h1>
                        <p>Timed out waiting for authentication.</p>
                        <p><a href="/get_token">Try again</a></p>
                    </body>
                </html>
                """
            )
    finally:
        # Restore the old token future
        authenticator.token_future = old_token_future


# Run the server
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
