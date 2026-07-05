"""LangChain agent using Pydantic concepts.

This example combines:

- BaseModel
- Annotated fields
- field_validator
- model_validator
- computed_field
- nested models
- LangChain tool args_schema
- console logging for flow understanding

Run:
    uv run python pydantic-1/08_langchain_agent_with_pydantic.py
"""

from __future__ import annotations

import logging
import os
import sys
from itertools import count
from typing import Annotated, Literal, Self

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, computed_field, field_validator, model_validator


logger = logging.getLogger("pydantic_langchain_flow")
step_counter = count(1)


def setup_logging() -> None:
    """Print readable flow logs on the console."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        stream=sys.stdout,
        force=True,
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)


def log_step(message: str) -> None:
    """Print one numbered flow step."""

    logger.info("[STEP %02d] %s", next(step_counter), message)


class Requester(BaseModel):
    """Nested model for the person who raised the ticket."""

    name: Annotated[str, Field(min_length=2)]
    email: str

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        logger.info("          Validator: clean requester.name")
        return value.strip().title()

    @field_validator("email")
    @classmethod
    def clean_email(cls, value: str) -> str:
        logger.info("          Validator: clean requester.email")
        cleaned_email = value.strip().lower()
        if "@" not in cleaned_email:
            raise ValueError("email must contain @")
        return cleaned_email


class TicketInput(BaseModel):
    """Pydantic schema used as the LangChain tool input."""

    title: Annotated[str, Field(min_length=5)]
    priority: Literal["low", "medium", "high", "critical"]
    affected_users: Annotated[int, Field(ge=0)]
    requester: Requester
    symptoms: list[Annotated[str, Field(min_length=3)]]

    @field_validator("priority", mode="before")
    @classmethod
    def normalize_priority(cls, value: str) -> str:
        logger.info("          Validator: normalize priority")
        return value.strip().lower()

    @model_validator(mode="after")
    def critical_ticket_must_have_affected_users(self) -> Self:
        logger.info("          Model validator: check cross-field ticket rules")
        if self.priority == "critical" and self.affected_users == 0:
            raise ValueError("critical tickets must have affected users")
        return self

    @computed_field
    @property
    def impact_score(self) -> int:
        logger.info("          Computed field: calculate impact_score")
        priority_score = {
            "low": 1,
            "medium": 10,
            "high": 100,
            "critical": 1000,
        }
        return priority_score[self.priority] + self.affected_users


TicketInput.model_rebuild()


@tool(args_schema=TicketInput)
def triage_ticket(
    title: str,
    priority: str,
    affected_users: int,
    requester: Requester,
    symptoms: list[str],
) -> str:
    """Validate and triage a support ticket."""

    log_step("LangChain called the triage_ticket tool")
    logger.info("          Raw tool input title=%r priority=%r", title, priority)

    log_step("Pydantic validates the tool input using TicketInput")
    ticket = TicketInput(
        title=title,
        priority=priority,
        affected_users=affected_users,
        requester=requester,
        symptoms=symptoms,
    )

    log_step("Tool uses the computed impact_score to choose an action")
    if ticket.impact_score >= 1000:
        action = "Escalate immediately and start incident communication."
    elif ticket.impact_score >= 100:
        action = "Assign an owner and begin urgent investigation."
    else:
        action = "Handle through the normal support queue."

    log_step("Tool returns validated result back to the agent")
    return (
        f"Validated ticket: {ticket.title}\n"
        f"Priority: {ticket.priority}\n"
        f"Affected users: {ticket.affected_users}\n"
        f"Requester: {ticket.requester.name} <{ticket.requester.email}>\n"
        f"Symptoms: {', '.join(ticket.symptoms)}\n"
        f"Impact score: {ticket.impact_score}\n"
        f"Recommended action: {action}"
    )


def build_mesh_model() -> ChatOpenAI:
    """Create the LLM using Mesh API settings from the project .env."""

    log_step("Load .env settings for the Mesh-backed LLM")
    load_dotenv()

    missing = [
        name
        for name in ("MESH_API_KEY", "MESH_API_URL", "MESH_MODEL")
        if not os.getenv(name)
    ]
    if missing:
        raise RuntimeError(f"Missing required .env values: {', '.join(missing)}")

    log_step(f"Create ChatOpenAI model for {os.environ['MESH_MODEL']}")
    return ChatOpenAI(
        api_key=os.environ["MESH_API_KEY"],
        base_url=os.environ["MESH_API_URL"].rstrip("/"),
        model=os.environ["MESH_MODEL"],
        temperature=float(os.getenv("MESH_TEMPERATURE", "0.2")),
        timeout=float(os.getenv("MESH_TIMEOUT_SECONDS", "60")),
    )


def show_pydantic_validation() -> None:
    """Show Pydantic working before the LangChain agent runs."""

    log_step("Create raw ticket data with messy strings")
    ticket = TicketInput(
        title="Payment API outage",
        priority="CRITICAL",
        affected_users="1500",
        requester={"name": " Chetan ", "email": " CHETANexample.COM "},
        symptoms=["checkout fails", "payment timeout"],
    )

    log_step("Print the cleaned Pydantic model before the agent runs")
    print("Pydantic validated input:")
    print(ticket.model_dump())
    print()


def main() -> None:
    setup_logging()
    log_step("Start LangChain + Pydantic example")

    show_pydantic_validation()

    log_step("Create LangChain agent with triage_ticket tool")
    agent = create_agent(
        model=build_mesh_model(),
        tools=[triage_ticket],
        system_prompt=(
            "You are a helpful support assistant. "
            "Always call triage_ticket when the user asks about ticket triage. "
            "After the tool returns, explain the result in simple language."
        ),
    )

    user_message = (
        "Triage this ticket: title Payment API outage, "
        "priority critical, affected users 1500, requester "
        "Chetan with email chetan@example.com, symptoms are "
        "checkout fails and payment timeout."
    )

    log_step("Send user message to the agent")
    logger.info("          User message: %s", user_message)

    result = agent.invoke(
        {"messages": [{"role": "user", "content": user_message}]}
    )

    log_step("Agent received the tool result and produced the final answer")
    print("Agent final answer:")
    print(result["messages"][-1].content_blocks)


if __name__ == "__main__":
    main()
