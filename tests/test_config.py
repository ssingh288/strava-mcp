"""Tests for configuration module."""

import os
from unittest import mock

from strava_mcp.config import StravaSettings


def test_strava_settings_defaults():
    """Test default settings for StravaSettings."""
    # Use required parameters only
    with mock.patch.dict(os.environ, {}, clear=True):
        # Explicitly ensure we're not using STRAVA_REFRESH_TOKEN from environment
        settings = StravaSettings(
            client_id="test_client_id",
            client_secret="test_client_secret",
            refresh_token=None,
            base_url="https://www.strava.com/api/v3",
        )

        assert settings.client_id == "test_client_id"
        assert settings.client_secret == "test_client_secret"
        assert settings.refresh_token is None
        assert settings.base_url == "https://www.strava.com/api/v3"


def test_strava_settings_from_env():
    """Test loading settings from environment variables."""
    with mock.patch.dict(
        os.environ,
        {
            "STRAVA_CLIENT_ID": "env_client_id",
            "STRAVA_CLIENT_SECRET": "env_client_secret",
            "STRAVA_REFRESH_TOKEN": "env_refresh_token",
            "STRAVA_BASE_URL": "https://custom.strava.api/v3",
        },
    ):
        # Even with env vars, we need to provide required params for type checking
        settings = StravaSettings(
            client_id="",  # Will be overridden by env vars
            client_secret="",  # Will be overridden by env vars
            base_url="",  # Will be overridden by env vars
        )

        assert settings.client_id == "env_client_id"
        assert settings.client_secret == "env_client_secret"
        assert settings.refresh_token == "env_refresh_token"
        assert settings.base_url == "https://custom.strava.api/v3"


def test_strava_settings_override():
    """Test overriding environment settings with direct values."""
    with mock.patch.dict(
        os.environ,
        {
            "STRAVA_CLIENT_ID": "env_client_id",
            "STRAVA_CLIENT_SECRET": "env_client_secret",
            "STRAVA_REFRESH_TOKEN": "env_refresh_token",
        },
    ):
        settings = StravaSettings(
            client_id="direct_client_id",
            client_secret="",  # Will be taken from env vars
            refresh_token="direct_refresh_token",
            base_url="https://www.strava.com/api/v3",
        )

        # Direct values should override environment variables
        assert settings.client_id == "direct_client_id"
        assert settings.client_secret == "env_client_secret"
        assert settings.refresh_token == "direct_refresh_token"


def test_strava_settings_model_config():
    """Test model configuration for StravaSettings."""
    # Access model_config safely, with type handling
    model_config = StravaSettings.model_config
    # We can safely access these fields as we know they exist in our configuration
    assert model_config.get("env_prefix") == "STRAVA_"
    assert model_config.get("env_file") == ".env"
    assert model_config.get("env_file_encoding") == "utf-8"
