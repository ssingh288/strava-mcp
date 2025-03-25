"""Tests for the Strava models."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from strava_mcp.models import Activity, DetailedActivity, ErrorResponse, Segment, SegmentEffort


@pytest.fixture
def activity_data():
    """Fixture with valid activity data."""
    return {
        "id": 1234567890,
        "name": "Morning Run",
        "distance": 5000.0,
        "moving_time": 1200,
        "elapsed_time": 1300,
        "total_elevation_gain": 50.0,
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
        "average_heartrate": 140.0,
        "max_heartrate": 160.0,
    }


@pytest.fixture
def detailed_activity_data(activity_data):
    """Fixture with valid detailed activity data."""
    return {
        **activity_data,
        "description": "Test description",
        "athlete": {"id": 123},
        "calories": 500.0,
    }


@pytest.fixture
def segment_data():
    """Fixture with valid segment data."""
    return {
        "id": 12345,
        "name": "Test Segment",
        "activity_type": "Run",
        "distance": 1000.0,
        "average_grade": 5.0,
        "maximum_grade": 10.0,
        "elevation_high": 200.0,
        "elevation_low": 150.0,
        "total_elevation_gain": 50.0,
        "start_latlng": [51.5, -0.1],
        "end_latlng": [51.5, -0.2],
        "climb_category": 0,
        "private": False,
        "starred": False,
    }


@pytest.fixture
def segment_effort_data(segment_data):
    """Fixture with valid segment effort data."""
    return {
        "id": 67890,
        "activity_id": 1234567890,
        "segment_id": 12345,
        "name": "Test Segment",
        "elapsed_time": 180,
        "moving_time": 180,
        "start_date": "2023-01-01T10:05:00Z",
        "start_date_local": "2023-01-01T10:05:00Z",
        "distance": 1000.0,
        "athlete": {"id": 123},
        "segment": segment_data,
    }


def test_activity_model(activity_data):
    """Test the Activity model."""
    activity = Activity(**activity_data)

    assert activity.id == activity_data["id"]
    assert activity.name == activity_data["name"]
    assert activity.distance == activity_data["distance"]
    assert activity.start_date == datetime.fromisoformat(activity_data["start_date"].replace("Z", "+00:00"))
    assert activity.start_date_local == datetime.fromisoformat(activity_data["start_date_local"].replace("Z", "+00:00"))
    assert activity.average_heartrate == activity_data["average_heartrate"]
    assert activity.max_heartrate == activity_data["max_heartrate"]


def test_activity_model_optional_fields(activity_data):
    """Test the Activity model with optional fields."""
    # Remove some optional fields
    data = activity_data.copy()
    data.pop("average_heartrate")
    data.pop("max_heartrate")

    activity = Activity(**data)

    assert activity.average_heartrate is None
    assert activity.max_heartrate is None


def test_activity_model_missing_required_fields(activity_data):
    """Test the Activity model with missing required fields."""
    data = activity_data.copy()
    data.pop("id")  # Remove a required field

    with pytest.raises(ValidationError):
        Activity(**data)


def test_detailed_activity_model(detailed_activity_data):
    """Test the DetailedActivity model."""
    activity = DetailedActivity(**detailed_activity_data)

    assert activity.id == detailed_activity_data["id"]
    assert activity.name == detailed_activity_data["name"]
    assert activity.description == detailed_activity_data["description"]
    assert activity.athlete == detailed_activity_data["athlete"]
    assert activity.calories == detailed_activity_data["calories"]


def test_detailed_activity_optional_fields(detailed_activity_data):
    """Test the DetailedActivity model with optional fields."""
    data = detailed_activity_data.copy()
    data.pop("description")
    data.pop("calories")

    activity = DetailedActivity(**data)

    assert activity.description is None
    assert activity.calories is None


def test_segment_model(segment_data):
    """Test the Segment model."""
    segment = Segment(**segment_data)

    assert segment.id == segment_data["id"]
    assert segment.name == segment_data["name"]
    assert segment.activity_type == segment_data["activity_type"]
    assert segment.distance == segment_data["distance"]
    assert segment.start_latlng == segment_data["start_latlng"]
    assert segment.end_latlng == segment_data["end_latlng"]


def test_segment_optional_fields(segment_data):
    """Test the Segment model with optional fields."""
    # Add some optional fields
    data = segment_data.copy()
    data["city"] = "London"
    data["state"] = "Greater London"
    data["country"] = "United Kingdom"

    segment = Segment(**data)

    assert segment.city == "London"
    assert segment.state == "Greater London"
    assert segment.country == "United Kingdom"


def test_segment_missing_fields(segment_data):
    """Test the Segment model with missing required fields."""
    data = segment_data.copy()
    data.pop("id")  # Remove a required field

    with pytest.raises(ValidationError):
        Segment(**data)


def test_segment_effort_model(segment_effort_data):
    """Test the SegmentEffort model."""
    effort = SegmentEffort(**segment_effort_data)

    assert effort.id == segment_effort_data["id"]
    assert effort.activity_id == segment_effort_data["activity_id"]
    assert effort.segment_id == segment_effort_data["segment_id"]
    assert effort.name == segment_effort_data["name"]
    assert effort.elapsed_time == segment_effort_data["elapsed_time"]
    assert effort.moving_time == segment_effort_data["moving_time"]
    assert effort.start_date == datetime.fromisoformat(segment_effort_data["start_date"].replace("Z", "+00:00"))
    assert effort.start_date_local == datetime.fromisoformat(
        segment_effort_data["start_date_local"].replace("Z", "+00:00")
    )
    assert effort.distance == segment_effort_data["distance"]
    assert effort.athlete == segment_effort_data["athlete"]

    # Test nested segment object
    assert effort.segment.id == segment_effort_data["segment"]["id"]
    assert effort.segment.name == segment_effort_data["segment"]["name"]


def test_segment_effort_optional_fields(segment_effort_data):
    """Test the SegmentEffort model with optional fields."""
    # Add some optional fields
    data = segment_effort_data.copy()
    data["average_watts"] = 200.0
    data["device_watts"] = True
    data["average_heartrate"] = 150.0
    data["max_heartrate"] = 170.0
    data["pr_rank"] = 1
    data["achievements"] = [{"type": "overall", "rank": 1}]

    effort = SegmentEffort(**data)

    assert effort.average_watts == 200.0
    assert effort.device_watts is True
    assert effort.average_heartrate == 150.0
    assert effort.max_heartrate == 170.0
    assert effort.pr_rank == 1
    assert effort.achievements == [{"type": "overall", "rank": 1}]


def test_segment_effort_missing_fields(segment_effort_data):
    """Test the SegmentEffort model with missing required fields."""
    data = segment_effort_data.copy()
    data.pop("segment")  # Remove a required field

    with pytest.raises(ValidationError):
        SegmentEffort(**data)


def test_error_response():
    """Test the ErrorResponse model."""
    data = {"message": "Resource not found", "code": 404}

    error = ErrorResponse(**data)

    assert error.message == "Resource not found"
    assert error.code == 404
