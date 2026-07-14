# Deep Agents Concepts Mini Lab

This folder adds two small examples based on the LangChain Deep Agents
overview. They are designed for learning, so each script defaults to a dry-run
mode that explains the concept without calling an LLM.

Run the examples from the repo root.

## Concept 1: Task Planning And Subagents

Deep Agents include two delegation helpers by default:

- `write_todos` for keeping a structured task list while the agent works.
- `task` for launching a short-lived subagent with an isolated context window.

Run the dry-run lesson:

```powershell
uv run python deepagents/concepts/01_task_planning_and_subagents.py
```

Run the real Mesh-backed Deep Agent:

```powershell
uv run python deepagents/concepts/01_task_planning_and_subagents.py --real
```

What to watch:

- The main agent should make a small plan.
- The main agent should delegate standards review to the `standards-reviewer`
  subagent.
- The subagent should return one final report to the parent.
- The parent should combine that report with its own final answer.

## Concept 2: Virtual Filesystem And Permissions

Deep Agents also include a virtual filesystem. The model can use tools such as
`ls`, `read_file`, `write_file`, `edit_file`, `glob`, and `grep`. The default
`StateBackend` keeps files in the agent state for that run.

This example also shows permission rules:

- writes under `/workspace/**` are allowed
- reads under `/secrets/**` are denied
- writes under `/protected/**` are denied

Run the dry-run lesson:

```powershell
uv run python deepagents/concepts/02_virtual_filesystem_permissions.py
```

Run the real Mesh-backed Deep Agent:

```powershell
uv run python deepagents/concepts/02_virtual_filesystem_permissions.py --real
```

What to watch:

- The agent reads a file from the virtual `/workspace`.
- The agent writes a safe summary file under `/workspace`.
- The agent intentionally tries one denied read under `/secrets`.
- The agent intentionally tries one denied write under `/protected`.

## Required `.env` For `--real`

```env
MESH_API_KEY=...
MESH_API_URL=...
MESH_MODEL=...
MESH_TEMPERATURE=0.2
MESH_TIMEOUT_SECONDS=60
```

## Why These Two Concepts Matter

Use planning and subagents when one request has multiple independent pieces of
work. The parent stays focused on orchestration while each subagent gets a clean
context window.

Use the virtual filesystem when an agent needs working files, scratch reports,
or intermediate artifacts. Add permissions when some paths should be read-only,
write-only, or blocked from the model.
