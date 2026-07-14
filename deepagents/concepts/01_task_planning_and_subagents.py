"""Concept 1: task planning and subagents in Deep Agents.

Dry-run:
    uv run python deepagents/concepts/01_task_planning_and_subagents.py

Real Mesh-backed run:
    uv run python deepagents/concepts/01_task_planning_and_subagents.py --real

Learning goal:
    Deep Agents add built-in planning and delegation on top of the normal tool
    calling loop. The parent agent can use `write_todos` to track work and the
    `task` tool to launch a focused subagent with its own context window.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


REPO_ROOT = Path(__file__).resolve().parents[2]
STANDARDS_DIR = REPO_ROOT / "deepagents" / "automation-standards"
SAMPLE_TEST_CASE = (
    REPO_ROOT
    / "deepagents"
    / "test-script-generator"
    / "sample-testcases"
    / "order-status-api.md"
)


def build_mesh_model() -> ChatOpenAI:
    """Create a Mesh-backed chat model from the repo-root .env file."""

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


def read_sample_test_case() -> str:
    """Read the sample API test case used by this learning demo."""

    return SAMPLE_TEST_CASE.read_text(encoding="utf-8")


def read_automation_standard(category: str) -> str:
    """Read local automation standards for api, web, or database tests."""

    normalized = category.strip().lower()
    if normalized not in {"api", "web", "database"}:
        return "Unknown category. Use one of: api, web, database."
    return (STANDARDS_DIR / f"{normalized}-tests.md").read_text(encoding="utf-8")


def summarize_result(result: dict[str, Any]) -> str:
    """Return the final assistant message in a display-friendly form."""

    messages = result.get("messages", [])
    if not messages:
        return str(result)
    final_message = messages[-1]
    content = getattr(final_message, "content", None)
    if isinstance(content, str):
        return content
    blocks = getattr(final_message, "content_blocks", None)
    return str(blocks if blocks is not None else final_message)


def print_dry_run_lesson() -> None:
    print("# Concept 1: Task Planning And Subagents\n")
    print("Deep Agents include two useful built-in tools:")
    print("- write_todos: maintain a task list in agent state.")
    print("- task: launch a short-lived subagent for isolated work.\n")
    print("In this example, the parent agent should:")
    print("1. Use write_todos to plan the review.")
    print("2. Read the sample test case.")
    print("3. Delegate standards comparison to the standards-reviewer subagent.")
    print("4. Combine the subagent report into a final answer.\n")
    print("Run with --real to let the Mesh-backed Deep Agent perform the flow.")


def run_real_agent() -> None:
    model = build_mesh_model()
    subagents = [
        {
            "name": "standards-reviewer",
            "description": (
                "Reviews test cases against the local automation standards and "
                "returns a concise gap report."
            ),
            "system_prompt": (
                "You are a focused automation standards reviewer. Read the test "
                "case and the relevant standards. Return only a short report with "
                "strengths, gaps, and recommended next actions."
            ),
            "tools": [read_sample_test_case, read_automation_standard],
        }
    ]

    agent = create_deep_agent(
        model=model,
        tools=[read_sample_test_case, read_automation_standard],
        subagents=subagents,
        system_prompt=(
            "You are teaching Deep Agents concepts. For this run, explicitly "
            "demonstrate planning and delegation. First use write_todos to plan. "
            "Then read the sample test case. Then call the task tool with "
            "subagent_type='standards-reviewer' to compare the API test case "
            "against the API automation standard. Finish with a compact lesson "
            "that explains what the parent did versus what the subagent did."
        ),
    )

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Teach me how Deep Agents use task planning and "
                        "subagents by reviewing the sample order status API "
                        "test case."
                    ),
                }
            ]
        }
    )
    print(summarize_result(result))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Teach Deep Agents task planning and subagent delegation."
    )
    parser.add_argument(
        "--real",
        action="store_true",
        help="Call the Mesh-backed Deep Agent. Default is a no-LLM dry run.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.real:
        run_real_agent()
    else:
        print_dry_run_lesson()


if __name__ == "__main__":
    main()
