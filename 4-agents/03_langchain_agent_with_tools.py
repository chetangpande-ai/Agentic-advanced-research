"""LangChain create_agent tool calling: agent-managed loop.

Run:
    uv run python 4-agents/03_langchain_agent_with_tools.py

Learning point:
    You provide Python functions as tools. The agent handles model calls,
    tool execution, tool-result messages, and the final answer loop.
"""

from __future__ import annotations
import os
from pathlib import Path
from typing import Any
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI


REPO_ROOT = Path(__file__).resolve().parent.parent


def build_llm() -> ChatOpenAI:
    load_dotenv(REPO_ROOT / ".env")

    missing = [
        name
        for name in ("MESH_API_KEY", "MESH_API_URL", "MESH_MODEL")
        if not os.getenv(name)
    ]
    if missing:
        raise RuntimeError(f"Missing required .env values: {', '.join(missing)}")

    return ChatOpenAI(
        api_key=os.environ["MESH_API_KEY"],
        base_url=os.environ["MESH_API_URL"].rstrip("/"),
        model=os.environ["MESH_MODEL"],
        temperature=float(os.getenv("MESH_TEMPERATURE", "0.2")),
        timeout=float(os.getenv("MESH_TIMEOUT_SECONDS", "60")),
    )


def get_order_status(order_id: str) -> str:
    """Get the latest shipping status for an order."""

    print(f"\n[PYTHON TOOL EXECUTED] get_order_status(order_id={order_id})")
    return (
        f"Order {order_id} is SHIPPED. "
        "Last updated at 2026-07-11T09:30:00+05:30."
    )


def print_agent_messages(result: dict[str, Any]) -> None:
    print("\n===== Agent Messages =====")
    for index, message in enumerate(result["messages"], start=1):
        print(f"\nMessage {index}: {message.__class__.__name__}")
        print("content:", message.content)
        tool_calls = getattr(message, "tool_calls", None)
        if tool_calls:
            print("tool_calls:", tool_calls)
        usage = getattr(message, "usage_metadata", None)
        if usage:
            print("usage:", usage)


def main() -> None:
    agent = create_agent(
        model=build_llm(),
        tools=[get_order_status],
        system_prompt="Always call get_order_status before answering order status questions.",
    )

    print("STEP 1: Invoke LangChain agent")
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "What is the status of order ORD-1001?",
                }
            ]
        }
    )

    print("\n===== Final Answer =====")
    print(result["messages"][-1].content)

    print_agent_messages(result)


if __name__ == "__main__":
    main()
