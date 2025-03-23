import logging
from datetime import datetime
from typing import Optional

import httpx
from fastapi import FastAPI
from httpx import Response

from strava_mcp.config import StravaSettings
from strava_mcp.models import (
    Activity,
    DetailedActivity,
    ErrorResponse,
    SegmentEffort,
)

logger = logging.getLogger(__name__)


class StravaAPI:
    """Client for the Strava API."""

    def __init__(self, settings: StravaSettings, app: Optional[FastAPI] = None):
        """Initialize the Strava API client.

        Args:
            settings: Strava API settings
            app: FastAPI app for auth routes (optional)
        """
        self.settings = settings
        self.access_token = None
        self.token_expires_at = None
        self.app = app
        self.auth_flow_in_progress = False
        self._client = httpx.AsyncClient(
            base_url=settings.base_url,
            timeout=30.0,
        )

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def setup_auth_routes(self):
        """Set up authentication routes if app is available."""
        if not self.app:
            logger.warning("No FastAPI app provided, skipping auth routes setup")
            return

        from strava_mcp.auth import StravaAuthenticator
        
        # Check if we have a FastAPI app or a FastMCP server
        fastapi_app = None
        
        # If it's a FastAPI app, use it directly
        if hasattr(self.app, "add_api_route"):
            fastapi_app = self.app
        # If it's a FastMCP server, try to get its FastAPI app
        elif hasattr(self.app, "_app"):
            fastapi_app = self.app._app
        
        if not fastapi_app:
            logger.warning("Could not get FastAPI app from the provided object, auth flow will not be available")
            return
            
        # Create authenticator and set up routes
        try:
            authenticator = StravaAuthenticator(
                self.settings.client_id,
                self.settings.client_secret,
                fastapi_app
            )
            authenticator.setup_routes(fastapi_app)
            
            # Store authenticator for later use
            self._authenticator = authenticator
            logger.info("Successfully set up Strava auth routes")
        except Exception as e:
            logger.error(f"Error setting up auth routes: {e}")
            return

    async def start_auth_flow(self) -> str:
        """Start the auth flow to get a refresh token.

        Returns:
            The refresh token

        Raises:
            Exception: If the auth flow fails or is not available
        """
        if not self.app:
            raise Exception(
                "No FastAPI app available for auth flow. "
                "Please set STRAVA_REFRESH_TOKEN manually in your environment variables."
            )
            
        authenticator = getattr(self, '_authenticator', None)
        if not authenticator:
            raise Exception(
                "Auth routes not set up or setup failed. "
                "Please set STRAVA_REFRESH_TOKEN manually in your environment variables."
            )
        
        if self.auth_flow_in_progress:
            raise Exception("Auth flow already in progress")
        
        self.auth_flow_in_progress = True
        try:
            # Display instructions to the user and open browser
            auth_url = self._authenticator.get_authorization_url()
            logger.info(
                f"\nNo refresh token available. Opening browser for authorization. "
                f"If browser doesn't open, please visit this URL manually: {auth_url}"
            )
            
            # Get the refresh token and open browser automatically
            refresh_token = await self._authenticator.get_refresh_token(open_browser=True)
            
            # Store it in settings
            self.settings.refresh_token = refresh_token
            
            logger.info("Successfully obtained refresh token")
            return refresh_token
        finally:
            self.auth_flow_in_progress = False

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

        # If we don't have a refresh token, try to get one through auth flow
        if not self.settings.refresh_token:
            logger.warning("No refresh token available, attempting to start auth flow")
            try:
                self.settings.refresh_token = await self.start_auth_flow()
            except Exception as e:
                error_msg = f"Failed to start auth flow: {e}"
                logger.error(error_msg)
                raise Exception(
                    "No refresh token available and could not start auth flow. "
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
            error_msg = (
                f"Strava API request failed: {response.status_code} - {response.text}"
            )
            logger.error(error_msg)

            try:
                error_data = response.json()
                error = ErrorResponse(**error_data)
                raise Exception(
                    f"Strava API error: {error.message} (code: {error.code})"
                )
            except Exception as err:
                msg = (
                    f"Strava API failed: {response.status_code} - {response.text[:50]}"
                )
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

    async def get_activity(
        self, activity_id: int, include_all_efforts: bool = False
    ) -> DetailedActivity:
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

        response = await self._request(
            "GET", f"/activities/{activity_id}", params=params
        )
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

