"""HuggingFace embedding model for Chroma vector store."""

import logging
import os

from langchain_community.embeddings import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)

_embeddings_cache: HuggingFaceEmbeddings | None = None


def get_embeddings() -> HuggingFaceEmbeddings:
    """Return a cached HuggingFace embeddings instance."""
    global _embeddings_cache
    if _embeddings_cache is None:
        model_name = os.getenv(
            "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        )
        logger.info("Loading embedding model: %s", model_name)
        _embeddings_cache = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embeddings_cache
