"""Q&A Coach node — Socratic method tutoring for semiconductor concepts."""
from __future__ import annotations

from langchain_core.messages import AIMessage

from semiconductor.adapters.state import InterviewState
from semiconductor.application.use_cases.coach_concept import CoachConceptUseCase
from semiconductor.infrastructure.llm import LangChainLLMService


def qa_coach_node(state: InterviewState) -> dict:
    coach_uc = CoachConceptUseCase(LangChainLLMService.coach())

    topic = state.get("current_qa_topic") or "반도체 기초"
    hint_count = state.get("hint_count", 0)
    messages = state.get("messages", [])

    if not topic:
        return {
            "display_output": (
                "학습할 주제를 알려주세요. 예시: /qa TSV 구조"
            ),
        }

    response_text, new_hint_count = coach_uc.execute(
        topic=topic,
        messages=messages,
        hint_count=hint_count,
    )

    return {
        "hint_count": new_hint_count,
        "display_output": response_text,
        "messages": [AIMessage(content=response_text)],
    }
