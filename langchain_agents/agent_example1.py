import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

REPO_ROOT = Path(__file__).resolve().parent.parent


def build_llm() -> ChatOpenAI:
    """Create the LLM using Mesh API settings from the project .env."""

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


def get_weather(city: str) -> str:
    """Get weather for a given city."""

    return f"It's always sunny in {city}!"


def main() -> None:
    agent = create_agent(
        model=build_llm(),
        tools=[get_weather],
        system_prompt=(
            "You are a helpful assistant. "
            "Always call get_weather before answering weather questions."
        ),
        checkpointer=InMemorySaver(),
    )


    # Identifies one conversation
    config = {
        "configurable": {
            "thread_id": "chetan-chat"
        }
    }
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "I am chetan",
                }
            ]
        },
        config=config,
    )
    print(result["messages"][-1].content_blocks)

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "who am i?",
                }
            ]
        },
        config=config,
    )
    print(result["messages"][-1].content_blocks)



if __name__ == "__main__":
    main()
