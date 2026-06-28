# pydantic_experiments / AGENTS.md

Single-file CLI experiment connecting Pydantic AI with Ollama.

## Running

```bash
python src/cli_agent.py
```

Exit the CLI with `exit` or `quit`.

## Requirements

- Ollama running locally on `http://localhost:11434/v1`
- Model: `llama3.2`

## Architecture

- Only file: `src/cli_ollama_agent.py`
- Provides `get_time()` tool (returns local datetime)
- Dutch default instruction: agent should keep answers short
- Security via `@agent.tool_plain` decorators (path validation, 10MB limit)
- Bestandslezen/schrijven via Pydantic AI ReadFile/WriteFile API

## Best Practices

- Gebruik **altijd Pydantic AI methoden** waar mogelijk (RunScript, ReadFile, WriteFile, ListDirectory)
- **Niet zelf functionaliteit dupliceren** die Pydantic AI al heeft geïmplementeerd
- Gebruik `@agent.tool_plain` voor custom tools met security checks
- Padvalidatie en filesize limits zijn verplicht bij file operaties

## Notes

No tests, no CI. Pure runtime experiment.