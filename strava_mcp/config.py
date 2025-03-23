from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class StravaSettings(BaseSettings):
    """Strava API settings."""

    client_id: str = Field(..., description="Strava API client ID")
    client_secret: str = Field(..., description="Strava API client secret")
    refresh_token: str | None = Field(
        default=None,
        description="Strava API refresh token (can be generated through auth flow)",
    )
    base_url: str = Field("https://www.strava.com/api/v3", description="Strava API base URL")

    model_config = SettingsConfigDict(env_prefix="STRAVA_", env_file=".env", env_file_encoding="utf-8")

    @model_validator(mode="after")
    def load_from_env(self):
        """Load values from environment variables if not directly provided."""
        import os

        # Only override empty values with environment values
        if not self.client_id and os.environ.get("STRAVA_CLIENT_ID"):
            self.client_id = os.environ["STRAVA_CLIENT_ID"]

        if not self.client_secret and os.environ.get("STRAVA_CLIENT_SECRET"):
            self.client_secret = os.environ["STRAVA_CLIENT_SECRET"]

        if not self.refresh_token and os.environ.get("STRAVA_REFRESH_TOKEN"):
            self.refresh_token = os.environ["STRAVA_REFRESH_TOKEN"]

        if not self.base_url and os.environ.get("STRAVA_BASE_URL"):
            self.base_url = os.environ["STRAVA_BASE_URL"]

        return self
