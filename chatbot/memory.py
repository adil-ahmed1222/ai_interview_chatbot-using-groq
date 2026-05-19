"""Session chat history helpers (multi-turn memory via Streamlit + LLM context)."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def get_chat_history_tuples(messages: list[dict[str, Any]]) -> list[tuple[str, str]]:
    """Convert session messages to (human, ai) tuples for streaming."""
    history: list[tuple[str, str]] = []
    i = 0
    while i < len(messages) - 1:
        if messages[i].get("role") == "user" and messages[i + 1].get("role") == "assistant":
            history.append((messages[i]["content"], messages[i + 1]["content"]))
            i += 2
        else:
            i += 1
    return history
