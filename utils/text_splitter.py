"""Split resume text into chunks for vector storage."""

import logging
import os

from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


def get_text_splitter() -> RecursiveCharacterTextSplitter:
    """Create a recursive character splitter with env-configured sizes."""
    chunk_size = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "150"))
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )


def split_resume_text(text: str) -> list[str]:
    """Split resume text into overlapping chunks."""
    splitter = get_text_splitter()
    chunks = splitter.split_text(text)
    logger.info("Split resume into %d chunks.", len(chunks))
    return chunks
