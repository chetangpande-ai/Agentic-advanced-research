"""Simple Chat Completions API example using existing Mesh .env settings.

Run:
    uv run python 4-agents/01_chat_completion_api_metadata.py

This prints:
    - request messages
    - assistant content
    - input/output/total tokens
    - full response metadata returned by the LLM gateway
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


REPO_ROOT = Path(__file__).resolve().parent.parent


def load_settings() -> tuple[OpenAI, str, float]:
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


def print_json(title: str, value: object) -> None:
    print(f"\n===== {title} =====")
    print(json.dumps(value, indent=2, ensure_ascii=False))


def main() -> None:
    client, model, temperature = load_settings()

    messages = [
        {
            "role": "system",
            "content": "You are a concise assistant. Reply in one short paragraph.",
        },
        {
            "role": "user",
            "content": "Explain the Chat Completions API concept in simple words.",
        },
    ]

    print("Model:", model)
    print("Base URL:", os.environ["MESH_API_URL"].rstrip("/"))
    print_json("Input Messages Sent To LLM", messages)

    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )

    response = completion.model_dump()
    choice = completion.choices[0]
    usage = completion.usage

    print("\n===== Assistant Content =====")
    print(choice.message.content)

    print("\n===== Token Usage =====")
    print("input_tokens:", usage.prompt_tokens if usage else None)
    print("output_tokens:", usage.completion_tokens if usage else None)
    print("total_tokens:", usage.total_tokens if usage else None)

    print("\n===== Common Metadata =====")
    print("id:", completion.id)
    print("object:", completion.object)
    print("created:", completion.created)
    print("model:", completion.model)
    print("finish_reason:", choice.finish_reason)
    print("system_fingerprint:", getattr(completion, "system_fingerprint", None))

    print_json("Full Raw Response Metadata", response)


if __name__ == "__main__":
    main()
