# LLM Context Window Basics

This folder keeps the idea very simple.

An LLM context window is the text/messages sent to the model in one request.

The LLM does not remember previous API calls by itself. If you say:

```text
Hi, I am Chetan.
```

and later ask:

```text
What is my name?
```

the application must send the earlier message again. That message history is the context window.

## Examples

### 1. Smallest Demo

```powershell
uv run python agents-context/01_simple_context_window.py
```

This shows:

- First call: `Hi, I am Chetan.`
- Second call: `What is my name?`
- The script sends previous messages again, so the LLM can answer.

### 2. Real Application Style

```powershell
uv run python agents-context/02_realtime_chat_session.py
```

This shows the real project pattern:

- user opens a chat session
- backend stores messages for that session
- every new question loads previous messages
- backend sends recent message history to the LLM
- backend saves the assistant reply

In production, `ChatSessionStore` is usually Redis, Postgres, Cosmos DB, or another database.

### 3. Streamlit UI

```powershell
uv run streamlit run agents-context/03_streamlit_context_app.py
```

This opens a small browser app where you can see:

- chat messages in the current session
- the exact context window sent to the LLM
- each response
- input, output, and total tokens returned by the provider
- `New Chat`, which starts a fresh session id
- `Reset Context`, which clears the current session history

## .env

```text
MESH_API_KEY=...
MESH_API_URL=...
MESH_MODEL=...
MESH_TEMPERATURE=0.2
MESH_TIMEOUT_SECONDS=60
```

## Key Idea

Memory in an LLM app is not magic. It is usually just stored messages that your application sends back to the LLM.

Simple formula:

```text
LLM answer = system prompt + previous messages + latest user question
```
