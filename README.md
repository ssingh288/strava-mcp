# Strava MCP Server

A Model Context Protocol (MCP) server for interacting with the Strava API.

## Features

This MCP server provides tools to access data from the Strava API:

- Get user's activities
- Get a specific activity's details
- Get the segments of an activity
- Get the leaderboard of a segment

## Installation

### Prerequisites

- Python 3.13 or later
- Strava API credentials (client ID, client secret, and refresh token)

### Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd strava
```

2. Install dependencies with [uv](https://docs.astral.sh/uv/):

```bash
uv install
```

3. Set up environment variables with your Strava API credentials:

```bash
export STRAVA_CLIENT_ID=your_client_id
export STRAVA_CLIENT_SECRET=your_client_secret
export STRAVA_REFRESH_TOKEN=your_refresh_token
```

Alternatively, you can create a `.env` file in the root directory with these variables.

## Usage

### Running the Server

To run the server:

```bash
python main.py
```

### Development Mode

You can run the server in development mode with the MCP CLI:

```bash
mcp dev main.py
```

### Installing in Claude Desktop

To install the server in Claude Desktop:

```bash
mcp install main.py
```

## Tools

### Get User Activities

Retrieves a list of activities for the authenticated user.

**Parameters:**
- `before` (optional): Epoch timestamp to filter activities before a certain time
- `after` (optional): Epoch timestamp to filter activities after a certain time
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Number of items per page (default: 30)

### Get Activity

Gets detailed information about a specific activity.

**Parameters:**
- `activity_id`: The ID of the activity
- `include_all_efforts` (optional): Whether to include all segment efforts (default: false)

### Get Activity Segments

Retrieves the segments from a specific activity.

**Parameters:**
- `activity_id`: The ID of the activity

### Get Segment Leaderboard

Gets the leaderboard for a specific segment.

**Parameters:**
- `segment_id`: The ID of the segment
- `gender` (optional): Filter by gender ('M' or 'F')
- `age_group` (optional): Filter by age group
- `weight_class` (optional): Filter by weight class
- `following` (optional): Filter by friends of the authenticated athlete
- `club_id` (optional): Filter by club
- `date_range` (optional): Filter by date range
- `context_entries` (optional): Number of context entries
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Number of items per page (default: 30)

## Development

### Project Structure

- `strava_mcp/`: Main package directory
  - `__init__.py`: Package initialization
  - `config.py`: Configuration settings using pydantic-settings
  - `models.py`: Pydantic models for Strava API entities
  - `api.py`: Low-level API client for Strava
  - `service.py`: Service layer for business logic
  - `server.py`: MCP server implementation
- `tests/`: Unit tests
- `main.py`: Entry point to run the server

### Running Tests

To run tests:

```bash
pytest
```

## License

[MIT License](LICENSE)

## Acknowledgements

- [Strava API](https://developers.strava.com/)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)