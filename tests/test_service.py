import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from strava_mcp.config import StravaSettings
from strava_mcp.service import StravaService
from strava_mcp.models import Activity, DetailedActivity, SegmentEffort, Leaderboard


@pytest.fixture
def settings():
    return StravaSettings(
        client_id="test_client_id",
        client_secret="test_client_secret",
        refresh_token="test_refresh_token",
    )


@pytest.fixture
def mock_api():
    mock = AsyncMock()
    mock.get_activities = AsyncMock()
    mock.get_activity = AsyncMock()
    mock.get_activity_segments = AsyncMock()
    mock.get_segment_leaderboard = AsyncMock()
    return mock


@pytest.fixture
def service(settings, mock_api):
    with patch("strava_mcp.service.StravaAPI", return_value=mock_api):
        service = StravaService(settings)
        yield service


@pytest.mark.asyncio
async def test_get_activities(service, mock_api):
    # Setup mocked data
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
    mock_api.get_activities.return_value = [mock_activity]
    
    # Test get_activities
    activities = await service.get_activities()
    
    # Verify API call
    mock_api.get_activities.assert_called_once_with(None, None, 1, 30)
    
    # Verify response
    assert len(activities) == 1
    assert activities[0] == mock_activity


@pytest.mark.asyncio
async def test_get_activity(service, mock_api):
    # Setup mocked data
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
    mock_api.get_activity.return_value = mock_activity
    
    # Test get_activity
    activity = await service.get_activity(1234567890)
    
    # Verify API call
    mock_api.get_activity.assert_called_once_with(1234567890, False)
    
    # Verify response
    assert activity == mock_activity


@pytest.mark.asyncio
async def test_get_activity_segments(service, mock_api):
    # Setup mocked data
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
    mock_api.get_activity_segments.return_value = [mock_segment]
    
    # Test get_activity_segments
    segments = await service.get_activity_segments(1234567890)
    
    # Verify API call
    mock_api.get_activity_segments.assert_called_once_with(1234567890)
    
    # Verify response
    assert len(segments) == 1
    assert segments[0] == mock_segment


@pytest.mark.asyncio
async def test_get_segment_leaderboard(service, mock_api):
    # Setup mocked data
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
    mock_api.get_segment_leaderboard.return_value = mock_leaderboard
    
    # Test get_segment_leaderboard
    leaderboard = await service.get_segment_leaderboard(12345)
    
    # Verify API call
    mock_api.get_segment_leaderboard.assert_called_once_with(
        12345, None, None, None, None, None, None, None, 1, 30
    )
    
    # Verify response
    assert leaderboard == mock_leaderboard