import logging

from strava_mcp.api import StravaAPI
from strava_mcp.config import StravaSettings
from strava_mcp.models import Activity, DetailedActivity, Leaderboard, SegmentEffort

logger = logging.getLogger(__name__)


class StravaService:
    """Service for interacting with the Strava API."""

    def __init__(self, settings: StravaSettings):
        """Initialize the Strava service.

        Args:
            settings: Strava API settings
        """
        self.settings = settings
        self.api = StravaAPI(settings)

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
        try:
            logger.info(f"Getting leaderboard for segment {segment_id}")
            leaderboard = await self.api.get_segment_leaderboard(
                segment_id,
                gender,
                age_group,
                weight_class,
                following,
                club_id,
                date_range,
                context_entries,
                page,
                per_page,
            )
            logger.info(f"Retrieved leaderboard with {leaderboard.entry_count} entries")
            return leaderboard
        except Exception as e:
            logger.error(
                f"Error getting leaderboard for segment {segment_id}: {str(e)}"
            )
            raise
