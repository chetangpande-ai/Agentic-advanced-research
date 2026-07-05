"""Real project style: keep chat history per user/session.

Run:
    uv run python agents-context/02_realtime_chat_session.py

In a real app, the browser/mobile client sends a user_id or session_id.
The backend loads that session's previous messages, adds the new user input,
sends the full recent history to the LLM, then saves the assistant reply.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


REPO_ROOT = Path(__file__).resolve().parent.parent


class ChatSessionStore:
    """In real projects this is usually Redis, Postgres, Cosmos DB, etc."""

    def __init__(self) -> None:
        self._messages_by_session: dict[str, list[dict[str, str]]] = {}

    def get_messages(self, session_id: str) -> list[dict[str, str]]:
        return self._messages_by_session.setdefault(
            session_id,
            [
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Answer briefly.",
                }
            ],
        )

    def save_message(self, session_id: str, role: str, content: str) -> None:
        self.get_messages(session_id).append({"role": role, "content": content})


def build_llm() -> ChatOpenAI:
    load_dotenv(REPO_ROOT / ".env")

    return ChatOpenAI(
        api_key=os.environ["MESH_API_KEY"],
        base_url=os.environ["MESH_API_URL"].rstrip("/"),
        model=os.environ["MESH_MODEL"],
        temperature=float(os.getenv("MESH_TEMPERATURE", "0.2")),
        timeout=float(os.getenv("MESH_TIMEOUT_SECONDS", "60")),
    )


def handle_chat_message(
    llm: ChatOpenAI,
    store: ChatSessionStore,
    session_id: str,
    user_input: str,
) -> str:
    store.save_message(session_id, "user", user_input)

    context_window = list(store.get_messages(session_id))
    response = llm.invoke(context_window)

    store.save_message(session_id, "assistant", response.content)
    print_request_details(session_id, context_window, response)
    return response.content


def print_request_details(session_id: str, messages: list[dict[str, str]], response: Any) -> None:
    usage = getattr(response, "usage_metadata", None) or {}

    print(f"\nSession: {session_id}")
    print("Context window sent to LLM:")
    for message in messages:
        print(f"- {message['role']}: {message['content']}")
    print(
        "Tokens:",
        f"input={usage.get('input_tokens')}",
        f"output={usage.get('output_tokens')}",
        f"total={usage.get('total_tokens')}",
    )


def main() -> None:
    llm = build_llm()
    store = ChatSessionStore()
    session_id = "user-chetan-browser-session-1"

    answer1 = handle_chat_message(llm, store, session_id, "Hi, I am Chetan.")
    print("Assistant:", answer1)

    answer2 = handle_chat_message(llm, store, session_id, "What is my name?")
    print("Assistant:", answer2)

    print(
        "\nReal app pattern: session storage is the memory. The LLM only sees "
        "what the backend loads from storage and sends in the current request."
    )


if __name__ == "__main__":
    main()
