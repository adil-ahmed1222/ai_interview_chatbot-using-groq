"""
Voice-ready / API extension scaffold.

Run separately when you add FastAPI/Flask:
    uvicorn api.server:app --reload

Endpoints to implement:
    POST /upload-resume  — index resume
    POST /chat           — non-streaming Q&A
    POST /chat/stream    — SSE streaming
    GET  /health
"""

from typing import Any


def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "resume-ai-chatbot"}


def chat_payload(question: str, session_id: str) -> dict[str, Any]:
    """Example request shape for future API clients."""
    return {"question": question, "session_id": session_id}
