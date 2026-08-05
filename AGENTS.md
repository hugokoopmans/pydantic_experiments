# pydantic_experiments / AGENTS.md

Compact overzicht voor contributors van deze experimenteerrepo rond Pydantic AI.

De repo bevat drie losse experimenten:

- CLI agent (lokale tools + model)
- MCP server + client-koppeling
- A2A Agent A (coordinator) + Agent B (specialist)

## Running

```bash
python src/cli_agent.py
```

MCP server starten:

```bash
MCP_TRANSPORT=streamable-http MCP_LOG_LEVEL=DEBUG python src/mcp_server.py
```

A2A (2 terminals):

```bash
# terminal 1
python src/a2a_agent_b.py

# terminal 2
A2A_AGENT_B_URL=http://127.0.0.1:8100 python src/a2a_agent_a.py
```

## Requirements

- Python venv in dit project
- Ollama lokaal op `http://localhost:11434/v1`
- Voor A2A experiment: `fasta2a`

## Architecture

- `src/cli_agent.py` - CLI client met lokale file-tools en MCP toolset
- `src/mcp_server.py` - standalone MCP server (`echo`, `get_time`)
- `src/a2a_agent_a.py` - Agent A coordinator (CLI) die delegeert naar Agent B
- `src/a2a_agent_b.py` - Agent B specialist als A2A server
- `src/secure_path.py` - padvalidatie en file-size guardrails

## Best Practices

- Werk in kleine iteraties en valideer per stap (syntax + runtime).
- Houd MCP en A2A als losse processen; start ze in aparte terminals.
- Gebruik logging expliciet in server/client scripts voor debugbaarheid.
- Gebruik padvalidatie en size-limits bij file-operaties.

## Notes

- Geen test-suite of CI; dit is een runtime leerrepo.
- Exit uit CLI's met `exit` of `quit`.