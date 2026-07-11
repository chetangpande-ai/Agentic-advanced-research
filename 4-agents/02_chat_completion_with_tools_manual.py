"""Chat Completions API tool calling: manual loop.

Run:
    uv run python 4-agents/02_chat_completion_with_tools_manual.py

Learning point:
    The model can request a tool call, but your code must execute the tool
    and send the tool result back to the model.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


REPO_ROOT = Path(__file__).resolve().parent.parent


def build_client() -> tuple[OpenAI, str]:
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
    return client, os.environ["MESH_MODEL"]


def get_order_status(order_id: str) -> dict[str, str]:
    """Fake business tool. In real life this may call an API or database."""

    print(f"\n[PYTHON TOOL EXECUTED] get_order_status(order_id={order_id})")
    return {
        "order_id": order_id,
        "status": "SHIPPED",
        "last_updated": "2026-07-11T09:30:00+05:30",
    }


def main() -> None:
    client, model = build_client()

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_order_status",
                "description": "Get the latest shipping status for an order.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "string",
                            "description": "Order ID, for example ORD-1001.",
                        }
                    },
                    "required": ["order_id"],
                },
            },
        }
    ]

    messages = [
        {
            "role": "system",
            "content": "Use the get_order_status tool before answering order status questions.",
        },
        {
            "role": "user",
            "content": "What is the status of order ORD-1001?",
        },
    ]

    print("STEP 1: Send messages and tool schema to Chat Completions API")
    first_response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "get_order_status"}},
    )

    assistant_message = first_response.choices[0].message
    tool_calls = assistant_message.tool_calls or []
    print("Model requested tool calls:", len(tool_calls))

    messages.append(assistant_message.model_dump(exclude_none=True))

    print("\nSTEP 2: Your Python code manually executes requested tools")
    for tool_call in tool_calls:
        args = json.loads(tool_call.function.arguments)
        if tool_call.function.name == "get_order_status":
            tool_result = get_order_status(**args)
        else:
            raise ValueError(f"Unknown tool: {tool_call.function.name}")

        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result),
            }
        )

    print("\nSTEP 3: Send tool result back to Chat Completions API")
    final_response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
    )

    print("\n===== Final Answer =====")
    print(final_response.choices[0].message.content)

    print("\n===== Token Usage =====")
    usage = final_response.usage
    print("input_tokens:", usage.prompt_tokens if usage else None)
    print("output_tokens:", usage.completion_tokens if usage else None)
    print("total_tokens:", usage.total_tokens if usage else None)


if __name__ == "__main__":
    main()
