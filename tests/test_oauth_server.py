"""Tests for the Strava OAuth server module."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI

from strava_mcp.oauth_server import StravaOAuthServer, get_refresh_token_from_oauth


@pytest.fixture
def client_credentials():
    """Fixture for client credentials."""
    return {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
    }


@pytest.fixture
def oauth_server(client_credentials):
    """Fixture for StravaOAuthServer."""
    return StravaOAuthServer(
        client_id=client_credentials["client_id"],
        client_secret=client_credentials["client_secret"],
    )


@pytest.mark.asyncio
async def test_initialize_server(oauth_server):
    """Test initializing the server."""
    # Mock the OAuth server's dependencies directly
    with patch("strava_mcp.oauth_server.StravaAuthenticator") as mock_authenticator_class:
        with patch("asyncio.create_task") as mock_create_task:
            # Setup mocks
            mock_authenticator = MagicMock()
            mock_authenticator_class.return_value = mock_authenticator
            mock_task = MagicMock()
            mock_create_task.return_value = mock_task

            # Test method
            await oauth_server._initialize_server()

            # Verify FastAPI app was created
            assert oauth_server.app is not None
            assert oauth_server.app.title == "Strava OAuth"

            # Verify authenticator was created and configured
            mock_authenticator_class.assert_called_once_with(
                client_id=oauth_server.client_id,
                client_secret=oauth_server.client_secret,
                app=oauth_server.app,
                host=oauth_server.host,
                port=oauth_server.port,
            )
            assert oauth_server.authenticator == mock_authenticator

            # Verify token future was stored in authenticator
            assert mock_authenticator.token_future is oauth_server.token_future

            # Verify routes were set up
            mock_authenticator.setup_routes.assert_called_once_with(oauth_server.app)

            # Verify server task was created
            mock_create_task.assert_called_once()
            assert oauth_server.server_task == mock_task


@pytest.mark.asyncio
async def test_run_server(oauth_server):
    """Test running the server."""
    with patch("uvicorn.Server") as mock_server_class:
        with patch("uvicorn.Config") as mock_config_class:
            # Setup mocks
            mock_server = AsyncMock()
            mock_server_class.return_value = mock_server
            mock_config = MagicMock()
            mock_config_class.return_value = mock_config

            # Create app
            oauth_server.app = FastAPI()

            # Test method
            await oauth_server._run_server()

            # Verify config was created correctly
            mock_config_class.assert_called_once_with(
                app=oauth_server.app,
                host=oauth_server.host,
                port=oauth_server.port,
                log_level="info",
            )

            # Verify server was created and run
            mock_server_class.assert_called_once_with(mock_config)
            mock_server.serve.assert_called_once()
            assert oauth_server.server == mock_server


@pytest.mark.asyncio
async def test_run_server_exception(oauth_server):
    """Test running the server with an exception."""
    with patch("uvicorn.Server") as mock_server_class:
        with patch("uvicorn.Config") as mock_config_class:
            # Setup mocks
            mock_server = AsyncMock()
            mock_server.serve = AsyncMock(side_effect=Exception("Test error"))
            mock_server_class.return_value = mock_server
            mock_config = MagicMock()
            mock_config_class.return_value = mock_config

            # Create app and token future
            oauth_server.app = FastAPI()
            oauth_server.token_future = asyncio.Future()

            # Test method
            await oauth_server._run_server()

            # Verify token future has exception
            assert oauth_server.token_future.done()
            with pytest.raises(Exception, match="Test error"):
                await oauth_server.token_future


@pytest.mark.asyncio
async def test_stop_server(oauth_server):
    """Test stopping the server."""
    # Setup server and task
    oauth_server.server = MagicMock()
    oauth_server.server_task = MagicMock()
    oauth_server.server_task.done = MagicMock(return_value=False)

    # Make asyncio.wait_for return immediately
    with patch("asyncio.wait_for", new=AsyncMock()) as mock_wait_for:
        # Test method
        await oauth_server._stop_server()

        # Verify server was stopped
        assert oauth_server.server.should_exit is True
        mock_wait_for.assert_called_once_with(oauth_server.server_task, timeout=5.0)


@pytest.mark.asyncio
async def test_stop_server_timeout(oauth_server):
    """Test stopping the server with timeout."""
    # Setup server and task
    oauth_server.server = MagicMock()
    oauth_server.server_task = MagicMock()
    oauth_server.server_task.done = MagicMock(return_value=False)

    # Make asyncio.wait_for raise TimeoutError
    with patch("asyncio.wait_for", new=AsyncMock(side_effect=TimeoutError())) as mock_wait_for:
        # Test method
        await oauth_server._stop_server()

        # Verify server was stopped
        assert oauth_server.server.should_exit is True
        mock_wait_for.assert_called_once_with(oauth_server.server_task, timeout=5.0)


@pytest.mark.asyncio
async def test_get_token(oauth_server):
    """Test getting a token."""
    # Setup mocks
    oauth_server._initialize_server = AsyncMock()
    oauth_server._stop_server = AsyncMock()
    oauth_server.authenticator = MagicMock()
    oauth_server.authenticator.get_authorization_url = MagicMock(return_value="https://example.com/auth")

    with patch("webbrowser.open") as mock_open:
        # Prepare token future
        oauth_server.token_future = asyncio.Future()
        oauth_server.token_future.set_result("test_refresh_token")

        # Test method
        token = await oauth_server.get_token()

        # Verify
        assert token == "test_refresh_token"
        oauth_server._initialize_server.assert_called_once()
        oauth_server.authenticator.get_authorization_url.assert_called_once()
        mock_open.assert_called_once_with("https://example.com/auth")
        oauth_server._stop_server.assert_called_once()


@pytest.mark.asyncio
async def test_get_token_no_authenticator(oauth_server):
    """Test getting a token with no authenticator."""
    # Setup mocks
    oauth_server._initialize_server = AsyncMock()
    oauth_server._stop_server = AsyncMock()
    oauth_server.authenticator = None

    # Test method
    with pytest.raises(Exception, match="Authenticator not initialized"):
        await oauth_server.get_token()

    # Verify
    oauth_server._initialize_server.assert_called_once()
    # The stop server is not called because we exit with exception before getting there
    # oauth_server._stop_server.assert_called_once()


@pytest.mark.asyncio
async def test_get_token_cancelled(oauth_server):
    """Test getting a token that is cancelled."""
    # Setup mocks
    oauth_server._initialize_server = AsyncMock()
    oauth_server._stop_server = AsyncMock()
    oauth_server.authenticator = MagicMock()
    oauth_server.authenticator.get_authorization_url = MagicMock(return_value="https://example.com/auth")

    with patch("webbrowser.open") as mock_open:
        # Prepare token future with cancellation
        oauth_server.token_future = asyncio.Future()
        oauth_server.token_future.cancel()

        # Test method
        with pytest.raises(Exception, match="OAuth flow was cancelled"):
            await oauth_server.get_token()

        # Verify
        oauth_server._initialize_server.assert_called_once()
        oauth_server.authenticator.get_authorization_url.assert_called_once()
        mock_open.assert_called_once_with("https://example.com/auth")
        oauth_server._stop_server.assert_called_once()


@pytest.mark.asyncio
async def test_get_token_exception(oauth_server):
    """Test getting a token with exception."""
    # Setup mocks
    oauth_server._initialize_server = AsyncMock()
    oauth_server._stop_server = AsyncMock()
    oauth_server.authenticator = MagicMock()
    oauth_server.authenticator.get_authorization_url = MagicMock(return_value="https://example.com/auth")

    with patch("webbrowser.open") as mock_open:
        # Prepare token future with exception
        oauth_server.token_future = asyncio.Future()
        oauth_server.token_future.set_exception(Exception("Test error"))

        # Test method
        with pytest.raises(Exception, match="OAuth flow failed: Test error"):
            await oauth_server.get_token()

        # Verify
        oauth_server._initialize_server.assert_called_once()
        oauth_server.authenticator.get_authorization_url.assert_called_once()
        mock_open.assert_called_once_with("https://example.com/auth")
        oauth_server._stop_server.assert_called_once()


@pytest.mark.asyncio
async def test_get_refresh_token_from_oauth(client_credentials):
    """Test get_refresh_token_from_oauth function."""
    with patch("strava_mcp.oauth_server.StravaOAuthServer") as mock_oauth_server_class:
        # Setup mock
        mock_server = MagicMock()
        mock_server.get_token = AsyncMock(return_value="test_refresh_token")
        mock_oauth_server_class.return_value = mock_server

        # Test function
        token = await get_refresh_token_from_oauth(client_credentials["client_id"], client_credentials["client_secret"])

        # Verify
        assert token == "test_refresh_token"
        mock_oauth_server_class.assert_called_once_with(
            client_credentials["client_id"], client_credentials["client_secret"]
        )
        mock_server.get_token.assert_called_once()
