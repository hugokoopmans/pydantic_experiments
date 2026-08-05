import logging
import os

import uvicorn
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider


logger = logging.getLogger("a2a_agent_b")


def configure_logging() -> None:
    level_name = os.getenv("A2A_B_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def build_specialist_agent() -> Agent[None, str]:
    model = OpenAIChatModel(
        model_name=os.getenv("A2A_MODEL_NAME", "llama3.1"),
        provider=OpenAIProvider(base_url=os.getenv("A2A_MODEL_BASE_URL", "http://localhost:11434/v1")),
    )

    return Agent(
        model=model,
        instructions=(
            "Je bent Agent B, een specialist die korte, duidelijke antwoorden geeft. "
            "Antwoord in het Nederlands. "
            "Gebruik maximaal 5 zinnen tenzij expliciet om meer detail wordt gevraagd."
        ),
        name="agent-b-specialist",
    )


def main() -> None:
    configure_logging()

    host = os.getenv("A2A_B_HOST", "127.0.0.1")
    port = int(os.getenv("A2A_B_PORT", "8100"))
    public_url = os.getenv("A2A_B_PUBLIC_URL", f"http://{host}:{port}")

    specialist = build_specialist_agent()
    app = specialist.to_a2a(
        name="Agent B Specialist",
        url=public_url,
        version="0.1.0",
        description="Specialist agent for short delegated answers.",
    )

    logger.info("Starting Agent B A2A server on %s:%d", host, port)
    uvicorn.run(app, host=host, port=port, log_level=os.getenv("A2A_B_UVICORN_LOG_LEVEL", "info"))


if __name__ == "__main__":
    main()
