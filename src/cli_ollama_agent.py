# cli_ollama_agent.py
from datetime import datetime

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

model = OpenAIModel(
    model_name="llama3.2",
    provider=OpenAIProvider(base_url="http://localhost:11434/v1"),
)

agent = Agent(
    model=model,
    instructions="Je bent een behulpzame commandline assistent. Houd antwoorden kort.",
)

@agent.tool_plain
def get_time() -> str:
    """Geef de lokale tijd terug."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main() -> None:
    print("MyAgent CLI. Typ 'exit' om te stoppen.")
    while True:
        prompt = input("> ").strip()
        if prompt.lower() in {"exit", "quit"}:
            break

        result = agent.run_sync(prompt)
        print(result.output)
        print()

if __name__ == "__main__":
    main()
