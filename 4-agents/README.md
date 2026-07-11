# Agents Basics

This folder starts with a simple Chat Completions API example because agents are
built on top of LLM calls.

Run:

```powershell
uv run python 4-agents\01_chat_completion_api_metadata.py
```

## Chat Completions API Vs Agent

| Topic | Chat Completions API | Agent |
| --- | --- | --- |
| Main idea | Send messages to an LLM and get one response back. | Build an application loop around the LLM. |
| Who decides next step? | Your code decides before calling the model. | The agent can decide whether to answer, call a tool, ask for clarification, or continue. |
| State/context | You must pass message history each time. | The agent can manage state, memory, checkpoints, and intermediate steps. |
| Tools | Possible, but your app must orchestrate tool calls. | Tool use is a core pattern: search, files, APIs, validation, PR creation, etc. |
| Validation | Your app validates after the response. | The agent workflow can include validation stages. |
| HITL | Your app must pause and ask the human. | Agent workflows can include human approval stages. |
| Best for | Simple Q&A, summaries, extraction, one-shot generation. | Multi-step tasks with decisions, tools, memory, and approval gates. |

## What This Example Shows

`01_chat_completion_api_metadata.py` is **not a full agent**. It is the raw LLM
call that an agent may use internally.

It prints:

- the input messages sent to the model
- the assistant response content
- input tokens
- output tokens
- total tokens
- common metadata
- the full raw response metadata

## Simple Mental Model

```text
Chat Completions API:
    messages -> LLM -> response

Agent:
    user goal -> plan/decide -> LLM -> tool calls -> validation -> memory/HITL -> final result
```

So the Chat Completions API is the engine call. The agent is the larger workflow
that uses the engine call plus tools, state, policies, and decisions.
