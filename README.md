# Basic LangChain Agent

One-file LangChain agent using your Mesh API LLM from `.env`.

It has two tools:

- `get_weather(city)` for the quickstart weather example
- `search_latest_information(query)` for latest/current information using Tavily, with Wikipedia fallback

Run the default question:

```powershell
uv run python basic_agent.py
```

Ask your own question:

```powershell
uv run python basic_agent.py "What's the weather in Mumbai?"
```

Ask for latest information:

```powershell
uv run python basic_agent.py "What is the latest news about LangChain?"
```

For best latest-information results, add this to `.env`:

```env
TAVILY_API_KEY=your-tavily-key
```

If `TAVILY_API_KEY` is not set, the tool uses Wikipedia search instead.

The full agent code is in `basic_agent.py`.
