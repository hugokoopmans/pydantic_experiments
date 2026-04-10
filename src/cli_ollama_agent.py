# cli_ollama_agent.py
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider


class ReadFile(BaseModel):
    """Request to read a file."""
    path: str


class WriteFile(BaseModel):
    """Request to write a file."""
    path: str
    content: str


model = OpenAIModel(
    model_name="llama3.1",
    provider=OpenAIProvider(base_url="http://localhost:11434/v1"),
)

agent = Agent(
    model=model,
    instructions="Je bent een behulpzame commandline assistent. Gebruik read_file, write_file, en get_time tools als dat van pas komt. Houd antwoorden kort.",
)


@agent.tool_plain
def read_file(request: ReadFile) -> str:
    """Leest volledige inhoud van een bestand op het opgegeven pad."""
    path = Path(request.path).resolve()

    if not path.is_relative_to(Path.cwd().resolve()):
        return "Fout: Toegang geweigerd - pad buiten werkende map."

    if not path.is_file():
        return f"Fout: Bestand niet gevonden: {request.path}"

    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            content = path.read_text(encoding="latin-1")
        except UnicodeDecodeError:
            import base64
            return f"Bestand lijkt binair. Base64: {base64.b64encode(path.read_bytes()).decode()[:200]}..."

    return content


@agent.tool_plain
def write_file(request: WriteFile) -> str:
    """Schrijft tekst naar een bestand op opgegeven pad. Retourneert status bericht."""
    path = Path(request.path)

    try:
        parent = path.parent.resolve()
        parent.relative_to(Path.cwd().resolve())
    except ValueError:
        return "Fout: Toegang geweigerd."

    if path.exists():
        return f"Fout: Bestand bestaat al: {request.path}"

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(request.content, encoding="utf-8")

    return f"Bestand gemaakt: {path}"


@agent.tool_plain
def get_time() -> str:
    """Geeft de lokale datum en tijd terug."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main() -> None:
    print("MyAgent CLI. Typ 'exit' om te stoppen.")
    while True:
        prompt = input("> ").strip()
        if prompt.lower() in {"exit", "quit", "doei"}:
            break
        result = agent.run_sync(prompt)
        print(result.output)
        print()


if __name__ == "__main__":
    main()
