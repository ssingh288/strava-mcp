import logging
import json
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from mcp.server.fastmcp import FastMCP, Context

from strava_mcp.config import StravaSettings
from strava_mcp.service import StravaService
from strava_mcp.models import Activity, DetailedActivity, SegmentEffort, Leaderboard


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """Set up and tear down the Strava service for the MCP server.
    
    Args:
        server: The FastMCP server instance
    
    Yields:
        The lifespan context containing the Strava service
    """
    # Load settings from environment variables
    try:
        settings = StravaSettings()
        logger.info("Loaded Strava API settings")
    except Exception as e:
        logger.error(f"Failed to load Strava API settings: {str(e)}")
        raise
    
    # Initialize the Strava service
    service = StravaService(settings)
    logger.info("Initialized Strava service")
    
    try:
        yield {"service": service}
    finally:
        # Clean up resources
        await service.close()
        logger.info("Closed Strava service")


# Create the MCP server
mcp = FastMCP(
    "Strava",
    description="MCP server for interacting with the Strava API",
    lifespan=lifespan,
)


@mcp.tool()
async def get_user_activities(
    ctx: Context,
    before: Optional[int] = None,
    after: Optional[int] = None,
    page: int = 1,
    per_page: int = 30,
) -> List[Dict]:
    """Get the authenticated user's activities.
    
    Args:
        ctx: The MCP request context
        before: An epoch timestamp to use for filtering activities that have taken place before a certain time
        after: An epoch timestamp to use for filtering activities that have taken place after a certain time
        page: Page number
        per_page: Number of items per page
    
    Returns:
        List of activities
    """
    service = ctx.request_context.lifespan_context["service"]
    
    try:
        activities = await service.get_activities(before, after, page, per_page)
        return [activity.model_dump() for activity in activities]
    except Exception as e:
        logger.error(f"Error in get_user_activities tool: {str(e)}")
        raise


@mcp.tool()
async def get_activity(
    ctx: Context,
    activity_id: int,
    include_all_efforts: bool = False,
) -> Dict:
    """Get details of a specific activity.
    
    Args:
        ctx: The MCP request context
        activity_id: The ID of the activity
        include_all_efforts: Whether to include all segment efforts
    
    Returns:
        The activity details
    """
    service = ctx.request_context.lifespan_context["service"]
    
    try:
        activity = await service.get_activity(activity_id, include_all_efforts)
        return activity.model_dump()
    except Exception as e:
        logger.error(f"Error in get_activity tool: {str(e)}")
        raise


@mcp.tool()
async def get_activity_segments(
    ctx: Context,
    activity_id: int,
) -> List[Dict]:
    """Get the segments of a specific activity.
    
    Args:
        ctx: The MCP request context
        activity_id: The ID of the activity
    
    Returns:
        List of segment efforts for the activity
    """
    service = ctx.request_context.lifespan_context["service"]
    
    try:
        segments = await service.get_activity_segments(activity_id)
        return [segment.model_dump() for segment in segments]
    except Exception as e:
        logger.error(f"Error in get_activity_segments tool: {str(e)}")
        raise


@mcp.tool()
async def get_segment_leaderboard(
    ctx: Context,
    segment_id: int,
    gender: Optional[str] = None,
    age_group: Optional[str] = None,
    weight_class: Optional[str] = None,
    following: Optional[bool] = None,
    club_id: Optional[int] = None,
    date_range: Optional[str] = None,
    context_entries: Optional[int] = None,
    page: int = 1,
    per_page: int = 30,
) -> Dict:
    """Get the leaderboard for a given segment.
    
    Args:
        ctx: The MCP request context
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
    service = ctx.request_context.lifespan_context["service"]
    
    try:
        leaderboard = await service.get_segment_leaderboard(
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
        return leaderboard.model_dump()
    except Exception as e:
        logger.error(f"Error in get_segment_leaderboard tool: {str(e)}")
        raise