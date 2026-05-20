"""Shared helpers: logging, file I/O, name extraction, chat export."""

import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = PROJECT_ROOT / "prompts"
RUNTIME_TMP = Path(os.environ.get("TMPDIR", "/tmp")) / "ai_interview_chatbot"


def _path_is_writable(path: Path) -> bool:
    """Return True if we can create and write a probe file in path."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".write_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return True
    except OSError:
        return False


def get_runtime_dir(subdir: str | Path) -> Path:
    """
    Writable folder for uploads/cache.
    Streamlit Cloud mounts /mount/src as read-only — falls back to /tmp.
    """
    rel = Path(subdir)
    for candidate in (PROJECT_ROOT / rel, RUNTIME_TMP / rel):
        if _path_is_writable(candidate):
            return candidate
    raise OSError(f"No writable directory available for '{subdir}'")


def get_uploads_dir() -> Path:
    return get_runtime_dir("uploads")


def get_chat_history_dir() -> Path:
    return get_runtime_dir("data/chat_history")


def setup_logging(level: int = logging.INFO) -> None:
    """Configure root logger for the application."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def ensure_directories() -> None:
    """Create writable runtime directories (never crash app startup)."""
    for name, getter in (
        ("uploads", get_uploads_dir),
        ("chat_history", get_chat_history_dir),
    ):
        try:
            getter()
        except OSError as exc:
            logger.warning("Could not prepare %s directory: %s", name, exc)


def save_uploaded_file(filename: str, content: bytes) -> Path:
    """Persist uploaded resume to a writable uploads folder."""
    uploads = get_uploads_dir()
    safe_name = re.sub(r"[^\w.\-]", "_", filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = uploads / f"{timestamp}_{safe_name}"
    dest.write_bytes(content)
    logger.info("Saved resume to %s", dest)
    return dest


def extract_candidate_name(resume_text: str) -> str:
    """
    Heuristic name extraction from resume header.
    Falls back to 'Candidate' if uncertain.
    """
    lines = [ln.strip() for ln in resume_text.splitlines() if ln.strip()]
    if not lines:
        return "Candidate"

    first_line = lines[0]
    # Skip lines that look like titles or contact info
    if re.search(r"@|http|linkedin|phone|\d{3}", first_line, re.I):
        for line in lines[1:6]:
            if not re.search(r"@|http|phone|\d{3}", line, re.I) and 2 <= len(line.split()) <= 5:
                if re.match(r"^[A-Z][a-z]+(\s+[A-Z][a-z'.-]+)+$", line):
                    return line
        return "Candidate"

    words = first_line.split()
    if 2 <= len(words) <= 5 and len(first_line) < 60:
        if all(w[0].isupper() for w in words if w.isalpha()):
            return first_line

    return "Candidate"


def load_prompt_file(filename: str) -> str:
    """Load a prompt template from prompts/."""
    path = PROMPTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8").strip()


def format_chat_for_download(messages: list[dict[str, Any]], candidate_name: str) -> str:
    """Format chat history as plain text for download."""
    lines = [
        "Resume AI Interview Chat — Export",
        f"Candidate: {candidate_name}",
        f"Exported: {datetime.now().isoformat(timespec='seconds')}",
        "-" * 60,
        "",
    ]
    for msg in messages:
        role = msg.get("role", "unknown").upper()
        content = msg.get("content", "")
        lines.append(f"[{role}]")
        lines.append(content)
        lines.append("")
    return "\n".join(lines)


def save_chat_history_json(messages: list[dict[str, Any]], candidate_name: str) -> Path:
    """Persist chat session as JSON in data/chat_history/."""
    ensure_directories()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = re.sub(r"[^\w\-]", "_", candidate_name)
    path = get_chat_history_dir() / f"chat_{safe_name}_{timestamp}.json"
    payload = {
        "candidate": candidate_name,
        "exported_at": datetime.now().isoformat(),
        "messages": messages,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    logger.info("Chat history saved to %s", path)
    return path


def read_resume_file(filename: str, content: bytes) -> str:
    """Dispatch to PDF or DOCX reader based on extension."""
    from utils.docx_reader import extract_text_from_docx
    from utils.pdf_reader import extract_text_from_pdf

    from io import BytesIO

    ext = Path(filename).suffix.lower()
    stream = BytesIO(content)

    if ext == ".pdf":
        return extract_text_from_pdf(stream)
    if ext in (".docx", ".doc"):
        return extract_text_from_docx(stream)
    raise ValueError(f"Unsupported file type: {ext}. Use PDF or DOCX.")
