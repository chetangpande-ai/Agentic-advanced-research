"""Deep Agents practice script for Java TestNG Maven automation generation.

Run without an LLM first:
    uv run python deepagents\test-script-generator\test_script_generator.py --sample --dry-run

Run with Deep Agents and Mesh LLM from .env:
    uv run python deepagents\test-script-generator\test_script_generator.py --sample
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from deepagents import create_deep_agent


SCRIPT_DIR = Path(__file__).resolve().parent
DEEPAGENTS_ROOT = SCRIPT_DIR.parent
WORKSPACE_ROOT = DEEPAGENTS_ROOT.parent
STANDARDS_DIR = DEEPAGENTS_ROOT / "automation-standards"
GENERATED_ROOT = DEEPAGENTS_ROOT / "generated-tests"
SAMPLE_FILE = SCRIPT_DIR / "sample-testcases" / "order-status-api.md"

LAST_PROJECT_DIR: Path | None = None
LAST_VALIDATION: dict[str, Any] = {}
LAST_CLARITY: dict[str, Any] = {}
LAST_CATEGORY: dict[str, Any] = {}
LAST_SECURITY: dict[str, Any] = {}

SECRET_LABEL_RE = re.compile(
    r"\b(password|passwd|pwd|secret|client[_ -]?secret|api[_ -]?key|token|"
    r"access[_ -]?token|refresh[_ -]?token|authorization|bearer|connection[_ -]?string)\b"
    r"\s*[:=]\s*['\"]?([^'\"\s,;]+)",
    re.IGNORECASE,
)
USERNAME_LABEL_RE = re.compile(
    r"\b(username|user name|login|user id|userid|email)\b\s*[:=]\s*['\"]?([^'\"\s,;]+)",
    re.IGNORECASE,
)
BEARER_TOKEN_RE = re.compile(
    r"\bBearer\s+(?!token\b|authorization\b|header\b)[A-Za-z0-9._\-~+/=]{12,}",
    re.IGNORECASE,
)
JWT_RE = re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b")
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")


def log_step(step: int, message: str) -> None:
    print(f"[STEP {step:02d}] {message}")


def build_mesh_model() -> ChatOpenAI:
    """Create a LangChain chat model using Mesh API settings from .env."""

    load_dotenv(WORKSPACE_ROOT / ".env")

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


def scan_sensitive_test_data(testcases: str) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []

    for line_number, line in enumerate(testcases.splitlines(), start=1):
        for match in SECRET_LABEL_RE.finditer(line):
            label = match.group(1)
            value = match.group(2)
            findings.append(
                {
                    "line": line_number,
                    "type": normalize_finding_type(label),
                    "severity": "high",
                    "label": label,
                    "redacted_value": redact_value(value),
                    "recommendation": (
                        "Remove the literal secret. Use a placeholder such as "
                        "${TEST_PASSWORD}, ${API_TOKEN}, or a secure test-data reference."
                    ),
                }
            )

        for match in USERNAME_LABEL_RE.finditer(line):
            label = match.group(1)
            value = match.group(2)
            findings.append(
                {
                    "line": line_number,
                    "type": "credential_identifier",
                    "severity": "medium",
                    "label": label,
                    "redacted_value": redact_value(value),
                    "recommendation": (
                        "Prefer a synthetic test user alias or an environment placeholder "
                        "instead of a real user/account identifier."
                    ),
                }
            )

        for match in BEARER_TOKEN_RE.finditer(line):
            findings.append(
                {
                    "line": line_number,
                    "type": "bearer_token",
                    "severity": "high",
                    "label": "Bearer",
                    "redacted_value": redact_value(match.group(0)),
                    "recommendation": "Do not place bearer tokens in test cases. Use a secure token provider.",
                }
            )

        for match in JWT_RE.finditer(line):
            findings.append(
                {
                    "line": line_number,
                    "type": "jwt_token",
                    "severity": "high",
                    "label": "jwt",
                    "redacted_value": redact_value(match.group(0)),
                    "recommendation": "Do not place JWT values in test cases. Use a secure token provider.",
                }
            )

        for match in EMAIL_RE.finditer(line):
            redacted = redact_value(match.group(0))
            already_reported = any(
                item["line"] == line_number and item["redacted_value"] == redacted
                for item in findings
            )
            if not already_reported:
                findings.append(
                    {
                        "line": line_number,
                        "type": "possible_user_identifier",
                        "severity": "medium",
                        "label": "email",
                        "redacted_value": redacted,
                        "recommendation": (
                            "Confirm this is a synthetic test account. Use an alias or placeholder "
                            "when the account belongs to a real user."
                        ),
                    }
                )

    high_risk = [item for item in findings if item["severity"] == "high"]
    medium_risk = [item for item in findings if item["severity"] == "medium"]
    status = "blocked" if high_risk else "review_required" if medium_risk else "passed"
    return {
        "status": status,
        "block_generation": bool(high_risk),
        "finding_count": len(findings),
        "high_risk_count": len(high_risk),
        "medium_risk_count": len(medium_risk),
        "findings": findings,
        "policy": (
            "High-risk secrets block LLM/code generation. Medium-risk user identifiers "
            "are flagged for HITL review."
        ),
    }


def normalize_finding_type(label: str) -> str:
    clean = re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")
    if "password" in clean or clean in {"passwd", "pwd"}:
        return "password"
    if "token" in clean or clean in {"authorization", "bearer"}:
        return "token"
    if "key" in clean:
        return "api_key"
    if "connection" in clean:
        return "connection_string"
    return clean or "secret"


def redact_value(value: str) -> str:
    clean = value.strip().strip(".,;:)]}")
    if not clean:
        return "<empty>"
    if len(clean) <= 4:
        return "*" * len(clean)
    return clean[:2] + "*" * max(4, len(clean) - 4) + clean[-2:]


def analyze_clarity(testcases: str) -> dict[str, Any]:
    normalized = testcases.strip()
    lower = normalized.lower()
    questions: list[str] = []
    signals: list[str] = []

    if len(normalized) < 120:
        questions.append("Please provide more detailed steps, preconditions, and expected results.")
        signals.append("input_is_short")

    has_steps = bool(re.search(r"(^|\n)\s*(steps?|actions?)\s*:", lower)) or bool(
        re.search(r"(^|\n)\s*\d+\.", normalized)
    )
    if not has_steps:
        questions.append("What exact user or system actions should the automated test perform?")
        signals.append("missing_steps")

    expected_words = [
        "expected",
        "verify",
        "assert",
        "status code",
        "response contains",
        "should display",
        "should be displayed",
    ]
    if not any(word in lower for word in expected_words):
        questions.append("What specific expected result should be asserted?")
        signals.append("missing_expected_result")

    ambiguous_words = [
        "proper",
        "correct",
        "valid data",
        "invalid data",
        "various",
        "multiple",
        "several",
        "as required",
        "etc",
        "tbd",
        "fast",
        "slow",
    ]
    found_ambiguous = [word for word in ambiguous_words if word in lower]
    if found_ambiguous:
        questions.append(
            "Please replace ambiguous terms with exact values, inputs, messages, or thresholds: "
            + ", ".join(found_ambiguous)
        )
        signals.append("ambiguous_terms")

    needs_data = any(word in lower for word in ["login", "api", "database", "db", "order", "customer"])
    has_data = bool(re.search(r"`[^`]+`|[A-Z]{2,}-\d+|https?://|/[\w/{-]+", normalized))
    if needs_data and not has_data:
        questions.append("What concrete test data, endpoint, URL, user, record, or ID should be used?")
        signals.append("missing_test_data")

    status = "needs_clarification" if questions else "clear"
    return {
        "status": status,
        "ready_for_generation": status == "clear",
        "signals": signals,
        "questions": questions,
    }


def detect_category(testcases: str) -> dict[str, Any]:
    lower = testcases.lower()
    keyword_map = {
        "web": [
            "browser",
            "page",
            "ui",
            "login",
            "button",
            "field",
            "screen",
            "selenium",
            "xpath",
            "css selector",
            "click",
        ],
        "api": [
            "api",
            "endpoint",
            "request",
            "response",
            "status code",
            "json",
            "header",
            "payload",
            "get ",
            "post ",
            "put ",
            "delete ",
        ],
        "database": [
            "database",
            "db",
            "sql",
            "query",
            "table",
            "record",
            "jdbc",
            "stored procedure",
            "row",
            "column",
        ],
    }
    scores = {
        category: sum(1 for keyword in keywords if keyword in lower)
        for category, keywords in keyword_map.items()
    }
    primary = max(scores, key=lambda item: scores[item])
    if scores[primary] == 0:
        primary = "api"
    web_vs_non_web = "web" if primary == "web" else "non-web"
    return {
        "web_vs_non_web": web_vs_non_web,
        "primary_category": primary,
        "scores": scores,
        "standards_file": f"{primary}-tests.md",
    }


def normalize_category(raw_category: str) -> str:
    raw = raw_category.strip().lower()
    try:
        parsed = json.loads(raw_category)
        raw = str(parsed.get("primary_category", raw)).lower()
    except json.JSONDecodeError:
        pass

    if "web" in raw:
        return "web"
    if "database" in raw or "db" in raw or "sql" in raw:
        return "database"
    return "api"


@tool
def scan_for_sensitive_test_data(testcases: str) -> str:
    """Flag credentials, secrets, tokens, and user identifiers in test case input."""

    global LAST_SECURITY
    LAST_SECURITY = scan_sensitive_test_data(testcases)
    return json.dumps(LAST_SECURITY, indent=2)


@tool
def check_testcase_clarity(testcases: str) -> str:
    """Check whether the input test cases are clear enough to automate."""

    global LAST_CLARITY
    LAST_CLARITY = analyze_clarity(testcases)
    return json.dumps(LAST_CLARITY, indent=2)


@tool
def classify_test_category(testcases: str) -> str:
    """Classify test cases as web or non-web, with API/database implementation detail."""

    global LAST_CATEGORY
    LAST_CATEGORY = detect_category(testcases)
    return json.dumps(LAST_CATEGORY, indent=2)


@tool
def read_automation_standards(category: str) -> str:
    """Read local automation standards for api, web, or database tests."""

    normalized = normalize_category(category)
    path = STANDARDS_DIR / f"{normalized}-tests.md"
    if not path.exists():
        raise FileNotFoundError(f"Standards file not found: {path}")
    return path.read_text(encoding="utf-8")


@tool
def write_java_testng_maven_project(testcases: str, category: str) -> str:
    """Write a Java TestNG Maven project for the provided test cases and category."""

    global LAST_PROJECT_DIR
    normalized = normalize_category(category)
    GENERATED_ROOT.mkdir(parents=True, exist_ok=True)

    slug = make_slug(first_meaningful_line(testcases) or f"{normalized}-generated-test")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    project_dir = GENERATED_ROOT / f"{slug}-{timestamp}"
    package_dir = project_dir / "src" / "test" / "java" / "com" / "example" / "generated"
    resource_dir = project_dir / "src" / "test" / "resources" / "test-data"
    package_dir.mkdir(parents=True, exist_ok=True)
    resource_dir.mkdir(parents=True, exist_ok=True)

    class_name = make_class_name(slug, normalized)
    (project_dir / "pom.xml").write_text(build_pom_xml(normalized), encoding="utf-8")
    (package_dir / f"{class_name}.java").write_text(
        build_java_test_source(normalized, class_name),
        encoding="utf-8",
    )
    (resource_dir / "README.md").write_text(
        "# Test Data\n\nKeep environment-specific data outside Java source files.\n",
        encoding="utf-8",
    )
    (project_dir / "README.md").write_text(
        build_generated_project_readme(testcases, normalized, class_name),
        encoding="utf-8",
    )

    LAST_PROJECT_DIR = project_dir
    return json.dumps(
        {
            "project_dir": str(project_dir),
            "category": normalized,
            "java_test_class": f"src/test/java/com/example/generated/{class_name}.java",
            "next_command": "mvn -q -DskipTests test-compile",
        },
        indent=2,
    )


@tool
def validate_generated_project(project_dir: str) -> str:
    """Compile with Maven when available, and always run static validation checks."""

    global LAST_VALIDATION
    path = resolve_generated_project(project_dir)
    static_result = static_validate_project(path)
    mvn = shutil.which("mvn.cmd") or shutil.which("mvn")

    if mvn:
        try:
            completed = subprocess.run(
                [mvn, "-q", "-DskipTests", "test-compile"],
                cwd=path,
                text=True,
                capture_output=True,
                timeout=180,
                check=False,
            )
            compile_result = {
                "status": "passed" if completed.returncode == 0 else "failed",
                "returncode": completed.returncode,
                "stdout": completed.stdout[-3000:],
                "stderr": completed.stderr[-3000:],
                "command": "mvn -q -DskipTests test-compile",
            }
        except subprocess.TimeoutExpired as exc:
            compile_result = {
                "status": "failed",
                "returncode": None,
                "stdout": (exc.stdout or "")[-3000:] if isinstance(exc.stdout, str) else "",
                "stderr": "Maven validation timed out after 180 seconds.",
                "command": "mvn -q -DskipTests test-compile",
            }
    else:
        compile_result = {
            "status": "skipped",
            "reason": "Maven was not found on PATH. Static validation still ran.",
            "command": "mvn -q -DskipTests test-compile",
        }

    LAST_VALIDATION = {
        "project_dir": str(path),
        "static_validation": static_result,
        "compile_validation": compile_result,
    }
    return json.dumps(LAST_VALIDATION, indent=2)


@tool
def prepare_human_review_packet(project_dir: str) -> str:
    """Create a human-in-the-loop review checklist before PR drafting."""

    path = resolve_generated_project(project_dir)
    review = build_hitl_review(path)
    review_path = path / "HITL_REVIEW.md"
    review_path.write_text(review, encoding="utf-8")
    return json.dumps(
        {
            "status": "human_review_required",
            "review_file": str(review_path),
            "message": "Review this file before approving PR draft creation.",
        },
        indent=2,
    )


@tool
def draft_pull_request(project_dir: str, title: str) -> str:
    """Draft a local pull request package after human approval."""

    path = resolve_generated_project(project_dir)
    pr_body = build_pr_description(path, title)
    pr_path = path / "PR_DESCRIPTION.md"
    pr_path.write_text(pr_body, encoding="utf-8")
    return json.dumps(
        {
            "status": "local_pr_draft_created",
            "pr_description": str(pr_path),
            "note": "No remote PR was pushed. Use the commands in PR_DESCRIPTION.md when ready.",
        },
        indent=2,
    )


def build_deep_agent(include_pr_tool: bool = False):
    tools = [
        scan_for_sensitive_test_data,
        check_testcase_clarity,
        classify_test_category,
        read_automation_standards,
        write_java_testng_maven_project,
        validate_generated_project,
        prepare_human_review_packet,
    ]
    if include_pr_tool:
        tools.append(draft_pull_request)

    return create_deep_agent(
        model=build_mesh_model(),
        tools=tools,
        system_prompt=build_system_prompt(include_pr_tool=include_pr_tool),
    )


def build_system_prompt(include_pr_tool: bool) -> str:
    if include_pr_tool:
        return (
            "You are a PR drafting assistant for generated Java TestNG Maven tests. "
            "A human has already approved the HITL review. Call draft_pull_request exactly once "
            "using the provided project_dir and title, then summarize the created file."
        )

    return textwrap.dedent(
        """
        You are a senior test automation architect using LangChain Deep Agents.
        Your job is to convert supplied test cases into a Java TestNG Maven
        automation starter.

        Follow this exact order:
        1. Call scan_for_sensitive_test_data.
        2. If the status is blocked, stop and ask the user to remove literal credentials or secrets.
        3. Call check_testcase_clarity.
        4. If the status is needs_clarification, stop and ask the returned questions.
        5. Call classify_test_category.
        6. Call read_automation_standards for the primary category.
        7. Call write_java_testng_maven_project.
        8. Call validate_generated_project.
        9. Call prepare_human_review_packet.

        Do not draft a pull request yet. PR drafting happens only after the CLI
        receives explicit human approval.

        Keep the final answer concise and include the generated project path,
        validation status, HITL review path, and any clarification questions.
        """
    ).strip()


def run_dry_run(testcases: str, auto_approve: bool) -> None:
    log_step(1, "Run security preflight before LLM or code generation")
    security = run_security_preflight(testcases)
    if security["block_generation"]:
        return

    log_step(2, "Check whether the test case is clear")
    clarity = analyze_clarity(testcases)
    print(json.dumps(clarity, indent=2))
    if not clarity["ready_for_generation"]:
        print("\nStopped before code generation. Answer the clarification questions first.")
        return

    log_step(3, "Classify web vs non-web category")
    category = detect_category(testcases)
    print(json.dumps(category, indent=2))

    log_step(4, "Read automation standards")
    standards = read_automation_standards.invoke({"category": category["primary_category"]})
    print(f"Loaded {len(standards.splitlines())} standards lines.")

    log_step(5, "Create Java TestNG Maven project")
    project_result = write_java_testng_maven_project.invoke(
        {"testcases": testcases, "category": category["primary_category"]}
    )
    print(project_result)
    project_dir = json.loads(project_result)["project_dir"]

    log_step(6, "Compile or statically validate generated project")
    validation = validate_generated_project.invoke({"project_dir": project_dir})
    print(validation)

    log_step(7, "Create HITL review packet")
    hitl = prepare_human_review_packet.invoke({"project_dir": project_dir})
    print(hitl)

    log_step(8, "PR draft gate")
    if auto_approve:
        print(draft_pull_request.invoke({"project_dir": project_dir, "title": "Add generated TestNG automation"}))
    else:
        print("Stopped before PR draft. Rerun with --auto-approve after reviewing HITL_REVIEW.md.")


def run_deep_agent(testcases: str, auto_approve: bool) -> None:
    log_step(1, "Run security preflight before sending content to the LLM")
    security = run_security_preflight(testcases)
    if security["block_generation"]:
        return

    log_step(2, "Build Deep Agent with Mesh LLM from .env")
    agent = build_deep_agent(include_pr_tool=False)

    log_step(3, "Invoke Deep Agent workflow")
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Generate automation for these test cases:\n\n" + testcases,
                }
            ]
        }
    )
    print("\nDeep Agent final response:\n")
    print(last_message_text(result))

    if LAST_PROJECT_DIR is None:
        return

    log_step(4, "Human-in-the-loop PR approval")
    approved = auto_approve
    if not auto_approve:
        try:
            answer = input("Type yes to draft a local PR package after HITL review: ")
        except EOFError:
            answer = ""
        approved = answer.strip().lower() in {"y", "yes"}

    if not approved:
        print("Stopped before PR draft. Review HITL_REVIEW.md and rerun with --auto-approve when ready.")
        return

    log_step(5, "Ask Deep Agent to draft the local PR package")
    pr_agent = build_deep_agent(include_pr_tool=True)
    pr_result = pr_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Human approved. Draft the local PR package.\n"
                        f"project_dir: {LAST_PROJECT_DIR}\n"
                        "title: Add generated TestNG automation"
                    ),
                }
            ]
        }
    )
    print("\nPR Agent final response:\n")
    print(last_message_text(pr_result))


def run_security_preflight(testcases: str) -> dict[str, Any]:
    global LAST_SECURITY
    LAST_SECURITY = scan_sensitive_test_data(testcases)
    print(json.dumps(LAST_SECURITY, indent=2))
    if LAST_SECURITY["block_generation"]:
        print(
            "\nStopped before LLM/code generation because high-risk credentials or "
            "secrets were found in the test case input."
        )
    return LAST_SECURITY


def read_input(args: argparse.Namespace) -> str:
    if args.input_file:
        return Path(args.input_file).read_text(encoding="utf-8")
    if args.testcases:
        return args.testcases
    if args.sample:
        return SAMPLE_FILE.read_text(encoding="utf-8")
    print("No input was provided, so the sample API test case will be used.\n")
    return SAMPLE_FILE.read_text(encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Practice Deep Agents with a TestNG generator.")
    parser.add_argument("--input-file", help="Path to a markdown or text file containing test cases.")
    parser.add_argument("--testcases", help="Inline test case text.")
    parser.add_argument("--sample", action="store_true", help="Use the built-in sample API test case.")
    parser.add_argument("--dry-run", action="store_true", help="Run deterministic tools without calling the LLM.")
    parser.add_argument(
        "--auto-approve",
        action="store_true",
        help="Skip the interactive HITL prompt and create the local PR draft.",
    )
    return parser


def first_meaningful_line(text: str) -> str:
    for line in text.splitlines():
        clean = line.strip(" #\t")
        if clean:
            return clean
    return ""


def make_slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return slug[:48] or "generated-test"


def make_class_name(slug: str, category: str) -> str:
    words = [word for word in slug.split("-") if word]
    base = "".join(word.capitalize() for word in words[:5]) or "Generated"
    suffix = {"web": "WebTest", "api": "ApiTest", "database": "DatabaseTest"}[category]
    if base.lower().endswith("test"):
        return base
    return base + suffix


def build_pom_xml(category: str) -> str:
    dependencies = [
        dependency_xml("org.testng", "testng", "7.10.2"),
    ]
    if category == "api":
        dependencies.append(dependency_xml("io.rest-assured", "rest-assured", "5.5.0"))
    elif category == "web":
        dependencies.append(dependency_xml("org.seleniumhq.selenium", "selenium-java", "4.25.0"))
    elif category == "database":
        dependencies.append(dependency_xml("com.h2database", "h2", "2.2.224"))

    deps = "\n".join(dependencies)
    return textwrap.dedent(
        f"""\
        <project xmlns="http://maven.apache.org/POM/4.0.0"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
          <modelVersion>4.0.0</modelVersion>
          <groupId>com.example.generated</groupId>
          <artifactId>generated-testng-automation</artifactId>
          <version>1.0-SNAPSHOT</version>

          <properties>
            <maven.compiler.source>17</maven.compiler.source>
            <maven.compiler.target>17</maven.compiler.target>
            <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
          </properties>

          <dependencies>
        {deps}
          </dependencies>

          <build>
            <plugins>
              <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.13.0</version>
              </plugin>
              <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <version>3.2.5</version>
              </plugin>
            </plugins>
          </build>
        </project>
        """
    )


def dependency_xml(group_id: str, artifact_id: str, version: str) -> str:
    return textwrap.indent(
        textwrap.dedent(
            f"""\
            <dependency>
              <groupId>{group_id}</groupId>
              <artifactId>{artifact_id}</artifactId>
              <version>{version}</version>
              <scope>test</scope>
            </dependency>"""
        ),
        "    ",
    )


def build_java_test_source(category: str, class_name: str) -> str:
    if category == "web":
        return build_web_test_source(class_name)
    if category == "database":
        return build_database_test_source(class_name)
    return build_api_test_source(class_name)


def build_api_test_source(class_name: str) -> str:
    return textwrap.dedent(
        f"""\
        package com.example.generated;

        import io.restassured.RestAssured;
        import org.testng.annotations.Test;

        import static io.restassured.RestAssured.given;
        import static org.testng.Assert.assertEquals;
        import static org.testng.Assert.assertFalse;

        public class {class_name} {{

            @Test
            public void shouldReturnOrderStatusForValidOrderId() {{
                RestAssured.baseURI = System.getProperty("api.baseUri", "https://example.test");

                String orderId =
                    given()
                        .header("Accept", "application/json")
                    .when()
                        .get("/orders/{{orderId}}/status", "ORD-1001")
                    .then()
                        .statusCode(200)
                        .extract()
                        .path("orderId");

                assertEquals(orderId, "ORD-1001", "The API should return the requested order ID.");
                assertFalse(orderId.isBlank(), "The order ID should not be blank.");
            }}
        }}
        """
    )


def build_web_test_source(class_name: str) -> str:
    return textwrap.dedent(
        f"""\
        package com.example.generated;

        import org.openqa.selenium.WebDriver;
        import org.openqa.selenium.chrome.ChromeDriver;
        import org.testng.annotations.AfterMethod;
        import org.testng.annotations.BeforeMethod;
        import org.testng.annotations.Test;

        import static org.testng.Assert.assertNotNull;

        public class {class_name} {{
            private WebDriver driver;

            @BeforeMethod(alwaysRun = true)
            public void setUp() {{
                driver = new ChromeDriver();
                driver.get(System.getProperty("app.url", "https://example.test"));
            }}

            @Test
            public void shouldDisplayExpectedPageForValidUserAction() {{
                assertNotNull(driver.getTitle(), "The page title should be available after navigation.");
            }}

            @AfterMethod(alwaysRun = true)
            public void tearDown() {{
                if (driver != null) {{
                    driver.quit();
                }}
            }}
        }}
        """
    )


def build_database_test_source(class_name: str) -> str:
    return textwrap.dedent(
        f"""\
        package com.example.generated;

        import org.testng.annotations.Test;

        import java.sql.Connection;
        import java.sql.DriverManager;
        import java.sql.PreparedStatement;
        import java.sql.ResultSet;
        import java.sql.SQLException;
        import java.sql.Statement;

        import static org.testng.Assert.assertEquals;

        public class {class_name} {{

            @Test
            public void shouldValidateExpectedRecordState() throws SQLException {{
                String jdbcUrl = System.getProperty("db.url", "jdbc:h2:mem:testdb;DB_CLOSE_DELAY=-1");

                try (Connection connection = DriverManager.getConnection(jdbcUrl, "sa", "")) {{
                    seedData(connection);

                    try (PreparedStatement statement = connection.prepareStatement(
                            "select status from orders where order_id = ?")) {{
                        statement.setString(1, "ORD-1001");
                        try (ResultSet resultSet = statement.executeQuery()) {{
                            resultSet.next();
                            assertEquals(resultSet.getString("status"), "READY");
                        }}
                    }}
                }}
            }}

            private void seedData(Connection connection) throws SQLException {{
                try (Statement statement = connection.createStatement()) {{
                    statement.execute("create table if not exists orders (order_id varchar(32), status varchar(32))");
                    statement.execute("delete from orders where order_id = 'ORD-1001'");
                    statement.execute("insert into orders values ('ORD-1001', 'READY')");
                }}
            }}
        }}
        """
    )


def build_generated_project_readme(testcases: str, category: str, class_name: str) -> str:
    return textwrap.dedent(
        f"""\
        # Generated TestNG Automation

        Category: `{category}`

        Main generated test:

        ```text
        src/test/java/com/example/generated/{class_name}.java
        ```

        Compile the generated tests:

        ```powershell
        mvn -q -DskipTests test-compile
        ```

        ## Source Test Cases

        ```text
        {testcases.strip()}
        ```
        """
    )


def resolve_generated_project(project_dir: str) -> Path:
    path = Path(project_dir).expanduser()
    if not path.is_absolute():
        path = (WORKSPACE_ROOT / path).resolve()
    else:
        path = path.resolve()

    generated_root = GENERATED_ROOT.resolve()
    if generated_root not in path.parents and path != generated_root:
        raise ValueError(f"Project path must stay under {generated_root}: {path}")
    if not path.exists():
        raise FileNotFoundError(f"Generated project not found: {path}")
    return path


def static_validate_project(path: Path) -> dict[str, Any]:
    issues: list[str] = []
    pom = path / "pom.xml"
    java_files = list(path.glob("src/test/java/**/*.java"))

    if not pom.exists():
        issues.append("pom.xml is missing.")
    if not java_files:
        issues.append("No Java test files found under src/test/java.")

    for java_file in java_files:
        text = java_file.read_text(encoding="utf-8")
        if "@Test" not in text:
            issues.append(f"{java_file.name} does not contain a TestNG @Test method.")
        if "Thread.sleep" in text:
            issues.append(f"{java_file.name} uses Thread.sleep.")
        if "password" in text.lower() and "System.getProperty" not in text:
            issues.append(f"{java_file.name} may hardcode a password.")

    return {
        "status": "passed" if not issues else "failed",
        "issues": issues,
        "java_files": [str(file.relative_to(path)) for file in java_files],
    }


def build_hitl_review(path: Path) -> str:
    security = json.dumps(LAST_SECURITY, indent=2) if LAST_SECURITY else "Not captured."
    clarity = json.dumps(LAST_CLARITY, indent=2) if LAST_CLARITY else "Not captured."
    category = json.dumps(LAST_CATEGORY, indent=2) if LAST_CATEGORY else "Not captured."
    validation = json.dumps(LAST_VALIDATION, indent=2) if LAST_VALIDATION else "Not captured."
    return textwrap.dedent(
        f"""\
        # HITL Review

        Generated project:

        ```text
        {path}
        ```

        ## Reviewer Checklist

        - [ ] Test case intent is correctly understood.
        - [ ] Category selection is correct.
        - [ ] Environment URLs, credentials, and tokens are not hardcoded.
        - [ ] Security preflight findings are resolved or accepted as synthetic test data.
        - [ ] Assertions match the expected business outcome.
        - [ ] Test data is safe for repeat execution.
        - [ ] Generated code follows the local automation standards.
        - [ ] Validation result is acceptable.

        ## Security Preflight Result

        ```json
        {security}
        ```

        ## Clarity Result

        ```json
        {clarity}
        ```

        ## Category Result

        ```json
        {category}
        ```

        ## Validation Result

        ```json
        {validation}
        ```
        """
    )


def build_pr_description(path: Path, title: str) -> str:
    validation_status = LAST_VALIDATION.get("compile_validation", {}).get("status", "not captured")
    static_status = LAST_VALIDATION.get("static_validation", {}).get("status", "not captured")
    return textwrap.dedent(
        f"""\
        # {title}

        ## Summary

        - Adds generated Java TestNG Maven automation under `{path.name}`.
        - Includes HITL review evidence.
        - Keeps environment-specific values outside Java source.

        ## Validation

        - Static validation: `{static_status}`
        - Maven test compile: `{validation_status}`

        ## Suggested Commands

        ```powershell
        git checkout -b feature/generated-testng-automation
        git add deepagents/generated-tests/{path.name}
        git commit -m "Add generated TestNG automation"
        gh pr create --title "{title}" --body-file deepagents/generated-tests/{path.name}/PR_DESCRIPTION.md
        ```

        ## Reviewer Notes

        Review `HITL_REVIEW.md` before opening or merging the PR.
        """
    )


def last_message_text(result: dict[str, Any]) -> str:
    messages = result.get("messages", [])
    if not messages:
        return str(result)

    message = messages[-1]
    content = getattr(message, "content", None)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
            else:
                parts.append(str(item))
        return "\n".join(parts)

    content_blocks = getattr(message, "content_blocks", None)
    if content_blocks is not None:
        return str(content_blocks)
    return str(message)


def main() -> None:
    args = build_parser().parse_args()
    testcases = read_input(args)

    if args.dry_run:
        run_dry_run(testcases, auto_approve=args.auto_approve)
    else:
        run_deep_agent(testcases, auto_approve=args.auto_approve)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped by user.")
        sys.exit(130)
