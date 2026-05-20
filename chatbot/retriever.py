"""Chroma vector store and retriever for resume RAG."""

import os

os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")

import logging
import shutil
from pathlib import Path
from typing import Optional

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from utils.embeddings import get_embeddings
from utils.helpers import PROJECT_ROOT
from utils.text_splitter import split_resume_text

logger = logging.getLogger(__name__)


def get_chroma_persist_dir() -> Path:
    rel = os.getenv("CHROMA_PERSIST_DIR", "vector_db/chroma_db")
    path = PROJECT_ROOT / rel
    path.mkdir(parents=True, exist_ok=True)
    return path


class ResumeVectorStore:
    """Manage Chroma persistence for a single resume collection."""

    def __init__(self, collection_name: str = "resume_collection"):
        self.collection_name = collection_name
        self.persist_dir = get_chroma_persist_dir()
        self._vectorstore: Optional[Chroma] = None

    def clear(self) -> None:
        """Remove persisted vectors for a fresh upload."""
        if self.persist_dir.exists():
            shutil.rmtree(self.persist_dir, ignore_errors=True)
            self.persist_dir.mkdir(parents=True, exist_ok=True)
        self._vectorstore = None
        logger.info("Cleared vector store at %s", self.persist_dir)

    def build_from_text(self, resume_text: str, metadata: Optional[dict] = None) -> Chroma:
        """Chunk resume, embed, and persist to Chroma."""
        self.clear()
        chunks = split_resume_text(resume_text)
        meta = metadata or {}
        documents = [
            Document(page_content=chunk, metadata={**meta, "chunk_index": i})
            for i, chunk in enumerate(chunks)
        ]
        embeddings = get_embeddings()
        self._vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            collection_name=self.collection_name,
            persist_directory=str(self.persist_dir),
        )
        logger.info("Built Chroma index with %d documents.", len(documents))
        return self._vectorstore

    def load(self) -> Optional[Chroma]:
        """Load existing Chroma store from disk."""
        if not any(self.persist_dir.iterdir()):
            return None
        embeddings = get_embeddings()
        self._vectorstore = Chroma(
            collection_name=self.collection_name,
            embedding_function=embeddings,
            persist_directory=str(self.persist_dir),
        )
        return self._vectorstore

    def get_retriever(self, k: int = 4):
        """Return a LangChain retriever over resume chunks."""
        if self._vectorstore is None:
            self.load()
        if self._vectorstore is None:
            raise RuntimeError("No resume indexed. Please upload a resume first.")
        return self._vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k},
        )

    def get_relevant_context(self, query: str, k: int = 4) -> str:
        """Fetch top-k chunks as a single context string."""
        retriever = self.get_retriever(k=k)
        docs = retriever.invoke(query)
        return "\n\n---\n\n".join(d.page_content for d in docs)
