"""Prompt templates for interview Q&A and preparation."""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate

from utils.helpers import load_prompt_file


def get_qa_system_prompt(candidate_name: str, context: str) -> str:
    """Build system prompt with resume context."""
    template = load_prompt_file("system_prompt.txt")
    return template.format(candidate_name=candidate_name, context=context)


def get_conversational_prompt() -> ChatPromptTemplate:
    """Prompt for conversational retrieval chain."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", "{system_prompt}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )


def get_condense_question_prompt() -> PromptTemplate:
    """Rephrase follow-up questions using chat history."""
    return PromptTemplate.from_template(
        """Given the following conversation and a follow-up question, rephrase the follow-up question to be a standalone question.

Chat History:
{chat_history}

Follow Up Input: {question}
Standalone question:"""
    )


def get_interview_prep_prompt(candidate_name: str, resume_text: str) -> str:
    """Build interview preparation prompt."""
    template = load_prompt_file("interview_prompt.txt")
    return template.format(candidate_name=candidate_name, resume_text=resume_text[:12000])


def get_suggested_questions_prompt(resume_excerpt: str) -> str:
    """Prompt for generating suggested interview questions."""
    return f"""Based ONLY on this resume excerpt, list exactly 8 interview questions an interviewer might ask.
Mix HR, behavioral, and technical questions relevant to this profile.
Output as a numbered list only — no answers.

Resume excerpt:
{resume_excerpt[:4000]}
"""
