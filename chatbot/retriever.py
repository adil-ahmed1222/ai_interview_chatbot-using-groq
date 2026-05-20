"""Chroma / FAISS vector store for resume RAG (Streamlit Cloud safe)."""

import os
import uuid

os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")

import logging
import shutil
from pathlib import Path
from typing import Any, Optional, Union

import chromadb
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore

from utils.embeddings import get_embeddings
from utils.helpers import PROJECT_ROOT, RUNTIME_TMP, _path_is_writable
from utils.text_splitter import split_resume_text

logger = logging.getLogger(__name__)

VectorStoreType = Union[Chroma, Any]


def _is_streamlit_cloud() -> bool:
    """Streamlit Cloud mounts repo at /mount/src (read-only)."""
    return Path("/mount/src").exists() or bool(os.environ.get("STREAMLIT_RUNTIME_ENV"))


def _use_in_memory_chroma() -> bool:
    mode = os.getenv("CHROMA_USE_MEMORY", "").lower()
    if mode in ("1", "true", "yes", "memory"):
        return True
    if mode in ("0", "false", "disk"):
        return False
    if _is_streamlit_cloud():
        return True
    project_db = PROJECT_ROOT / "vector_db" / "chroma_db"
    return not _path_is_writable(project_db)


def get_chroma_persist_dir() -> Optional[Path]:
    if _use_in_memory_chroma():
        return None

    custom = os.getenv("CHROMA_PERSIST_DIR", "").strip()
    if custom in (":memory:", "memory"):
        return None

    if custom:
        path = Path(custom) if Path(custom).is_absolute() else PROJECT_ROOT / custom
        if _path_is_writable(path):
            return path

    for candidate in (PROJECT_ROOT / "vector_db" / "chroma_db", RUNTIME_TMP / "chroma_db"):
        if _path_is_writable(candidate):
            return candidate

    return None


def _build_faiss(documents: list[Document], embeddings) -> VectorStore:
    """In-memory FAISS — no SQLite, reliable on Streamlit Cloud."""
    from langchain_community.vectorstores import FAISS

    logger.info("Building FAISS in-memory index (%d chunks).", len(documents))
    return FAISS.from_documents(documents, embeddings)


def _build_chroma(
    documents: list[Document],
    embeddings,
    collection_name: str,
    persist_dir: Optional[Path],
) -> Chroma:
    """Fresh Chroma client + add_documents (avoids tenants table / stale DB bugs)."""
    if persist_dir is not None:
        if persist_dir.exists():
            shutil.rmtree(persist_dir, ignore_errors=True)
        persist_dir.mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=Settings(anonymized_telemetry=False, allow_reset=True),
        )
    else:
        client = chromadb.EphemeralClient(
            settings=Settings(anonymized_telemetry=False, allow_reset=True),
        )

    # Unique collection per index build — avoids stale sqlite schema conflicts
    unique_name = f"{collection_name}_{uuid.uuid4().hex[:8]}"

    vectorstore = Chroma(
        client=client,
        collection_name=unique_name,
        embedding_function=embeddings,
    )
    vectorstore.add_documents(documents)
    logger.info("Built Chroma index '%s' with %d chunks.", unique_name, len(documents))
    return vectorstore


class ResumeVectorStore:
    """Resume vector index — in-memory on Streamlit Cloud, disk locally."""

    def __init__(self, collection_name: str = "resume_collection"):
        self.collection_name = collection_name
        self.persist_dir = get_chroma_persist_dir()
        self._vectorstore: Optional[VectorStoreType] = None
        self._backend: str = "none"

        if self.persist_dir is None:
            logger.info("Vector store: in-memory (Chroma ephemeral or FAISS fallback).")

    def clear(self) -> None:
        self._vectorstore = None
        self._backend = "none"
        if self.persist_dir and self.persist_dir.exists():
            shutil.rmtree(self.persist_dir, ignore_errors=True)
        logger.info("Cleared vector store.")

    def build_from_text(self, resume_text: str, metadata: Optional[dict] = None) -> VectorStoreType:
        self.clear()
        chunks = split_resume_text(resume_text)
        meta = metadata or {}
        documents = [
            Document(page_content=chunk, metadata={**meta, "chunk_index": i})
            for i, chunk in enumerate(chunks)
        ]
        embeddings = get_embeddings()

        # Streamlit Cloud: prefer FAISS (no Chroma SQLite tenants table issues)
        if _is_streamlit_cloud() or os.getenv("VECTOR_BACKEND", "").lower() == "faiss":
            self._vectorstore = _build_faiss(documents, embeddings)
            self._backend = "faiss"
            return self._vectorstore

        try:
            self._vectorstore = _build_chroma(
                documents, embeddings, self.collection_name, self.persist_dir
            )
            self._backend = "chroma"
            return self._vectorstore
        except Exception as exc:
            logger.warning("Chroma failed (%s); falling back to FAISS.", exc)
            self._vectorstore = _build_faiss(documents, embeddings)
            self._backend = "faiss"
            return self._vectorstore

    def load(self) -> Optional[VectorStoreType]:
        return self._vectorstore

    def get_retriever(self, k: int = 4):
        if self._vectorstore is None:
            raise RuntimeError("No resume indexed. Please upload a resume first.")
        return self._vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k},
        )

    def get_relevant_context(self, query: str, k: int = 4) -> str:
        retriever = self.get_retriever(k=k)
        docs = retriever.invoke(query)
        return "\n\n---\n\n".join(d.page_content for d in docs)
