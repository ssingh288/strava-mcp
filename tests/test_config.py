"""Tests for configuration module."""

import os
from unittest import mock

from strava_mcp.config import StravaSettings


def test_strava_settings_defaults():
    """Test default settings for StravaSettings."""
    # Use required parameters only
    with mock.patch.dict(os.environ, {}, clear=True):
        settings = StravaSettings(
            client_id="test_client_id",
            client_secret="test_client_secret",
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
        settings = StravaSettings()

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
            refresh_token="direct_refresh_token",
        )

        # Direct values should override environment variables
        assert settings.client_id == "direct_client_id"
        assert settings.client_secret == "env_client_secret"
        assert settings.refresh_token == "direct_refresh_token"


def test_strava_settings_model_config():
    """Test model configuration for StravaSettings."""
    assert StravaSettings.model_config["env_prefix"] == "STRAVA_"
    assert StravaSettings.model_config["env_file"] == ".env"
    assert StravaSettings.model_config["env_file_encoding"] == "utf-8"
