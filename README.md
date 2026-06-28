# pydantic_experiments

Single-file Pydantic AI + Ollama experiment.

## Running an agent

```bash
python src/cli_agent.py
```

## MCP Server

Run the MCP server as a standalone process (streamable HTTP):

```bash
MCP_TRANSPORT=streamable-http MCP_LOG_LEVEL=DEBUG python src/mcp_server.py
```

The MCP server has explicit logging for startup, tool calls, validation warnings, and unknown tool errors.

Set log level with `MCP_LOG_LEVEL`:

```bash
MCP_LOG_LEVEL=DEBUG python src/mcp_server.py
```

Supported levels include `DEBUG`, `INFO`, `WARNING`, `ERROR`.

Optional server settings:

- `MCP_HOST` (default `127.0.0.1`)
- `MCP_PORT` (default `8000`)
- `MCP_TRANSPORT` (default `streamable-http`)

## Two-Terminal Workflow (Server + Client)

Terminal 1: start the MCP server

```bash
MCP_TRANSPORT=streamable-http MCP_LOG_LEVEL=DEBUG python src/mcp_server.py
```

Terminal 2: start the CLI agent and connect to that MCP server

```bash
MCP_SERVER_URL=http://127.0.0.1:8000/mcp python src/cli_agent.py
```

The CLI agent keeps local file tools (`read_file`, `write_file`) and can use MCP tools from the server with prefix `mcp_`.

Requires Ollama or Llama.cpp running locally.

For Ollama on `http://localhost:11434/v1` with `llama3.2` model. For Llama.cpp on `http://localhost:8000` with an available model.

## Architecture

- `src/cli_agent.py` - CLI client met lokale file-tools plus MCP toolset via `MCP_SERVER_URL`
- `src/mcp_server.py` - Standalone MCP server met `echo` en `get_time` tools (streamable HTTP)
- `src/secure_path.py` - Secure path validation (10MB limit, cwd restriction)

## Exit

Type `exit` or `quit` to exit.
