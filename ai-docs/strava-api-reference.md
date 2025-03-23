# Strava API v3

## Activities

### Create an Activity (createActivity)

Creates a manual activity for an athlete, requires activity:write scope.

```
POST /api/v3/activities
```

#### Body Parameters:

| Parameter | Type | Min | Max | Default | Description | Required |
| --- | --- | --- | --- | --- | --- | --- |
| name | string |  |  |  | The name of the activity | Yes |
| sport_type | string |  |  |  | The type of sport: Alpineski, BackcountrySki, Canoeing, Crossfit, EBikeRide, Elliptical, EMountainBikeRide, Golf, GravelRide, Handcycle, Hike, IceSkate, InlineSkate, Kayaking, Kitesurf, MountainBikeRide, NordicSki, Pickleball, Pilates, Racquetball, Ride, RockClimbing, RollerSki, Rowing, Run, Sail, Skateboard, Snowboard, Snowshoe, Soccer, Squash, StairStepper, StandUpPaddling, Surfing, Swim, TableTennis, Tennis, TrailRun, Velomobile, VirtualRide, VirtualRow, VirtualRun, Walk, WeightTraining, Wheelchair, Windsurf, Workout, Yoga | No |
| start_date_local | datetime |  |  |  | ISO 8601 formatted date time | Yes |
| elapsed_time | int | 0 |  |  | In seconds | Yes |
| type | string |  |  |  | The type of activity: Run, Ride, Swim, Workout, Hike, Walk, AlpineSki, BackcountrySki, Canoeing, Crossfit, EBikeRide, Elliptical, Handcycle, IceSkate, InlineSkate, Kayaking, Kitesurf, NordicSki, RockClimbing, RollerSki, Rowing, Snowboard, Snowshoe, StairStepper, StandUpPaddling, Surfing, Velomobile, VirtualRide, VirtualRun, WeightTraining, Windsurf, Workout, Yoga | No |
| description | string |  |  |  | The description of the activity | No |
| distance | float | 0 |  |  | In meters | No |
| trainer | int | 0 | 1 | 0 | Set to 1 to mark as a trainer activity | No |
| commute | int | 0 | 1 | 0 | Set to 1 to mark as commute | No |

### Get Activity (getActivityById)

Returns the given activity that is owned by the authenticated athlete.

```
GET /api/v3/activities/{id}
```

#### Parameters

| Parameter | Type | Description | Required |
| --- | --- | --- | --- |
| id | int64 | The identifier of the activity | Yes |
| include_all_efforts | Boolean | To include all segments efforts | No |

### Get Comments (getCommentsByActivityId)

Returns the comments on the given activity.

```
GET /api/v3/activities/{id}/comments
```

#### Parameters

| Parameter | Type | Description | Required |
| --- | --- | --- | --- |
| id | int64 | The identifier of the activity | Yes |
| page | int32 | Page number, defaults to 1 | No |
| per_page | int32 | Number of items per page, defaults to 30 | No |

### Get Kudoers (getKudoersByActivityId)

Returns the athletes who kudoed the given activity.

```
GET /api/v3/activities/{id}/kudos
```

#### Parameters

| Parameter | Type | Description | Required |
| --- | --- | --- | --- |
| id | int64 | The identifier of the activity | Yes |
| page | int32 | Page number, defaults to 1 | No |
| per_page | int32 | Number of items per page, defaults to 30 | No |

### Get Laps (getLapsByActivityId)

Returns the laps of an activity.

```
GET /api/v3/activities/{id}/laps
```

#### Parameters

| Parameter | Type | Description | Required |
| --- | --- | --- | --- |
| id | int64 | The identifier of the activity | Yes |

### List Activity Photos (getLoggedInAthleteActivities)

Returns the list of photos associated with an activity.

```
GET /api/v3/activities/{id}/photos
```

#### Parameters

| Parameter | Type | Description | Required |
| --- | --- | --- | --- |
| id | int64 | The identifier of the activity | Yes |
| size | int32 | The size of each photo, defaults to 1000 | No |
| photo_sources | String | Must be "true" to include source URLs of photos | No |

### List Athlete Activities (getLoggedInAthleteActivities)

Returns the activities of an athlete for a specific identifier.

```
GET /api/v3/athlete/activities
```

#### Parameters

| Parameter | Type | Description | Required |
| --- | --- | --- | --- |
| before | int32 | An epoch timestamp to use for filtering activities that have taken place before a certain time | No |
| after | int32 | An epoch timestamp to use for filtering activities that have taken place after a certain time | No |
| page | int32 | Page number, defaults to 1 | No |
| per_page | int32 | Number of items per page, defaults to 30 | No |

### Get Activity Zones (getZonesByActivityId)

Returns the zones of an activity.

```
GET /api/v3/activities/{id}/zones
```

#### Parameters

| Parameter | Type | Description | Required |
| --- | --- | --- | --- |
| id | int64 | The identifier of the activity | Yes |

### Update Activity (updateActivityById)

Updates the given activity.

```
PUT /api/v3/activities/{id}
```

#### Parameters

| Parameter | Type | Description | Required |
| --- | --- | --- | --- |
| id | int64 | The identifier of the activity | Yes |
| body | body | The updates to activity | No |

## Athletes

### Get Authenticated Athlete (getLoggedInAthlete)

Returns the currently authenticated athlete.

```
GET /api/v3/athlete
```

### Get Zones (getLoggedInAthleteZones)

Returns the the authenticated athlete's heart rate and power zones.

```
GET /api/v3/athlete/zones
```

### Get Athlete Stats (getStats)

Returns the activity stats of an athlete.

```
GET /api/v3/athletes/{id}/stats
```

#### Parameters

| Parameter | Type | Description | Required |
| --- | --- | --- | --- |
| id | int64 | The identifier of the athlete | Yes |

## Clubs

### List Club Activities (getClubActivitiesById)

Returns a list of activities for members of a club.

```
GET /api/v3/clubs/{id}/activities
```

#### Parameters

| Parameter | Type | Description | Required |
| --- | --- | --- | --- |
| id | int64 | The identifier of the club | Yes |
| page | int32 | Page number, defaults to 1 | No |
| per_page | int32 | Number of items per page, defaults to 30 | No |

### Get Club (getClubById)

Returns a given club using its identifier.

```
GET /api/v3/clubs/{id}
```

#### Parameters

| Parameter | Type | Description | Required |
| --- | --- | --- | --- |
| id | int64 | The identifier of the club | Yes |

### List Club Administrators (getClubAdminsById)

Returns a list of the administrators of a given club.

```
GET /api/v3/clubs/{id}/admins
```

#### Parameters

| Parameter | Type | Description | Required |
| --- | --- | --- | --- |
| id | int64 | The identifier of the club | Yes |
| page | int32 | Page number, defaults to 1 | No |
| per_page | int32 | Number of items per page, defaults to 30 | No |

### List Club Members (getClubMembersById)

Returns a list of the members of a given club.

```
GET /api/v3/clubs/{id}/members
```

#### Parameters

| Parameter | Type | Description | Required |
| --- | --- | --- | --- |
| id | int64 | The identifier of the club | Yes |
| page | int32 | Page number, defaults to 1 | No |
| per_page | int32 | Number of items per page, defaults to 30 | No |

### List Athlete Clubs (getLoggedInAthleteClubs)

Returns a list of the clubs whose membership includes the authenticated athlete.

```
GET /api/v3/athlete/clubs
```

#### Parameters

| Parameter | Type | Description | Required |
| --- | --- | --- | --- |
| page | int32 | Page number, defaults to 1 | No |
| per_page | int32 | Number of items per page, defaults to 30 | No |

## Gear

### Get Gear (getGearById)

Returns the equipment using its identifier.

```
GET /api/v3/gear/{id}
```

#### Parameters

| Parameter | Type | Description | Required |
| --- | --- | --- | --- |
| id | string | The identifier of the gear | Yes |

## Routes

### Get Route (getRouteById)

Returns a route using its identifier.

```
GET /api/v3/routes/{id}
```

#### Parameters

| Parameter | Type | Description | Required |
| --- | --- | --- | --- |
| id | int64 | The identifier of the route | Yes |

### Get Routes (getRoutesByAthleteId)

Returns a list of the routes created by the authenticated athlete using their identifier.

```
GET /api/v3/athletes/{id}/routes
```

#### Parameters

| Parameter | Type | Description | Required |
| --- | --- | --- | --- |
| id | int64 | The identifier of the athlete | Yes |
| page | int32 | Page number, defaults to 1 | No |
| per_page | int32 | Number of items per page, defaults to 30 | No |

### Export Route GPX (getRouteAsGPX)

Returns a GPX file of the route.

```
GET /api/v3/routes/{id}/export_gpx
```

#### Parameters

| Parameter | Type | Description | Required |
| --- | --- | --- | --- |
| id | int64 | The identifier of the route | Yes |

### Export Route TCX (getRouteAsTCX)

Returns a TCX file of the route.

```
GET /api/v3/routes/{id}/export_tcx
```

#### Parameters

| Parameter | Type | Description | Required |
| --- | --- | --- | --- |
| id | int64 | The identifier of the route | Yes |

## Segment Efforts

### Get Segment Effort (getEffortById)

Returns a segment effort from a specific activity.

```
GET /api/v3/segment_efforts/{id}
```

#### Parameters

| Parameter | Type | Description | Required |
| --- | --- | --- | --- |
| id | int64 | The identifier of the segment effort | Yes |

## Segments

### Explore segments (exploreSegments)

Returns the top 10 segments matching a specified query.

```
GET /api/v3/segments/explore
```

#### Parameters

| Parameter | Type | Description | Required |
| --- | --- | --- | --- |
| bounds | string | The latitude and longitude for the SW corner and NE corner of the area to explore, specified as 2 pairs of coordinates: [sw_lat,sw_lng,ne_lat,ne_lng] | Yes |
| activity_type | string | Desired activity type, "running" or "riding" | No |
| min_cat | int32 | The minimum climb category | No |
| max_cat | int32 | The maximum climb category | No |

### Get Authenticated User's Starred Segments (getLoggedInAthleteStarredSegments)

Returns the segments that the authenticated athlete has starred.

```
GET /api/v3/segments/starred
```

#### Parameters

| Parameter | Type | Description | Required |
| --- | --- | --- | --- |
| page | int32 | Page number, defaults to 1 | No |
| per_page | int32 | Number of items per page, defaults to 30 | No |

### Get Segment (getSegmentById)

Returns the specified segment.

```
GET /api/v3/segments/{id}
```

#### Parameters

| Parameter | Type | Description | Required |
| --- | --- | --- | --- |
| id | int64 | The identifier of the segment | Yes |

### Star Segment (starSegment)

Stars/Unstars the given segment for the authenticated athlete.

```
PUT /api/v3/segments/{id}/starred
```

#### Parameters

| Parameter | Type | Description | Required |
| --- | --- | --- | --- |
| id | int64 | The identifier of the segment to star | Yes |
| starred | boolean | If true, star the segment; if false, unstar the segment | No |

### Get Segment Leaderboard (getLeaderboardBySegmentId)

Returns the specified segment leaderboard.

```
GET /api/v3/segments/{id}/leaderboard
```

#### Parameters

| Parameter | Type | Description | Required |
| --- | --- | --- | --- |
| id | int64 | The identifier of the segment leaderboard | Yes |
| gender | string | 'M' or 'F' | No |
| age_group | string | The age range to filter results by, values: 0_19, 20_24, 25_34, 35_44, 45_54, 55_64, 65_plus | No |
| weight_class | string | The weight range to filter results by, values: 0_124, 125_149, 150_164, 165_179, 180_199, 200_plus (pounds) or 0_54, 55_64, 65_74, 75_84, 85_94, 95_plus (kilograms) | No |
| following | boolean | Filter by friends of the authenticated athlete | No |
| club_id | int64 | Filter by club | No |
| date_range | string | Filter by date range, values: this_year, this_month, this_week, today | No |
| context_entries | int32 | Number of context entries to return either side of the authenticated athlete, default is 2, maximum is 15 | No |
| page | int32 | Page number, defaults to 1 | No |
| per_page | int32 | Number of items per page, defaults to 30 | No |

### Get Segment All Efforts (getAllEffortsBySegmentId)

Returns a set of the authenticated athlete's segment efforts for a given segment.

```
GET /api/v3/segments/{id}/all_efforts
```

#### Parameters

| Parameter | Type | Description | Required |
| --- | --- | --- | --- |
| id | int64 | The identifier of the segment | Yes |
| page | int32 | Page number, defaults to 1 | No |
| per_page | int32 | Number of items per page, defaults to 30 | No |

## Stream Sets

### Get Activity Streams (getActivityStreams)

Returns the given activity's streams.

```
GET /api/v3/activities/{id}/streams
```

#### Parameters

| Parameter | Type | Description | Required |
| --- | --- | --- | --- |
| id | int64 | The identifier of the activity | Yes |
| keys | string | Desired stream types, allowed values: time, distance, latlng, altitude, velocity_smooth, heartrate, cadence, watts, temp, moving, grade_smooth | No |
| key_by_type | boolean | Must be true, used to return detailed information about the stream types | No |

### Get Route Streams (getRouteStreams)

Returns the given route's streams.

```
GET /api/v3/routes/{id}/streams
```

#### Parameters

| Parameter | Type | Description | Required |
| --- | --- | --- | --- |
| id | int64 | The identifier of the route | Yes |

### Get Segment Effort Streams (getSegmentEffortStreams)

Returns a set of streams for a segment effort completed by the authenticated athlete.

```
GET /api/v3/segment_efforts/{id}/streams
```

#### Parameters

| Parameter | Type | Description | Required |
| --- | --- | --- | --- |
| id | int64 | The identifier of the segment effort | Yes |
| keys | string | Desired stream types, allowed values: time, distance, latlng, altitude, velocity_smooth, heartrate, cadence, watts, temp, moving, grade_smooth | No |
| key_by_type | boolean | Must be true, used to return detailed information about the stream types | No |

### Get Segment Streams (getSegmentStreams)

Returns the given segment's streams.

```
GET /api/v3/segments/{id}/streams
```

#### Parameters

| Parameter | Type | Description | Required |
| --- | --- | --- | --- |
| id | int64 | The identifier of the segment | Yes |
| keys | string | Desired stream types, allowed values: distance, latlng, altitude | No |
| key_by_type | boolean | Must be true, used to return detailed information about the stream types | No |

## Uploads

### Create Upload (createUpload)

Uploads a new data file to create an activity from.

```
POST /api/v3/uploads
```

#### Body Parameters

| Parameter | Type | Description | Required |
| --- | --- | --- | --- |
| file | file | The uploaded file | Yes |
| data_type | string | The format of the uploaded file, supports: fit, fit.gz, tcx, tcx.gz, gpx, gpx.gz | Yes |
| name | string | The desired name of the resulting activity | No |
| description | string | The desired description of the resulting activity | No |
| trainer | string | Whether the resulting activity should be marked as having been performed on a trainer | No |
| commute | string | Whether the resulting activity should be tagged as a commute | No |
| external_id | string | The desired external identifier of the resulting activity | No |

### Get Upload (getUploadById)

Returns an upload for a given identifier.

```
GET /api/v3/uploads/{uploadId}
```

#### Parameters

| Parameter | Type | Description | Required |
| --- | --- | --- | --- |
| uploadId | int64 | The identifier of the upload | Yes |