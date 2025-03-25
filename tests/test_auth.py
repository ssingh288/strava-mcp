"""Tests for the Strava authentication module."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import Response

from strava_mcp.auth import StravaAuthenticator, get_strava_refresh_token


@pytest.fixture
def client_credentials():
    """Fixture for client credentials."""
    return {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
    }


@pytest.fixture
def mock_token_response():
    """Fixture for token response."""
    return {
        "access_token": "test_access_token",
        "refresh_token": "test_refresh_token",
        "expires_at": 1609459200,
        "expires_in": 21600,
        "token_type": "Bearer",
    }


@pytest.fixture
def fastapi_app():
    """Fixture for FastAPI app."""
    return FastAPI()


@pytest.fixture
def authenticator(client_credentials, fastapi_app):
    """Fixture for StravaAuthenticator."""
    return StravaAuthenticator(
        client_id=client_credentials["client_id"],
        client_secret=client_credentials["client_secret"],
        app=fastapi_app,
    )


def test_get_authorization_url(authenticator):
    """Test getting the authorization URL."""
    url = authenticator.get_authorization_url()

    # Check that the URL contains the expected parameters
    assert "https://www.strava.com/oauth/authorize" in url
    assert f"client_id={authenticator.client_id}" in url
    # URL is encoded, so we need to check the non-encoded parts
    assert "redirect_uri=http%3A%2F%2F127.0.0.1%3A3008%2Fexchange_token" in url
    assert "response_type=code" in url
    assert "scope=" in url


def test_setup_routes(authenticator, fastapi_app):
    """Test setting up routes."""
    authenticator.setup_routes(fastapi_app)

    # Check that the routes were added
    routes = [route.path for route in fastapi_app.routes]
    assert authenticator.redirect_path in routes
    assert "/auth" in routes


def test_setup_routes_no_app(authenticator):
    """Test setting up routes with no app."""
    authenticator.app = None
    with pytest.raises(ValueError, match="No FastAPI app provided"):
        authenticator.setup_routes()


@pytest.mark.asyncio
async def test_exchange_token_success(authenticator, mock_token_response):
    """Test exchanging token successfully."""
    # Setup mock
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = mock_token_response
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

        # Set up a future to receive the token
        authenticator.token_future = asyncio.Future()

        # Call the handler
        response = await authenticator.exchange_token(code="test_code")

        # Check response
        assert response.status_code == 200
        assert "Authorization successful" in response.body.decode()

        # Check token future
        assert authenticator.token_future.done()
        assert await authenticator.token_future == "test_refresh_token"

        # Check token was saved
        assert authenticator.refresh_token == "test_refresh_token"

        # Verify correct API call
        mock_client.return_value.__aenter__.return_value.post.assert_called_once()
        args, kwargs = mock_client.return_value.__aenter__.return_value.post.call_args
        assert args[0] == "https://www.strava.com/oauth/token"
        assert kwargs["data"]["client_id"] == authenticator.client_id
        assert kwargs["data"]["client_secret"] == authenticator.client_secret
        assert kwargs["data"]["code"] == "test_code"
        assert kwargs["data"]["grant_type"] == "authorization_code"


@pytest.mark.asyncio
async def test_exchange_token_failure(authenticator):
    """Test exchanging token with failure."""
    # Setup mock
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 400
        mock_response.text = "Invalid code"
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

        # Set up a future to receive the token
        authenticator.token_future = asyncio.Future()

        # Call the handler
        response = await authenticator.exchange_token(code="invalid_code")

        # Check response
        assert response.status_code == 200
        assert "Authorization failed" in response.body.decode()

        # Check token future
        assert authenticator.token_future.done()
        # We expect a specific exception here, so using pytest.raises is appropriate
        with pytest.raises(Exception):  # noqa: B017
            await authenticator.token_future


@pytest.mark.asyncio
async def test_start_auth_flow(authenticator):
    """Test starting auth flow."""
    with patch.object(authenticator, "get_authorization_url", return_value="https://example.com/auth"):
        response = await authenticator.start_auth_flow()
        assert response.status_code == 307
        assert response.headers["location"] == "https://example.com/auth"


@pytest.mark.asyncio
async def test_get_refresh_token(authenticator):
    """Test getting refresh token."""
    # Mock the webbrowser.open call
    with patch("webbrowser.open", return_value=True) as mock_open:
        with patch.object(authenticator, "get_authorization_url", return_value="https://example.com/auth"):
            # Set the future result after a delay
            authenticator.token_future = None  # Reset it so a new one is created

            # Start the token request in background
            task = asyncio.create_task(authenticator.get_refresh_token())

            # Wait a bit and set the result
            await asyncio.sleep(0.1)
            # Initialize the token_future before setting result
            if not authenticator.token_future:
                authenticator.token_future = asyncio.Future()
            authenticator.token_future.set_result("test_refresh_token")

            # Get the result
            token = await task

            # Verify
            assert token == "test_refresh_token"
            mock_open.assert_called_once_with("https://example.com/auth")


@pytest.mark.asyncio
async def test_get_refresh_token_no_browser(authenticator):
    """Test getting refresh token without opening browser."""
    with patch("webbrowser.open") as mock_open:
        with patch.object(authenticator, "get_authorization_url", return_value="https://example.com/auth"):
            # Set the future result after a delay
            authenticator.token_future = None  # Reset it so a new one is created

            # Start the token request in background
            task = asyncio.create_task(authenticator.get_refresh_token(open_browser=False))

            # Wait a bit and set the result
            await asyncio.sleep(0.1)
            # Initialize the token_future before setting result
            if not authenticator.token_future:
                authenticator.token_future = asyncio.Future()
            authenticator.token_future.set_result("test_refresh_token")

            # Get the result
            token = await task

            # Verify
            assert token == "test_refresh_token"
            mock_open.assert_not_called()


@pytest.mark.asyncio
async def test_get_refresh_token_browser_fails(authenticator):
    """Test getting refresh token with browser opening failing."""
    with patch("webbrowser.open", return_value=False) as mock_open:
        with patch.object(authenticator, "get_authorization_url", return_value="https://example.com/auth"):
            # Set the future result after a delay
            authenticator.token_future = None  # Reset it so a new one is created

            # Start the token request in background
            task = asyncio.create_task(authenticator.get_refresh_token())

            # Wait a bit and set the result
            await asyncio.sleep(0.1)
            # Initialize the token_future before setting result
            if not authenticator.token_future:
                authenticator.token_future = asyncio.Future()
            authenticator.token_future.set_result("test_refresh_token")

            # Get the result
            token = await task

            # Verify
            assert token == "test_refresh_token"
            mock_open.assert_called_once_with("https://example.com/auth")


@pytest.mark.asyncio
async def test_get_strava_refresh_token(client_credentials):
    """Test get_strava_refresh_token function."""
    with patch("strava_mcp.auth.StravaAuthenticator") as mock_authenticator_class:
        # Setup mock
        mock_authenticator = MagicMock()
        mock_authenticator.get_refresh_token = AsyncMock(return_value="test_refresh_token")
        mock_authenticator.setup_routes = MagicMock()
        mock_authenticator_class.return_value = mock_authenticator

        # Test without app
        token = await get_strava_refresh_token(client_credentials["client_id"], client_credentials["client_secret"])

        # Verify
        assert token == "test_refresh_token"
        mock_authenticator_class.assert_called_once_with(
            client_credentials["client_id"], client_credentials["client_secret"], None
        )
        mock_authenticator.setup_routes.assert_not_called()

        # Reset mocks
        mock_authenticator_class.reset_mock()
        mock_authenticator.get_refresh_token.reset_mock()
        mock_authenticator.setup_routes.reset_mock()

        # Test with app
        app = FastAPI()
        token = await get_strava_refresh_token(
            client_credentials["client_id"], client_credentials["client_secret"], app
        )

        # Verify
        assert token == "test_refresh_token"
        mock_authenticator_class.assert_called_once_with(
            client_credentials["client_id"], client_credentials["client_secret"], app
        )
        mock_authenticator.setup_routes.assert_called_once_with(app)
