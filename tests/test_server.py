from unittest.mock import AsyncMock, MagicMock

import pytest

from strava_mcp.models import Activity, DetailedActivity, Leaderboard, SegmentEffort


class MockContext:
    """Mock MCP context for testing."""

    def __init__(self, service):
        self.request_context = MagicMock()
        self.request_context.lifespan_context = {"service": service}


@pytest.fixture
def mock_service():
    mock = AsyncMock()
    mock.get_activities = AsyncMock()
    mock.get_activity = AsyncMock()
    mock.get_activity_segments = AsyncMock()
    mock.get_segment_leaderboard = AsyncMock()
    return mock


@pytest.fixture
def mock_ctx(mock_service):
    return MockContext(mock_service)


@pytest.mark.asyncio
async def test_get_user_activities(mock_ctx, mock_service):
    # Setup mock data
    mock_activity = Activity(
        id=1234567890,
        name="Morning Run",
        distance=5000,
        moving_time=1200,
        elapsed_time=1300,
        total_elevation_gain=50,
        type="Run",
        sport_type="Run",
        start_date="2023-01-01T10:00:00Z",
        start_date_local="2023-01-01T10:00:00Z",
        timezone="Europe/London",
        achievement_count=2,
        kudos_count=5,
        comment_count=0,
        athlete_count=1,
        photo_count=0,
        trainer=False,
        commute=False,
        manual=False,
        private=False,
        flagged=False,
        average_speed=4.167,
        max_speed=5.3,
        has_heartrate=True,
        average_heartrate=140,
        max_heartrate=160,
    )
    mock_service.get_activities.return_value = [mock_activity]

    # Test tool
    from strava_mcp.server import get_user_activities

    result = await get_user_activities(mock_ctx)

    # Verify service call
    mock_service.get_activities.assert_called_once_with(None, None, 1, 30)

    # Verify result
    assert len(result) == 1
    assert result[0]["id"] == mock_activity.id
    assert result[0]["name"] == mock_activity.name


@pytest.mark.asyncio
async def test_get_activity(mock_ctx, mock_service):
    # Setup mock data
    mock_activity = DetailedActivity(
        id=1234567890,
        name="Morning Run",
        distance=5000,
        moving_time=1200,
        elapsed_time=1300,
        total_elevation_gain=50,
        type="Run",
        sport_type="Run",
        start_date="2023-01-01T10:00:00Z",
        start_date_local="2023-01-01T10:00:00Z",
        timezone="Europe/London",
        achievement_count=2,
        kudos_count=5,
        comment_count=0,
        athlete_count=1,
        photo_count=0,
        trainer=False,
        commute=False,
        manual=False,
        private=False,
        flagged=False,
        average_speed=4.167,
        max_speed=5.3,
        has_heartrate=True,
        average_heartrate=140,
        max_heartrate=160,
        athlete={"id": 123},
        description="Test description",
    )
    mock_service.get_activity.return_value = mock_activity

    # Test tool
    from strava_mcp.server import get_activity

    result = await get_activity(mock_ctx, 1234567890)

    # Verify service call
    mock_service.get_activity.assert_called_once_with(1234567890, False)

    # Verify result
    assert result["id"] == mock_activity.id
    assert result["name"] == mock_activity.name
    assert result["description"] == mock_activity.description


@pytest.mark.asyncio
async def test_get_activity_segments(mock_ctx, mock_service):
    # Setup mock data
    mock_segment = SegmentEffort(
        id=67890,
        activity_id=1234567890,
        segment_id=12345,
        name="Test Segment",
        elapsed_time=180,
        moving_time=180,
        start_date="2023-01-01T10:05:00Z",
        start_date_local="2023-01-01T10:05:00Z",
        distance=1000,
        athlete={"id": 123},
        segment={
            "id": 12345,
            "name": "Test Segment",
            "activity_type": "Run",
            "distance": 1000,
            "average_grade": 5.0,
            "maximum_grade": 10.0,
            "elevation_high": 200,
            "elevation_low": 150,
            "total_elevation_gain": 50,
            "start_latlng": [51.5, -0.1],
            "end_latlng": [51.5, -0.2],
            "climb_category": 0,
            "private": False,
            "starred": False,
        },
    )
    mock_service.get_activity_segments.return_value = [mock_segment]

    # Test tool
    from strava_mcp.server import get_activity_segments

    result = await get_activity_segments(mock_ctx, 1234567890)

    # Verify service call
    mock_service.get_activity_segments.assert_called_once_with(1234567890)

    # Verify result
    assert len(result) == 1
    assert result[0]["id"] == mock_segment.id
    assert result[0]["name"] == mock_segment.name


@pytest.mark.asyncio
async def test_get_segment_leaderboard(mock_ctx, mock_service):
    # Setup mock data
    mock_leaderboard = Leaderboard(
        entry_count=100,
        effort_count=200,
        kom_type="kom",
        entries=[
            {
                "athlete_name": "John Doe",
                "athlete_id": 123,
                "athlete_gender": "M",
                "average_hr": 160,
                "average_watts": 250,
                "distance": 1000,
                "elapsed_time": 180,
                "moving_time": 180,
                "start_date": "2023-01-01T10:00:00Z",
                "start_date_local": "2023-01-01T10:00:00Z",
                "activity_id": 12345,
                "effort_id": 67890,
                "rank": 1,
            }
        ],
    )
    mock_service.get_segment_leaderboard.return_value = mock_leaderboard

    # Test tool
    from strava_mcp.server import get_segment_leaderboard

    result = await get_segment_leaderboard(mock_ctx, 12345)

    # Verify service call
    mock_service.get_segment_leaderboard.assert_called_once_with(
        12345, None, None, None, None, None, None, None, 1, 30
    )

    # Verify result
    assert result["entry_count"] == mock_leaderboard.entry_count
    assert result["effort_count"] == mock_leaderboard.effort_count
    assert result["kom_type"] == mock_leaderboard.kom_type
    assert len(result["entries"]) == 1
