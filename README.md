# Agentic Practice Workspace

This repository is a hands-on learning workspace for Python agent patterns. It
contains small runnable examples for Mesh-backed LLM calls, LangChain agents,
context windows, Pydantic validation, RAG parsing, and a Deep Agents based test
script generator.

Most examples are intentionally simple and meant to be run from the project
root with `uv`.

## Quick Start

Install or sync dependencies:

```powershell
uv sync
```

Run the basic LangChain agent:

```powershell
uv run python basic_agent.py
```

Ask your own question:

```powershell
uv run python basic_agent.py "What's the weather in Mumbai?"
```

Run an example that does not need an LLM:

```powershell
uv run python pydantic-1/01_base_model.py
uv run python rag/01_pdf_loader_splitter_fixed.py
uv run python deepagents/test-script-generator/test_script_generator.py --sample --dry-run
```

## Environment

The project uses Python `3.14` through `.python-version` and `pyproject.toml`.

LLM-backed examples load Mesh API settings from the repo-root `.env` file:

```env
MESH_API_KEY=...
MESH_API_URL=...
MESH_MODEL=...
MESH_TEMPERATURE=0.2
MESH_TIMEOUT_SECONDS=60
```

The basic agent can also search current information. For best results, add:

```env
TAVILY_API_KEY=your-tavily-key
```

If `TAVILY_API_KEY` is not set, `basic_agent.py` falls back to Wikipedia search.
The `.env` file is ignored by git.

## Workspace Map

| Path | Purpose | Main Commands |
| --- | --- | --- |
| `basic_agent.py` | One-file LangChain `create_agent` example with weather and search tools. | `uv run python basic_agent.py` |
| `4-agents/` | Chat Completions basics, manual tool calling, LangChain agent tool calling, and terminal chatbot examples. | `uv run python 4-agents/01_chat_completion_api_metadata.py` |
| `agents-context/` | Context-window and chat-session lessons, including a Streamlit UI that shows messages, context sent to the LLM, responses, and tokens. | `uv run streamlit run agents-context/03_streamlit_context_app.py` |
| `pydantic-1/` | Step-by-step Pydantic examples, from plain classes to a LangChain tool with a Pydantic `args_schema`. | `uv run python pydantic-1/08_langchain_agent_with_pydantic.py` |
| `rag/` | RAG parsing practice with notebooks, document-loader notes, PDFs, DOCX, CSV, JSON, HTML, Markdown, and Excel sample data. | `uv run python rag/01_pdf_loader_splitter_fixed.py` |
| `deepagents/` | Deep Agents practice project that converts test cases into Java TestNG Maven automation starters with security, clarity, category, validation, HITL, and local PR-draft steps. | `uv run python deepagents/test-script-generator/test_script_generator.py --sample --dry-run` |
| `pythonbasics.py` | Tiny Python typing scratch file. | `uv run python pythonbasics.py` |
| `test.ipynb` | Empty placeholder notebook. | Open in Jupyter or VS Code if needed. |

## Learning Paths

### 1. Basic LangChain Agent

`basic_agent.py` demonstrates the smallest useful agent shape:

1. Load Mesh model settings from `.env`.
2. Define Python tools.
3. Create a LangChain agent with `create_agent`.
4. Invoke the agent with a user message.
5. Print the final response.

Run:

```powershell
uv run python basic_agent.py
uv run python basic_agent.py "What is the latest news about LangChain?"
```

Tools included:

- `get_weather(city)` returns a simple demo weather response.
- `search_latest_information(query)` uses Tavily when configured, otherwise
  Wikipedia.

### 2. Chat Completions And Agents

The `4-agents/` folder starts from raw model calls and builds toward agent
behavior.

```powershell
uv run python 4-agents/01_chat_completion_api_metadata.py
uv run python 4-agents/02_chat_completion_with_tools_manual.py
uv run python 4-agents/03_langchain_agent_with_tools.py
uv run python 4-agents/04_conversational_chatbot.py
```

Use this folder to compare:

- raw Chat Completions API calls
- manual tool-call loops
- LangChain-managed tool execution
- a simple terminal chatbot with message history

See `4-agents/README.md` for the detailed comparison table.

### 3. Context Windows And Memory

The `agents-context/` folder explains that an LLM only sees what the application
sends in the current request. The examples show how previous messages become the
context window.

```powershell
uv run python agents-context/01_simple_context_window.py
uv run python agents-context/02_realtime_chat_session.py
uv run streamlit run agents-context/03_streamlit_context_app.py
```

The Streamlit app is the most visual example. It shows:

- current chat messages
- exact context window sent to the LLM
- assistant responses
- input, output, and total token usage
- `New Chat` and `Reset Context` controls

See `agents-context/README.md` for the focused lesson.

### 4. Pydantic Basics

The `pydantic-1/` folder is a progressive learning track.

```powershell
uv run python pydantic-1/00_plain_class_vs_pydantic.py
uv run python pydantic-1/01_base_model.py
uv run python pydantic-1/02_annotated_fields.py
uv run python pydantic-1/03_field_validator.py
uv run python pydantic-1/04_model_validator.py
uv run python pydantic-1/05_computed_field.py
uv run python pydantic-1/06_nested_models.py
uv run python pydantic-1/07_dataclass.py
uv run python pydantic-1/08_langchain_agent_with_pydantic.py
```

Files `00` through `07` are local Pydantic examples. File `08` combines
Pydantic with a LangChain agent and needs Mesh API settings in `.env`.

See `pydantic-1/README.md` for the full learning order and concept notes.

### 5. RAG And Data Parsing

The `rag/` folder focuses on loading and splitting source documents before a
full retrieval pipeline.

Run the clean PDF loader and splitter example:

```powershell
uv run python rag/01_pdf_loader_splitter_fixed.py
```

Useful RAG assets:

- `rag/data_parsing_part1_langchain_data_loaders.ipynb` explores LangChain
  document loaders.
- `rag/parsing.ipynb` is a tiny notebook smoke test.
- `rag/data_parsing_part2.ipynb` and `rag/rag_example1.ipynb` are empty
  placeholders.
- `rag/data/` contains sample text, PDF, DOCX, CSV, JSON, HTML, Markdown, and
  Excel files for loader practice.
- `rag/data/langchain_document_loaders.md` explains loader categories and the
  common `Document(page_content, metadata)` shape.

### 6. Deep Agents Test Script Generator

The `deepagents/` folder is a larger practice project. It turns test cases into
Java TestNG Maven automation starter projects.

Run deterministic logic without calling an LLM:

```powershell
uv run python deepagents/test-script-generator/test_script_generator.py --sample --dry-run
```

Create the local PR draft in dry-run mode:

```powershell
uv run python deepagents/test-script-generator/test_script_generator.py --sample --dry-run --auto-approve
```

Check the blocked-credentials path:

```powershell
uv run python deepagents/test-script-generator/test_script_generator.py --input-file deepagents/test-script-generator/sample-testcases/login-with-credentials-blocked.md --dry-run
```

Run the Mesh-backed Deep Agent flow:

```powershell
uv run python deepagents/test-script-generator/test_script_generator.py --sample
```

The generator includes:

- security preflight for credentials, tokens, and possible user identifiers
- clarity checks and clarification questions
- web/API/database classification
- local automation standards
- Java TestNG Maven project generation
- static validation and optional Maven compile validation
- human-in-the-loop review packet
- local PR description draft

Generated projects are stored under `deepagents/generated-tests/`. One generated
API example is already checked in with its `README.md`, `HITL_REVIEW.md`,
`PR_DESCRIPTION.md`, `pom.xml`, and Java test source.

See `deepagents/README.md` for the full workflow diagram and production gaps.

## Files That Are Local Or Tooling

- `.env` contains local credentials and is ignored by git.
- `.venv/`, `__pycache__/`, `.pytest_cache/`, and `.ruff_cache/` are ignored
  runtime/tooling folders.
- `.agents/` and `.codex/` are local assistant/tooling folders in this
  workspace, not application source code.

## Suggested Order For Learning

1. Run `pydantic-1/00_plain_class_vs_pydantic.py` through
   `pydantic-1/07_dataclass.py`.
2. Run `4-agents/01_chat_completion_api_metadata.py` to see the raw LLM call and
   token metadata.
3. Run `4-agents/02_chat_completion_with_tools_manual.py`, then
   `4-agents/03_langchain_agent_with_tools.py`.
4. Run `agents-context/01_simple_context_window.py`, then the Streamlit context
   UI.
5. Run `basic_agent.py` and try weather plus latest-information questions.
6. Explore `rag/01_pdf_loader_splitter_fixed.py` and the RAG notebooks.
7. Run the Deep Agents generator in `--dry-run` mode before using the real LLM
   flow.

## Notes

- Run commands from the repository root: `D:\AI\Agentic-Practise`.
- Many LLM examples print token usage or response metadata so you can see what
  was sent and returned.
- The Deep Agents dry-run path is useful when you want to understand the
  workflow mechanics without spending LLM calls.
- Maven is optional for the Deep Agents generated Java projects. If Maven is not
  on `PATH`, static validation still runs.
