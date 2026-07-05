"""Smallest possible context-window example.

Run:
    uv run python agents-context/01_simple_context_window.py

Idea:
    The LLM does not remember earlier API calls by magic.
    Your application must send the previous messages again.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


REPO_ROOT = Path(__file__).resolve().parent.parent


def build_llm() -> ChatOpenAI:
    load_dotenv(REPO_ROOT / ".env")

    return ChatOpenAI(
        api_key=os.environ["MESH_API_KEY"],
        base_url=os.environ["MESH_API_URL"].rstrip("/"),
        model=os.environ["MESH_MODEL"],
        temperature=float(os.getenv("MESH_TEMPERATURE", "0.2")),
        timeout=float(os.getenv("MESH_TIMEOUT_SECONDS", "60")),
    )


def print_token_usage(response: Any) -> None:
    usage = getattr(response, "usage_metadata", None) or {}
    print(
        "Tokens:",
        f"input={usage.get('input_tokens')}",
        f"output={usage.get('output_tokens')}",
        f"total={usage.get('total_tokens')}",
    )


def main() -> None:
    llm = build_llm()

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Answer briefly.",
        }
    ]

    print("\nSTEP 1: User tells the LLM their name")
    messages.append({"role": "user", "content": "Hi, I am Chetan."})
    response = llm.invoke(messages)
    messages.append({"role": "assistant", "content": response.content})
    print("Assistant:", response.content)
    print_token_usage(response)

    print("\nSTEP 2: User asks a follow-up question")
    messages.append({"role": "user", "content": "What is my name?"})

    print("\nContext window sent to LLM in step 2:")
    for message in messages:
        print(f"- {message['role']}: {message['content']}")

    response = llm.invoke(messages)
    print("\nAssistant:", response.content)
    print_token_usage(response)

    print(
        "\nKey learning: the model answered from the message history that "
        "this script sent in step 2."
    )


if __name__ == "__main__":
    main()
