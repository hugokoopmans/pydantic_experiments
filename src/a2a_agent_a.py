import asyncio
import logging
import os
import uuid
from typing import Any

import httpx
from fasta2a.client import A2AClient
from fasta2a.schema import Message, Task


logger = logging.getLogger("a2a_agent_a")


def configure_logging() -> None:
    level_name = os.getenv("A2A_A_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


AGENT_B_URL = os.getenv("A2A_AGENT_B_URL", "http://127.0.0.1:8100")
A2A_TIMEOUT_SECONDS = float(os.getenv("A2A_TIMEOUT_SECONDS", "30"))
A2A_POLL_SECONDS = float(os.getenv("A2A_POLL_SECONDS", "0.5"))
A2A_MAX_POLLS = int(os.getenv("A2A_MAX_POLLS", "40"))


def _extract_text_from_parts(parts: list[dict[str, Any]]) -> str:
    text_chunks: list[str] = []
    for part in parts:
        if part.get("kind") == "text" and isinstance(part.get("text"), str):
            text_chunks.append(part["text"])
    return "\n".join(text_chunks).strip()


def _extract_text_from_task(task: Task) -> str:
    artifacts = task.get("artifacts", [])
    for artifact in artifacts:
        text = _extract_text_from_parts(artifact.get("parts", []))
        if text:
            return text

    status = task.get("status", {})
    status_message = status.get("message")
    if status_message and isinstance(status_message, dict):
        text = _extract_text_from_parts(status_message.get("parts", []))
        if text:
            return text

    return ""


async def _call_agent_b(prompt: str) -> str:
    message: Message = {
        "role": "user",
        "kind": "message",
        "message_id": str(uuid.uuid4()),
        "parts": [{"kind": "text", "text": prompt}],
    }

    timeout = httpx.Timeout(A2A_TIMEOUT_SECONDS)
    async with httpx.AsyncClient(base_url=AGENT_B_URL, timeout=timeout) as http_client:
        client = A2AClient(base_url=AGENT_B_URL, http_client=http_client)
        response = await client.send_message(
            message,
            configuration={
                "blocking": True,
                "accepted_output_modes": ["text/plain"],
                "history_length": 10,
            },
        )

        if "error" in response:
            raise RuntimeError(f"A2A error: {response['error']}")

        result = response.get("result")
        if not isinstance(result, dict):
            raise RuntimeError("A2A response had no valid result")

        if result.get("kind") == "message":
            text = _extract_text_from_parts(result.get("parts", []))
            if text:
                return text

        if result.get("kind") == "task":
            task_id = result.get("id")
            if not isinstance(task_id, str):
                raise RuntimeError("A2A task result missing task id")

            for _ in range(A2A_MAX_POLLS):
                task_response = await client.get_task(task_id)
                if "error" in task_response:
                    raise RuntimeError(f"A2A task error: {task_response['error']}")

                task = task_response.get("result")
                if not isinstance(task, dict):
                    await asyncio.sleep(A2A_POLL_SECONDS)
                    continue

                state = task.get("status", {}).get("state")
                if state in {"completed", "failed", "rejected", "canceled", "unknown"}:
                    text = _extract_text_from_task(task)
                    if text:
                        return text
                    raise RuntimeError(f"A2A task ended with state={state} without text output")

                await asyncio.sleep(A2A_POLL_SECONDS)

            raise RuntimeError("A2A task polling timed out")

    raise RuntimeError("A2A response type not supported")


async def delegate_to_agent_b(prompt: str) -> str:
    logger.info("Delegating to Agent B at %s", AGENT_B_URL)
    try:
        result = await _call_agent_b(prompt)
        logger.info("Agent B response length=%d", len(result))
        return result
    except Exception as exc:  # noqa: BLE001
        logger.exception("Delegation to Agent B failed")
        return (
            "FOUT_AGENT_B: Agent B was niet bereikbaar of gaf geen geldig antwoord. "
            f"Details: {exc}"
        )


async def main() -> None:
    configure_logging()
    logger.info("Agent A started. Agent B URL=%s", AGENT_B_URL)

    print("Agent A CLI. Typ 'exit' om te stoppen.")
    print(f"Agent B endpoint: {AGENT_B_URL}")

    while True:
        prompt = input("> ").strip()
        if prompt.lower() in {"exit", "quit", "doei"}:
            break

        result = await delegate_to_agent_b(prompt)
        print(result)
        print()


if __name__ == "__main__":
    asyncio.run(main())
