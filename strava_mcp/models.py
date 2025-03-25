from datetime import datetime

from pydantic import BaseModel, Field


class Activity(BaseModel):
    """Represents a Strava activity."""

    id: int = Field(..., description="The unique identifier of the activity")
    name: str = Field(..., description="The name of the activity")
    distance: float = Field(..., description="The distance in meters")
    moving_time: int = Field(..., description="Moving time in seconds")
    elapsed_time: int = Field(..., description="Elapsed time in seconds")
    total_elevation_gain: float = Field(..., description="Total elevation gain in meters")
    type: str = Field(..., description="Type of activity")
    sport_type: str = Field(..., description="Type of sport")
    start_date: datetime = Field(..., description="Start date and time in UTC")
    start_date_local: datetime = Field(..., description="Start date and time in athlete's timezone")
    timezone: str = Field(..., description="The timezone of the activity")
    achievement_count: int = Field(..., description="The number of achievements")
    kudos_count: int = Field(..., description="The number of kudos")
    comment_count: int = Field(..., description="The number of comments")
    athlete_count: int = Field(..., description="The number of athletes")
    photo_count: int = Field(..., description="The number of photos")
    map: dict | None = Field(None, description="The map of the activity")
    trainer: bool = Field(..., description="Whether this activity was recorded on a training machine")
    commute: bool = Field(..., description="Whether this activity is a commute")
    manual: bool = Field(..., description="Whether this activity was created manually")
    private: bool = Field(..., description="Whether this activity is private")
    flagged: bool = Field(..., description="Whether this activity is flagged")
    workout_type: int | None = Field(None, description="The workout type")
    average_speed: float = Field(..., description="Average speed in meters per second")
    max_speed: float = Field(..., description="Maximum speed in meters per second")
    has_heartrate: bool = Field(..., description="Whether the activity has heartrate data")
    average_heartrate: float | None = Field(None, description="Average heartrate during activity")
    max_heartrate: float | None = Field(None, description="Maximum heartrate during activity")
    elev_high: float | None = Field(None, description="The highest elevation")
    elev_low: float | None = Field(None, description="The lowest elevation")


class DetailedActivity(Activity):
    """Detailed version of a Strava activity."""

    description: str | None = Field(None, description="The description of the activity")
    athlete: dict = Field(..., description="The athlete who performed the activity")
    calories: float | None = Field(None, description="Calories burned during activity")
    segment_efforts: list[dict] | None = Field(None, description="List of segment efforts")
    splits_metric: list[dict] | None = Field(None, description="Splits in metric units")
    splits_standard: list[dict] | None = Field(None, description="Splits in standard units")
    best_efforts: list[dict] | None = Field(None, description="List of best efforts")
    photos: dict | None = Field(None, description="Photos associated with activity")
    gear: dict | None = Field(None, description="Gear used during activity")
    device_name: str | None = Field(None, description="Name of device used to record activity")


class Segment(BaseModel):
    """Represents a Strava segment."""

    id: int = Field(..., description="The unique identifier of the segment")
    name: str = Field(..., description="The name of the segment")
    activity_type: str = Field(..., description="The activity type of the segment")
    distance: float = Field(..., description="The segment's distance in meters")
    average_grade: float = Field(..., description="The segment's average grade, in percents")
    maximum_grade: float = Field(..., description="The segments's maximum grade, in percents")
    elevation_high: float = Field(..., description="The segments's highest elevation, in meters")
    elevation_low: float = Field(..., description="The segments's lowest elevation, in meters")
    total_elevation_gain: float = Field(..., description="The segments's total elevation gain, in meters")
    start_latlng: list[float] = Field(..., description="Start coordinates [latitude, longitude]")
    end_latlng: list[float] = Field(..., description="End coordinates [latitude, longitude]")
    climb_category: int = Field(..., description="The category of the climb [0, 5]")
    city: str | None = Field(None, description="The city this segment is in")
    state: str | None = Field(None, description="The state this segment is in")
    country: str | None = Field(None, description="The country this segment is in")
    private: bool = Field(..., description="Whether this segment is private")
    starred: bool = Field(..., description="Whether this segment is starred by the authenticated athlete")


class SegmentEffort(BaseModel):
    """Represents a Strava segment effort."""

    id: int = Field(..., description="The unique identifier of the segment effort")
    activity_id: int = Field(..., description="The ID of the associated activity")
    segment_id: int = Field(..., description="The ID of the associated segment")
    name: str = Field(..., description="The name of the segment")
    elapsed_time: int = Field(..., description="The elapsed time in seconds")
    moving_time: int = Field(..., description="The moving time in seconds")
    start_date: datetime = Field(..., description="Start date and time in UTC")
    start_date_local: datetime = Field(..., description="Start date and time in athlete's timezone")
    distance: float = Field(..., description="The effort's distance in meters")
    average_watts: float | None = Field(None, description="Average wattage")
    device_watts: bool | None = Field(None, description="Whether power data comes from a power meter")
    average_heartrate: float | None = Field(None, description="Average heartrate")
    max_heartrate: float | None = Field(None, description="Maximum heartrate")
    pr_rank: int | None = Field(None, description="Personal record rank (1-3), 0 if not a PR")
    achievements: list[dict] | None = Field(None, description="List of achievements")
    athlete: dict = Field(..., description="The athlete who performed the effort")
    segment: Segment = Field(..., description="The segment")


class ErrorResponse(BaseModel):
    """Represents an error response from the Strava API."""

    message: str = Field(..., description="Error message")
    code: int = Field(..., description="Error code")
