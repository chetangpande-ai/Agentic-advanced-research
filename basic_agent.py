"""Basic LangChain agent using your Mesh API LLM.

This follows the LangChain quickstart shape:

1. Define one tool as a normal Python function.
2. Create an agent with `create_agent`.
3. Invoke the agent with one user message.
4. Print the final answer.

Run:
    uv run python basic_agent.py

Ask your own question:
    uv run python basic_agent.py "What's the weather in Mumbai?"

Required .env values:
    MESH_API_KEY=...
    MESH_API_URL=https://api.meshapi.ai/v1
    MESH_MODEL=your-model-name

Optional .env values:
    MESH_TEMPERATURE=0.2
    MESH_TIMEOUT_SECONDS=60
    TAVILY_API_KEY=...
"""

from __future__ import annotations

import json
import os
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI


def get_weather(city: str) -> str:
    """Get weather for a given city. Use this for every weather question."""

    return f"It's always sunny in {city}!"


def search_latest_information(query: str) -> str:
    """Search for current or latest information. Use for recent events, news, or facts that may change."""

    load_dotenv()

    if os.getenv("TAVILY_API_KEY"):
        return _search_tavily(query)

    return _search_wikipedia(query)


def _search_tavily(query: str) -> str:
    payload = {
        "query": query,
        "search_depth": "basic",
        "max_results": 3,
        "include_answer": True,
    }
    request = Request(
        "https://api.tavily.com/search",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {os.environ['TAVILY_API_KEY']}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError) as exc:
        return f"Tavily search failed: {exc}"

    answer = data.get("answer") or "No direct answer returned."
    results = data.get("results", [])
    sources = [
        f"- {item.get('title', 'Untitled')}: {item.get('url', 'no url')}"
        for item in results[:3]
    ]

    return f"{answer}\n\nSources:\n" + "\n".join(sources)


def _search_wikipedia(query: str) -> str:
    params = urlencode(
        {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": 3,
            "format": "json",
        }
    )
    request = Request(
        f"https://en.wikipedia.org/w/api.php?{params}",
        headers={"User-Agent": "agentic-practise-basic-agent/0.1"},
    )

    try:
        with urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError) as exc:
        return f"Wikipedia search failed: {exc}"

    pages = data.get("query", {}).get("search", [])
    if not pages:
        return f"No Wikipedia results found for: {query}"

    lines = []
    for page in pages:
        title = page.get("title", "Untitled")
        snippet = re.sub("<.*?>", "", page.get("snippet", ""))
        url_title = title.replace(" ", "_")
        lines.append(f"- {title}: {snippet} https://en.wikipedia.org/wiki/{url_title}")

    return "TAVILY_API_KEY is not set, so I used Wikipedia instead.\n\n" + "\n".join(lines)


def build_mesh_model() -> ChatOpenAI:
    """Create a LangChain chat model using Mesh API settings from .env."""

    load_dotenv()

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


def main() -> None:
    question = " ".join(sys.argv[1:]) or "What's the weather in San Francisco?"

    agent = create_agent(
        model=build_mesh_model(),
        tools=[get_weather, search_latest_information],
        system_prompt=(
            "You are a helpful assistant. "
            "Always call get_weather before answering weather questions. "
            "Always call search_latest_information for latest, current, recent, news, or date-dependent questions."
        ),
    )

    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]}
    )

    print(result["messages"][-1].content_blocks)


if __name__ == "__main__":
    main()
