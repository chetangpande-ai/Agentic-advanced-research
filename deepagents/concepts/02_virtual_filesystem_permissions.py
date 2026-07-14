"""Concept 2: virtual filesystem and permissions in Deep Agents.

Dry-run:
    uv run python deepagents/concepts/02_virtual_filesystem_permissions.py

Real Mesh-backed run:
    uv run python deepagents/concepts/02_virtual_filesystem_permissions.py --real

Learning goal:
    Deep Agents include virtual filesystem tools such as `ls`, `read_file`,
    `write_file`, `edit_file`, `glob`, and `grep`. Permissions let you decide
    which virtual paths the agent may read or write.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any

from deepagents import FilesystemPermission, create_deep_agent
from deepagents.backends import StateBackend
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


REPO_ROOT = Path(__file__).resolve().parents[2]


INITIAL_FILES = {
    "/workspace/source-test-case.md": {
        "content": """# Test Case: Password Reset API

Scenario:
Verify that the password reset endpoint accepts a valid reset request.

Steps:
1. Send POST `/password-reset` with a synthetic user email.
2. Verify the response status code is `202`.
3. Verify the response contains a tracking ID.

Expected result:
The request is accepted without exposing whether the email exists.
""",
        "encoding": "utf-8",
    },
    "/protected/approval-policy.md": {
        "content": "Only a human reviewer may change approval policy files.",
        "encoding": "utf-8",
    },
    "/secrets/token.txt": {
        "content": "demo-secret-token-this-path-should-not-be-readable",
        "encoding": "utf-8",
    },
}


PERMISSIONS = [
    FilesystemPermission(
        operations=["write"],
        paths=["/workspace/**"],
        mode="allow",
    ),
    FilesystemPermission(
        operations=["read"],
        paths=["/secrets/**"],
        mode="deny",
    ),
    FilesystemPermission(
        operations=["write"],
        paths=["/protected/**"],
        mode="deny",
    ),
]


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


def summarize_result(result: dict[str, Any]) -> str:
    """Return final answer plus visible virtual files from the run."""

    messages = result.get("messages", [])
    final = str(messages[-1].content if messages else result)
    files = result.get("files", {})
    file_lines = ["\n\nVirtual files after the run:"]
    for path in sorted(files):
        content = files[path].get("content", "")
        if isinstance(content, list):
            content = "\n".join(str(line) for line in content)
        preview = str(content).replace("\n", " ")[:100]
        file_lines.append(f"- {path}: {preview}")
    return final + "\n".join(file_lines)


def print_dry_run_lesson() -> None:
    print("# Concept 2: Virtual Filesystem And Permissions\n")
    print("Deep Agents can work with a virtual filesystem.")
    print("In this demo the initial virtual files are:")
    for path in sorted(INITIAL_FILES):
        print(f"- {path}")

    print("\nPermission rules:")
    for permission in PERMISSIONS:
        operations = ", ".join(permission.operations)
        paths = ", ".join(permission.paths)
        print(f"- {permission.mode.upper()} {operations} on {paths}")

    print("\nExpected real run:")
    print("1. Agent lists and reads /workspace/source-test-case.md.")
    print("2. Agent writes /workspace/review-summary.md.")
    print("3. Agent tries to read /secrets/token.txt and receives a denial.")
    print("4. Agent tries to write under /protected and receives a denial.\n")
    print("Run with --real to let the Mesh-backed Deep Agent perform the flow.")


def run_real_agent() -> None:
    agent = create_deep_agent(
        model=build_mesh_model(),
        tools=[],
        backend=StateBackend(),
        permissions=PERMISSIONS,
        system_prompt=(
            "You are teaching Deep Agents virtual filesystem behavior. Use the "
            "built-in filesystem tools. First list /workspace, then read "
            "/workspace/source-test-case.md. Write a short review summary to "
            "/workspace/review-summary.md. Then intentionally attempt to read "
            "/secrets/token.txt and intentionally attempt one write to "
            "/protected/agent-note.md so the learner can see both permission "
            "denials. Finish by explaining which operations succeeded and which "
            "operations were blocked. Never invent or reveal secret content."
        ),
    )

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Demonstrate the Deep Agents virtual filesystem and "
                        "permission boundary using the provided files."
                    ),
                }
            ],
            "files": INITIAL_FILES,
        }
    )
    print(summarize_result(result))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Teach Deep Agents virtual filesystem and permissions."
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
