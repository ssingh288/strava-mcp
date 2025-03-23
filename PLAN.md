NOTES

## Transport:
 - stdio: works only on local machine
 - sse: what is this? HTTP with Server-Sent Events (SSE)

JSON-RPC 2.0 as the message format

## Startup:

Claude Desktop is in charge of starting the server.
The same is true for Claude Code.
For remote access, this would obviously not be true.

## Use cases

Local tool:
 - local file search
 - local file edit

Remote tool:
 - weather


## How to write a server

https://modelcontextprotocol.io/tutorials/building-mcp-with-llms

Use Claude Code to write the server., and follow the instructions.

### Debugging

### Inspecting the server

npx @modelcontextprotocol/inspector uv --directory /Users/yorrickjansen/work/mcp/weather run weather.py


### Steps

1. Gather documentation
    a. Use firecrawl to get the documentation (install firecrawl MCP)
