import logging

from fastapi import FastAPI

from strava_mcp.api import StravaAPI
from strava_mcp.config import StravaSettings
from strava_mcp.models import Activity, DetailedActivity, SegmentEffort

logger = logging.getLogger(__name__)


class StravaService:
    """Service for interacting with the Strava API."""

    def __init__(self, settings: StravaSettings, app: FastAPI | None = None):
        """Initialize the Strava service.

        Args:
            settings: Strava API settings
            app: FastAPI app for auth routes (optional)
        """
        self.settings = settings
        self.api = StravaAPI(settings, app)

    async def initialize(self):
        """Initialize the service."""
        # Log info about OAuth flow if no refresh token
        if not self.settings.refresh_token:
            logger.info(
                "No STRAVA_REFRESH_TOKEN found in environment. "
                "The standalone OAuth flow will be triggered automatically when needed."
            )

    async def close(self):
        """Close the API client."""
        await self.api.close()

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
        try:
            logger.info("Getting activities for authenticated athlete")
            activities = await self.api.get_activities(before, after, page, per_page)
            logger.info(f"Retrieved {len(activities)} activities")
            return activities
        except Exception as e:
            logger.error(f"Error getting activities: {str(e)}")
            raise

    async def get_activity(self, activity_id: int, include_all_efforts: bool = False) -> DetailedActivity:
        """Get a specific activity.

        Args:
            activity_id: The ID of the activity
            include_all_efforts: Whether to include all segment efforts

        Returns:
            The activity details
        """
        try:
            logger.info(f"Getting activity {activity_id}")
            activity = await self.api.get_activity(activity_id, include_all_efforts)
            logger.info(f"Retrieved activity: {activity.name}")
            return activity
        except Exception as e:
            logger.error(f"Error getting activity {activity_id}: {str(e)}")
            raise

    async def get_activity_segments(self, activity_id: int) -> list[SegmentEffort]:
        """Get segments from a specific activity.

        Args:
            activity_id: The ID of the activity

        Returns:
            List of segment efforts for the activity
        """
        try:
            logger.info(f"Getting segments for activity {activity_id}")
            segments = await self.api.get_activity_segments(activity_id)
            logger.info(f"Retrieved {len(segments)} segments")
            return segments
        except Exception as e:
            logger.error(f"Error getting segments for activity {activity_id}: {str(e)}")
            raise
