from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class StravaSettings(BaseSettings):
    """Strava API settings."""

    client_id: str = Field(..., description="Strava API client ID")
    client_secret: str = Field(..., description="Strava API client secret")
    refresh_token: str | None = Field(
        None,
        description="Strava API refresh token (can be generated through auth flow)",
    )
    base_url: str = Field(
        "https://www.strava.com/api/v3", description="Strava API base URL"
    )

    model_config = SettingsConfigDict(
        env_prefix="STRAVA_", env_file=".env", env_file_encoding="utf-8"
    )
