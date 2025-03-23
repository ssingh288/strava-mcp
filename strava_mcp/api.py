import logging
from datetime import datetime

import httpx
from httpx import Response

from strava_mcp.config import StravaSettings
from strava_mcp.models import (
    Activity,
    DetailedActivity,
    ErrorResponse,
    Leaderboard,
    SegmentEffort,
)

logger = logging.getLogger(__name__)


class StravaAPI:
    """Client for the Strava API."""

    def __init__(self, settings: StravaSettings):
        """Initialize the Strava API client.

        Args:
            settings: Strava API settings
        """
        self.settings = settings
        self.access_token = None
        self.token_expires_at = None
        self._client = httpx.AsyncClient(
            base_url=settings.base_url,
            timeout=30.0,
        )

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def _ensure_token(self) -> str:
        """Ensure we have a valid access token.

        Returns:
            The access token
        """
        now = datetime.now().timestamp()

        # If token is still valid, return it
        if self.access_token and self.token_expires_at and now < self.token_expires_at:
            return self.access_token

        # Otherwise, refresh the token
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

            logger.info("Successfully refreshed access token")
            # TODO remove this, do not log secrets
            # logger.info(f"Token expires at: {self.token_expires_at}")
            # logger.info(f"Token value: {self.access_token}")
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

    async def get_segment_leaderboard(
        self,
        segment_id: int,
        gender: str | None = None,
        age_group: int | None = None,
        weight_class: int | None = None,
        following: bool | None = None,
        club_id: int | None = None,
        date_range: int | None = None,
        context_entries: int | None = None,
        page: int = 1,
        per_page: int = 30,
    ) -> Leaderboard:
        """Get the leaderboard for a given segment.

        Args:
            segment_id: The ID of the segment
            gender: Filter by gender ('M' or 'F')
            age_group: Filter by age group
            weight_class: Filter by weight class
            following: Filter by friends of the authenticated athlete
            club_id: Filter by club
            date_range: Filter by date range
            context_entries: Number of context entries
            page: Page number
            per_page: Number of items per page

        Returns:
            The segment leaderboard
        """
        params = {"page": page, "per_page": per_page}

        if gender:
            # Convert gender string to integer code
            gender_code = 0  # Default
            if gender.upper() == "M":
                gender_code = 1
            elif gender.upper() == "F":
                gender_code = 2
            params["gender"] = gender_code
        if age_group:
            params["age_group"] = int(age_group)
        if weight_class:
            params["weight_class"] = int(weight_class)
        if following is not None:
            params["following"] = 1 if following else 0
        if club_id:
            params["club_id"] = club_id
        if date_range:
            params["date_range"] = int(date_range)
        if context_entries:
            params["context_entries"] = context_entries

        response = await self._request(
            "GET", f"/segments/{segment_id}/leaderboard", params=params
        )
        data = response.json()

        return Leaderboard(**data)
