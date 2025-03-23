from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from strava_mcp.api import StravaAPI
from strava_mcp.config import StravaSettings
from strava_mcp.models import Activity, DetailedActivity


@pytest.fixture
def settings():
    return StravaSettings(
        client_id="test_client_id",
        client_secret="test_client_secret",
        refresh_token="test_refresh_token",
        base_url="https://www.strava.com/api/v3",
    )


@pytest.fixture
def mock_response():
    mock = MagicMock()
    mock.is_success = True
    mock.json = MagicMock(return_value={})
    mock.status_code = 200
    return mock


@pytest.fixture
def api(settings):
    api = StravaAPI(settings)
    api._client = AsyncMock()
    api.access_token = "test_access_token"
    api.token_expires_at = datetime.now().timestamp() + 3600
    return api


@pytest.mark.asyncio
async def test_ensure_token_valid(api):
    # Token is already valid
    token = await api._ensure_token()
    assert token == "test_access_token"


@pytest.mark.asyncio
async def test_ensure_token_refresh(settings):
    with patch("httpx.AsyncClient") as mock_client:
        # Setup mock for token refresh
        mock_instance = mock_client.return_value.__aenter__.return_value
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new_access_token",
            "expires_at": datetime.now().timestamp() + 3600,
        }
        mock_instance.post.return_value = mock_response

        # Create API with expired token
        api = StravaAPI(settings)
        api.access_token = "old_access_token"
        api.token_expires_at = datetime.now().timestamp() - 3600

        # Test token refresh
        token = await api._ensure_token()
        assert token == "new_access_token"

        # Verify correct API call was made
        mock_instance.post.assert_called_once()
        args, kwargs = mock_instance.post.call_args
        assert args[0] == "https://www.strava.com/oauth/token"
        assert kwargs["json"]["client_id"] == "test_client_id"
        assert kwargs["json"]["client_secret"] == "test_client_secret"
        assert kwargs["json"]["refresh_token"] == "test_refresh_token"
        assert kwargs["json"]["grant_type"] == "refresh_token"


@pytest.mark.asyncio
async def test_get_activities(api, mock_response):
    # Setup mock response
    activity_data = {
        "id": 1234567890,
        "name": "Morning Run",
        "distance": 5000,
        "moving_time": 1200,
        "elapsed_time": 1300,
        "total_elevation_gain": 50,
        "type": "Run",
        "sport_type": "Run",
        "start_date": "2023-01-01T10:00:00Z",
        "start_date_local": "2023-01-01T10:00:00Z",
        "timezone": "Europe/London",
        "achievement_count": 2,
        "kudos_count": 5,
        "comment_count": 0,
        "athlete_count": 1,
        "photo_count": 0,
        "trainer": False,
        "commute": False,
        "manual": False,
        "private": False,
        "flagged": False,
        "average_speed": 4.167,
        "max_speed": 5.3,
        "has_heartrate": True,
        "average_heartrate": 140,
        "max_heartrate": 160,
    }
    mock_response.json.return_value = [activity_data]
    api._client.request.return_value = mock_response

    # Test get_activities
    activities = await api.get_activities()

    # Verify request
    api._client.request.assert_called_once()
    args, kwargs = api._client.request.call_args
    assert args[0] == "GET"
    assert args[1] == "/athlete/activities"
    assert kwargs["params"] == {"page": 1, "per_page": 30}

    # Verify response
    assert len(activities) == 1
    assert isinstance(activities[0], Activity)
    assert activities[0].id == activity_data["id"]
    assert activities[0].name == activity_data["name"]


@pytest.mark.asyncio
async def test_get_activity(api, mock_response):
    # Setup mock response
    activity_data = {
        "id": 1234567890,
        "name": "Morning Run",
        "distance": 5000,
        "moving_time": 1200,
        "elapsed_time": 1300,
        "total_elevation_gain": 50,
        "type": "Run",
        "sport_type": "Run",
        "start_date": "2023-01-01T10:00:00Z",
        "start_date_local": "2023-01-01T10:00:00Z",
        "timezone": "Europe/London",
        "achievement_count": 2,
        "kudos_count": 5,
        "comment_count": 0,
        "athlete_count": 1,
        "photo_count": 0,
        "trainer": False,
        "commute": False,
        "manual": False,
        "private": False,
        "flagged": False,
        "average_speed": 4.167,
        "max_speed": 5.3,
        "has_heartrate": True,
        "average_heartrate": 140,
        "max_heartrate": 160,
        "athlete": {"id": 123},
        "description": "Test description",
    }
    mock_response.json.return_value = activity_data
    api._client.request.return_value = mock_response

    # Test get_activity
    activity = await api.get_activity(1234567890)

    # Verify request
    api._client.request.assert_called_once()
    args, kwargs = api._client.request.call_args
    assert args[0] == "GET"
    assert args[1] == "/activities/1234567890"

    # Verify response
    assert isinstance(activity, DetailedActivity)
    assert activity.id == activity_data["id"]
    assert activity.name == activity_data["name"]
    assert activity.description == activity_data["description"]
