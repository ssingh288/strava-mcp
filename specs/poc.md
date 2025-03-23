# Strava MCP Server

I want to create a MCP server that can be used to interact with the Strava API.


## Features


### Tools

- [ ] Get user's activities
- [ ] Get a specific activity
- [ ] Get the leaderboard of an activity
- [ ] Get the segments of an activity

### Prompts

No prompts are to be exposed for now.


### Resources

No resources are to be exposed for now.



## Details

Be VERY CAREFUL to follow the instructions:

1. Read the documentation of the Strava API and MCP in ai-docs directory.
2. Do not add any dependencies to the project, except for the ones that are already installed (see pyproject.toml).
3. Add relevant comments to the code to explain what it does.
4. Complete the README.md file, and add all relevant information.
5. Write unit tests for the code, and add them to the tests directory.
6. Code must be written in the strava_mcp directory.
7. Implement logging of errors and warnings.
8. Use pydantic for Model Driven Development.
9. Use pydantic-settings for configuration.
10. Separate logic, api, and data access layers.
11. Use type hints and docstrings to describe the code.
12. Write the tests first, and then implement the code 
13. Setup CI/CD pipeline with Github Actions, and make unit tests pass, then that server starts. Upload code coverage to Codecov.
14. Use uv to manage the project.
15. Setup pre-commit hooks with Ruff, isort, and pyright.



