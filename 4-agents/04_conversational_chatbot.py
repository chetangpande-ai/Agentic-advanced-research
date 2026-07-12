"""Simple terminal chatbot with dynamic user input.

Run:
    uv run python 4-agents/04_conversational_chatbot.py

Type messages in the terminal. Type exit, quit, or bye to stop.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


REPO_ROOT = Path(__file__).resolve().parent.parent


def build_client() -> tuple[OpenAI, str, float]:
    load_dotenv(REPO_ROOT / ".env")

    missing = [
        name
        for name in ("MESH_API_KEY", "MESH_API_URL", "MESH_MODEL")
        if not os.getenv(name)
    ]
    if missing:
        raise RuntimeError(f"Missing required .env values: {', '.join(missing)}")

    client = OpenAI(
        api_key=os.environ["MESH_API_KEY"],
        base_url=os.environ["MESH_API_URL"].rstrip("/"),
    )
    model = os.environ["MESH_MODEL"]
    temperature = float(os.getenv("MESH_TEMPERATURE", "0.2"))
    return client, model, temperature


def print_tokens(completion) -> None:
    usage = completion.usage
    if not usage:
        print("Tokens: not returned")
        return

    print(
        "Tokens:",
        f"input={usage.prompt_tokens}",
        f"output={usage.completion_tokens}",
        f"total={usage.total_tokens}",
    )


def main() -> None:
    client, model, temperature = build_client()

    messages = [
        {
            "role": "system",
            "content": "You are a helpful conversational chatbot. Answer clearly and briefly.",
        }
    ]

    print("Simple Conversational Chatbot")
    print(f"Model: {model}")
    print("Type exit, quit, or bye to stop.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except EOFError:
            print("\nChat ended.")
            break

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit", "bye"}:
            print("Chat ended.")
            break

        messages.append({"role": "user", "content": user_input})

        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )

        assistant_text = completion.choices[0].message.content or ""
        messages.append({"role": "assistant", "content": assistant_text})

        print(f"Assistant: {assistant_text}")
        print_tokens(completion)
        print(f"Messages kept in conversation history: {len(messages)}\n")


if __name__ == "__main__":
    main()
