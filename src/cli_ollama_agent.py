# cli_ollama_agent.py
import logging
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.messages import ModelResponse
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

# --- Logging configuratie ---
# File handler: alle logs naar bestand
file_handler = logging.FileHandler("agent.log", encoding="utf-8")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

# Console handler: alleen warnings en errors (geen INFO spam in CLI)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler],
)
logger = logging.getLogger("agent")


class ReadFile(BaseModel):
    """Request to read a file."""
    path: str


class WriteFile(BaseModel):
    """Request to write content to a file."""
    path: str
    content: str

# ollama local
model = OpenAIChatModel(
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
    logger.info("📖 read_file aangeroepen voor: %s", request.path)
    path = Path(request.path).resolve()

    if not path.is_relative_to(Path.cwd().resolve()):
        logger.warning("⛔ Toegang geweigerd (buiten cwd): %s", request.path)
        return "Fout: Toegang geweigerd - pad buiten werkende map."

    if not path.is_file():
        logger.warning("❌ Bestand niet gevonden: %s", request.path)
        return f"Fout: Bestand niet gevonden: {request.path}"

    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            content = path.read_text(encoding="latin-1")
        except UnicodeDecodeError:
            import base64
            logger.info("📄 Binair bestand gedetecteerd: %s", request.path)
            return f"Bestand lijkt binair. Base64: {base64.b64encode(path.read_bytes()).decode()[:200]}..."

    logger.info("✅ Bestand gelezen: %s (%d bytes)", request.path, len(content))
    return content


@agent.tool_plain
def write_file(request: WriteFile) -> str:
    """Schrijft tekst naar een bestand op opgegeven pad. Retourneert status bericht."""
    logger.info("✍️ write_file aangeroepen voor: %s", request.path)
    path = Path(request.path)

    try:
        parent = path.parent.resolve()
        parent.relative_to(Path.cwd().resolve())
    except ValueError:
        logger.warning("⛔ Toegang geweigerd (buiten cwd): %s", request.path)
        return "Fout: Toegang geweigerd."

    if path.exists():
        logger.warning("❌ Bestand bestaat al: %s", request.path)
        return f"Fout: Bestand bestaat al: {request.path}"

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(request.content, encoding="utf-8")

    logger.info("✅ Bestand geschreven: %s (%d bytes)", path, len(request.content))
    return f"Bestand gemaakt: {path}"


@agent.tool_plain
def get_time() -> str:
    """Geeft de lokale datum en tijd terug."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info("🕐 get_time aangeroepen → %s", now)
    return now


def log_tool_calls(result) -> None:
    """Log tool calls en results uit de run history."""
    for msg in result.all_messages():
        if isinstance(msg, ModelResponse):
            for part in msg.parts:
                if hasattr(part, 'tool_name'):
                    logger.info("🔧 Tool call: %s → %s", part.tool_name, getattr(part, 'args', {}))
                if hasattr(part, 'content') and hasattr(part, 'tool_name'):
                    logger.info("🔧 Tool result: %s → %s", part.tool_name, str(part.content)[:100])


def main() -> None:
    logger.info("=" * 60)
    logger.info("MyAgent CLI gestart")
    logger.info("=" * 60)
    print("MyAgent CLI. Typ 'exit' om te stoppen.\n(Logs worden opgeslagen in agent.log)")
    while True:
        prompt = input("> ").strip()
        if prompt.lower() in {"exit", "quit", "doei"}:
            logger.info("👋 Afsluiten op verzoek van gebruiker")
            break
        logger.info("🧠 Gebruiker vroeg: %s", prompt)
        result = agent.run_sync(prompt)
        logger.info("💬 Agent antwoord: %s", result.output)

        log_tool_calls(result)

        print(result.output)
        print()

    logger.info("Agent gestopt")


if __name__ == "__main__":
    main()

