import logging
from datetime import datetime

import httpx
from fastapi import FastAPI
from httpx import Response

from strava_mcp.config import StravaSettings
from strava_mcp.models import Activity, DetailedActivity, ErrorResponse, SegmentEffort

logger = logging.getLogger(__name__)


class StravaAPI:
    """Client for the Strava API."""

    def __init__(self, settings: StravaSettings, app: FastAPI | None = None):
        """Initialize the Strava API client.

        Args:
            settings: Strava API settings
            app: FastAPI app (not used, kept for backward compatibility)
        """
        self.settings = settings
        self.access_token = None
        self.token_expires_at = None
        self.auth_flow_in_progress = False
        self._client = httpx.AsyncClient(
            base_url=settings.base_url,
            timeout=30.0,
        )

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def setup_auth_routes(self):
        """This method is deprecated and does nothing now.
        Standalone OAuth server is used instead.
        """
        logger.info("Using standalone OAuth server instead of integrated auth routes")
        return

    async def start_auth_flow(self) -> str:
        """This method is deprecated.
        The standalone OAuth server is used instead via _ensure_token().

        Returns:
            The refresh token

        Raises:
            Exception: Always raises exception directing to use standalone flow
        """
        raise Exception(
            "Integrated auth flow is no longer supported. "
            "The standalone OAuth server will be used automatically when needed."
        )

    async def _ensure_token(self) -> str:
        """Ensure we have a valid access token.

        Returns:
            The access token

        Raises:
            Exception: If unable to obtain a valid token
        """
        now = datetime.now().timestamp()

        # If token is still valid, return it
        if self.access_token and self.token_expires_at and now < self.token_expires_at:
            return self.access_token

        # If we don't have a refresh token, try to get one through standalone OAuth flow
        if not self.settings.refresh_token:
            logger.warning("No refresh token available, launching standalone OAuth server")
            try:
                # Import here to avoid circular import
                from strava_mcp.oauth_server import get_refresh_token_from_oauth

                logger.info("Starting OAuth flow to get refresh token")
                self.settings.refresh_token = await get_refresh_token_from_oauth(
                    self.settings.client_id, self.settings.client_secret
                )
                logger.info("Successfully obtained refresh token from OAuth flow")
            except Exception as e:
                error_msg = f"Failed to get refresh token through OAuth flow: {e}"
                logger.error(error_msg)

                # No fallback to MCP-integrated auth flow anymore
                raise Exception(
                    "No refresh token available and OAuth flow failed. "
                    "Please set STRAVA_REFRESH_TOKEN manually in your environment variables."
                ) from e

        # Now that we have a refresh token, refresh the access token
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://www.strava.com/oauth/token",
                json={
                    "client_id": self.settings.client_id,
                    "client_secret": self.settings.client_secret,
                    "refresh_token": self.settings.refresh_token,
                    "grant_type": "refresh_token",
                },
            )

            if response.status_code != 200:
                error_msg = f"Failed to refresh token: {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)

            data = response.json()
            self.access_token = data["access_token"]
            self.token_expires_at = data["expires_at"]

            # Update the refresh token if it changed
            if "refresh_token" in data:
                self.settings.refresh_token = data["refresh_token"]

            logger.info("Successfully refreshed access token")
            return self.access_token

    async def _request(self, method: str, endpoint: str, **kwargs) -> Response:
        """Make a request to the Strava API.

        Args:
            method: The HTTP method to use
            endpoint: The API endpoint to call
            **kwargs: Additional arguments to pass to the HTTP client

        Returns:
            The HTTP response

        Raises:
            Exception: If the request fails
        """
        token = await self._ensure_token()
        headers = {"Authorization": f"Bearer {token}"}
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        url = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        response = await self._client.request(method, url, headers=headers, **kwargs)

        if not response.is_success:
            error_msg = f"Strava API request failed: {response.status_code} - {response.text}"
            logger.error(error_msg)

            try:
                error_data = response.json()
                error = ErrorResponse(**error_data)
                raise Exception(f"Strava API error: {error.message} (code: {error.code})")
            except Exception as err:
                msg = f"Strava API failed: {response.status_code} - {response.text[:50]}"
                raise Exception(msg) from err

        return response

    async def get_activities(
        self,
        before: int | None = None,
        after: int | None = None,
        page: int = 1,
        per_page: int = 30,
    ) -> list[Activity]:
        """Get a list of activities for the authenticated athlete.

        Args:
            before: An epoch timestamp for filtering activities before a certain time
            after: An epoch timestamp for filtering activities after a certain time
            page: Page number
            per_page: Number of items per page

        Returns:
            List of activities
        """
        params = {"page": page, "per_page": per_page}
        if before:
            params["before"] = before
        if after:
            params["after"] = after

        response = await self._request("GET", "/athlete/activities", params=params)
        data = response.json()

        return [Activity(**activity) for activity in data]

    async def get_activity(self, activity_id: int, include_all_efforts: bool = False) -> DetailedActivity:
        """Get a specific activity.

        Args:
            activity_id: The ID of the activity
            include_all_efforts: Whether to include all segment efforts

        Returns:
            The activity details
        """
        params = {}
        if include_all_efforts:
            params["include_all_efforts"] = "true"

        response = await self._request("GET", f"/activities/{activity_id}", params=params)
        data = response.json()

        return DetailedActivity(**data)

    async def get_activity_segments(self, activity_id: int) -> list[SegmentEffort]:
        """Get segments from a specific activity.

        Args:
            activity_id: The ID of the activity

        Returns:
            List of segment efforts for the activity
        """
        activity = await self.get_activity(activity_id, include_all_efforts=True)

        if not activity.segment_efforts:
            return []

        # Add missing required fields before validation
        segment_efforts = []
        for effort in activity.segment_efforts:
            # Add activity_id which is required by the model
            effort["activity_id"] = activity_id
            # Add segment_id which is required by the model
            effort["segment_id"] = effort["segment"]["id"]
            # Add total_elevation_gain to the segment if it's missing
            if "total_elevation_gain" not in effort["segment"]:
                # Calculate from elevation high and low or set to 0
                elev_high = effort["segment"].get("elevation_high", 0)
                elev_low = effort["segment"].get("elevation_low", 0)
                effort["segment"]["total_elevation_gain"] = max(0, elev_high - elev_low)

            segment_efforts.append(SegmentEffort.model_validate(effort))

        return segment_efforts
