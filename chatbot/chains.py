"""Retrieval-augmented Q&A (RAG) without langchain-classic dependency."""

import logging
from typing import Iterator

from chatbot.llm import create_llm, invoke_with_fallback, stream_llm_response
from chatbot.prompts import (
    get_interview_prep_prompt,
    get_qa_system_prompt,
    get_suggested_questions_prompt,
)
from chatbot.retriever import ResumeVectorStore

logger = logging.getLogger(__name__)


class InterviewChainManager:
    """Orchestrates RAG Q&A, streaming, and prep generation."""

    def __init__(self):
        self.vector_store = ResumeVectorStore()
        self.candidate_name: str = "Candidate"
        self.resume_text: str = ""

    def index_resume(self, resume_text: str, candidate_name: str) -> None:
        """Chunk resume, embed, and persist to Chroma."""
        self.resume_text = resume_text
        self.candidate_name = candidate_name
        self.vector_store.build_from_text(
            resume_text,
            metadata={"candidate": candidate_name},
        )
        logger.info("Resume indexed for %s.", candidate_name)

    def _get_context(self, question: str) -> str:
        return self.vector_store.get_relevant_context(question, k=5)

    def ask(self, question: str, chat_history: list[tuple[str, str]] | None = None) -> str:
        """Non-streaming answer with retrieved resume context."""
        if not self.resume_text:
            raise RuntimeError("Upload a resume before asking questions.")

        context = self._get_context(question)
        system = get_qa_system_prompt(self.candidate_name, context)
        llm = create_llm(streaming=False)
        from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

        messages = [SystemMessage(content=system)]
        if chat_history:
            for human, ai in chat_history:
                messages.append(HumanMessage(content=human))
                messages.append(AIMessage(content=ai))
        messages.append(HumanMessage(content=question))

        return invoke_with_fallback(llm, messages)

    def ask_stream(
        self,
        question: str,
        chat_history: list[tuple[str, str]],
    ) -> Iterator[str]:
        """Stream answer with retrieved resume context."""
        if not self.resume_text:
            raise RuntimeError("Upload a resume before asking questions.")

        context = self._get_context(question)
        system = get_qa_system_prompt(self.candidate_name, context)
        llm = create_llm(streaming=True)
        yield from stream_llm_response(llm, system, question, chat_history)

    def generate_interview_prep(self) -> str:
        """AI-generated interview preparation guide."""
        if not self.resume_text:
            raise RuntimeError("Upload a resume first.")
        prompt = get_interview_prep_prompt(self.candidate_name, self.resume_text)
        llm = create_llm(streaming=False, temperature=0.4)
        from langchain_core.messages import HumanMessage

        return invoke_with_fallback(llm, [HumanMessage(content=prompt)])

    def generate_suggested_questions(self) -> str:
        """Generate suggested interview questions from resume."""
        if not self.resume_text:
            raise RuntimeError("Upload a resume first.")
        prompt = get_suggested_questions_prompt(self.resume_text)
        llm = create_llm(streaming=False, temperature=0.5)
        from langchain_core.messages import HumanMessage

        return invoke_with_fallback(llm, [HumanMessage(content=prompt)])
