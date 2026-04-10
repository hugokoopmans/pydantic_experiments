# pydantic_experiments

Single-file Pydantic AI + Ollama experiment.

## Running

```bash
python src/cli_ollama_agent.py
```

Requires Ollama running locally on `http://localhost:11434/v1` with `llama3.2` model.

## Architecture

- `src/cli_ollama_agent.py` - CLI with `get_time()` tool and Dutch instructions

## Exit

Type `exit` or `quit` to exit.
