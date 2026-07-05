"""Streamlit UI for seeing the LLM context window.

Run:
    uv run streamlit run agents-context/03_streamlit_context_app.py
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


REPO_ROOT = Path(__file__).resolve().parent.parent
SYSTEM_MESSAGE = {
    "role": "system",
    "content": "You are a helpful assistant. Answer briefly.",
}


def load_config() -> None:
    load_dotenv(REPO_ROOT / ".env")
    missing = [
        name
        for name in ("MESH_API_KEY", "MESH_API_URL", "MESH_MODEL")
        if not os.getenv(name)
    ]
    if missing:
        st.error(f"Missing .env values: {', '.join(missing)}")
        st.stop()


@st.cache_resource
def build_llm() -> ChatOpenAI:
    load_config()
    return ChatOpenAI(
        api_key=os.environ["MESH_API_KEY"],
        base_url=os.environ["MESH_API_URL"].rstrip("/"),
        model=os.environ["MESH_MODEL"],
        temperature=float(os.getenv("MESH_TEMPERATURE", "0.2")),
        timeout=float(os.getenv("MESH_TIMEOUT_SECONDS", "60")),
    )


def reset_context() -> None:
    st.session_state.messages = [SYSTEM_MESSAGE.copy()]
    st.session_state.last_context_window = []
    st.session_state.token_rows = []


def start_new_chat() -> None:
    st.session_state.chat_number = st.session_state.get("chat_number", 0) + 1
    st.session_state.session_id = f"chat-{st.session_state.chat_number}"
    reset_context()


def ensure_state() -> None:
    if "chat_number" not in st.session_state:
        st.session_state.chat_number = 1
    if "session_id" not in st.session_state:
        st.session_state.session_id = "chat-1"
    if "messages" not in st.session_state:
        reset_context()
    if "last_context_window" not in st.session_state:
        st.session_state.last_context_window = []
    if "token_rows" not in st.session_state:
        st.session_state.token_rows = []


def usage_from_response(response: Any) -> dict[str, Any]:
    usage = getattr(response, "usage_metadata", None) or {}
    return {
        "input_tokens": usage.get("input_tokens"),
        "output_tokens": usage.get("output_tokens"),
        "total_tokens": usage.get("total_tokens"),
    }


def send_message(user_input: str) -> None:
    llm = build_llm()

    st.session_state.messages.append({"role": "user", "content": user_input})

    context_window = list(st.session_state.messages)
    response = llm.invoke(context_window)
    assistant_text = response.content
    usage = usage_from_response(response)

    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_text}
    )
    st.session_state.last_context_window = context_window
    st.session_state.token_rows.append(
        {
            "turn": len(st.session_state.token_rows) + 1,
            "user_input": user_input,
            "response": assistant_text,
            **usage,
        }
    )


def visible_messages() -> list[dict[str, str]]:
    return [
        message
        for message in st.session_state.messages
        if message["role"] != "system"
    ]


def main() -> None:
    st.set_page_config(page_title="LLM Context Window", layout="wide")
    ensure_state()
    load_config()

    st.title("LLM Context Window")
    st.caption(
        "The app remembers only because it stores previous messages and sends "
        "them again in the next LLM request."
    )

    with st.sidebar:
        st.subheader("LLM")
        st.write(f"Model: `{os.environ['MESH_MODEL']}`")
        st.write(f"Base URL: `{os.environ['MESH_API_URL'].rstrip('/')}`")
        st.divider()
        st.subheader("Chat Controls")
        st.write(f"Current chat: `{st.session_state.session_id}`")
        if st.button("New Chat", type="primary", use_container_width=True):
            start_new_chat()
            st.rerun()
        if st.button("Reset Context", use_container_width=True):
            reset_context()
            st.rerun()
        st.caption(
            "New Chat creates a fresh session id. Reset Context clears the "
            "messages, last context window, and token table for this session."
        )

    chat_col, details_col = st.columns([0.55, 0.45])

    with chat_col:
        st.subheader(f"Chat - {st.session_state.session_id}")
        for message in visible_messages():
            with st.chat_message(message["role"]):
                st.write(message["content"])

        user_input = st.chat_input("Try: Hi, I am Chetan.")
        if user_input:
            with st.spinner("Calling LLM with current session messages..."):
                send_message(user_input)
            st.rerun()

    with details_col:
        st.subheader("Session Messages")
        st.write("These are stored by the application.")
        st.json(st.session_state.messages, expanded=True)

        st.subheader("Last Context Window Sent To LLM")
        if st.session_state.last_context_window:
            st.json(st.session_state.last_context_window, expanded=True)
        else:
            st.info("Send a message to see the exact context window.")

        st.subheader("Tokens And Responses")
        if st.session_state.token_rows:
            st.dataframe(
                pd.DataFrame(st.session_state.token_rows),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Token usage appears after the first LLM response.")


if __name__ == "__main__":
    main()
