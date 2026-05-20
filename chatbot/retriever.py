"""Chroma vector store and retriever for resume RAG."""

import os

os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")

import logging
import shutil
from pathlib import Path
from typing import Optional

import chromadb
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from utils.embeddings import get_embeddings
from utils.helpers import PROJECT_ROOT, RUNTIME_TMP, _path_is_writable
from utils.text_splitter import split_resume_text

logger = logging.getLogger(__name__)


def _use_in_memory_chroma() -> bool:
    """Streamlit Cloud has a read-only app directory — use ephemeral Chroma."""
    mode = os.getenv("CHROMA_USE_MEMORY", "").lower()
    if mode in ("1", "true", "yes", "memory"):
        return True
    if mode in ("0", "false", "disk"):
        return False
    # Auto-detect: project vector_db not writable → in-memory
    project_db = PROJECT_ROOT / "vector_db" / "chroma_db"
    return not _path_is_writable(project_db)


def get_chroma_persist_dir() -> Optional[Path]:
    """
    Writable Chroma path, or None for in-memory (Streamlit Cloud).
    Override with CHROMA_PERSIST_DIR (/tmp/chroma or :memory:).
    """
    custom = os.getenv("CHROMA_PERSIST_DIR", "").strip()

    if custom in (":memory:", "memory"):
        return None

    if custom:
        path = Path(custom)
        if not path.is_absolute():
            path = PROJECT_ROOT / custom
        if _path_is_writable(path):
            return path
        logger.warning("CHROMA_PERSIST_DIR not writable (%s); using in-memory.", path)

    if _use_in_memory_chroma():
        return None

    for candidate in (
        PROJECT_ROOT / "vector_db" / "chroma_db",
        RUNTIME_TMP / "chroma_db",
    ):
        if _path_is_writable(candidate):
            return candidate

    return None


class ResumeVectorStore:
    """Manage Chroma persistence (disk or in-memory) for a single resume."""

    def __init__(self, collection_name: str = "resume_collection"):
        self.collection_name = collection_name
        self.persist_dir = get_chroma_persist_dir()
        self._vectorstore: Optional[Chroma] = None
        self._client = None
        if self.persist_dir is None:
            logger.info("Using in-memory Chroma (Streamlit Cloud / read-only FS).")

    def clear(self) -> None:
        """Reset vector store for a fresh upload."""
        self._vectorstore = None
        if self._client is not None:
            try:
                self._client.delete_collection(self.collection_name)
            except Exception:
                pass
            self._client = None
        if self.persist_dir and self.persist_dir.exists():
            shutil.rmtree(self.persist_dir, ignore_errors=True)
            self.persist_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Cleared vector store.")

    def _chroma_client(self):
        if self.persist_dir is None:
            self._client = chromadb.EphemeralClient()
        else:
            self._client = chromadb.PersistentClient(path=str(self.persist_dir))
        return self._client

    def build_from_text(self, resume_text: str, metadata: Optional[dict] = None) -> Chroma:
        """Chunk resume, embed, and store in Chroma."""
        self.clear()
        chunks = split_resume_text(resume_text)
        meta = metadata or {}
        documents = [
            Document(page_content=chunk, metadata={**meta, "chunk_index": i})
            for i, chunk in enumerate(chunks)
        ]
        embeddings = get_embeddings()
        client = self._chroma_client()

        kwargs = {
            "documents": documents,
            "embedding": embeddings,
            "collection_name": self.collection_name,
            "client": client,
        }
        if self.persist_dir is not None:
            kwargs["persist_directory"] = str(self.persist_dir)

        self._vectorstore = Chroma.from_documents(**kwargs)
        logger.info("Built Chroma index with %d chunks.", len(documents))
        return self._vectorstore

    def load(self) -> Optional[Chroma]:
        """Load persisted store from disk (skipped for in-memory)."""
        if self.persist_dir is None:
            return self._vectorstore
        if not self.persist_dir.exists() or not any(self.persist_dir.iterdir()):
            return None
        embeddings = get_embeddings()
        self._vectorstore = Chroma(
            collection_name=self.collection_name,
            embedding_function=embeddings,
            persist_directory=str(self.persist_dir),
        )
        return self._vectorstore

    def get_retriever(self, k: int = 4):
        if self._vectorstore is None:
            self.load()
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
