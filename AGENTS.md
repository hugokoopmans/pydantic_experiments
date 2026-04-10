# pydantic_experiments / AGENTS.md

Single-file CLI experiment connecting Pydantic AI with Ollama.

## Running

```bash
python src/cli_ollama_agent.py
```

Exit the CLI with `exit` or `quit`.

## Requirements

- Ollama running locally on `http://localhost:11434/v1`
- Model: `llama3.2`

## Architecture

- Only file: `src/cli_ollama_agent.py`
- Provides `get_time()` tool (returns local datetime)
- Dutch default instruction: agent should keep answers short

## Notes

No tests, no CI. Pure runtime experiment.