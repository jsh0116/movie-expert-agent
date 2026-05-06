"""LangGraph state definition for the semiconductor interview agent."""
from __future__ import annotations

from typing import Annotated, Optional, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class InterviewState(TypedDict):
    # ── Session config ────────────────────────────────────────────
    company: str           # "samsung_ds" | "sk_hynix"
    domain: Optional[str]  # None → all domains
    max_questions: int

    # ── Workflow control ──────────────────────────────────────────
    mode: str  # "idle" | "interview" | "qa" | "diagnostic"

    # ── Mock Interviewer tracking ─────────────────────────────────
    asked_count: int
    current_question_text: Optional[str]
    current_question_domain: Optional[str]
    current_question_key_points: list[str]
    evaluations: list[dict]  # serialized EvaluationResult dicts

    # ── Q&A Coach tracking ────────────────────────────────────────
    hint_count: int
    current_qa_topic: str

    # ── Conversation history (accumulates across turns) ───────────
    messages: Annotated[list[BaseMessage], add_messages]

    # ── Display output (printed to Jupyter cell) ──────────────────
    display_output: str

    # ── Chart image bytes (set by diagnostic_node, sent by Chainlit) ─
    chart_png: Optional[bytes]


def create_initial_state(
    company: str = "samsung_ds",
    domain: Optional[str] = None,
    max_questions: int = 5,
) -> InterviewState:
    return InterviewState(
        company=company,
        domain=domain,
        max_questions=max_questions,
        mode="idle",
        asked_count=0,
        current_question_text=None,
        current_question_domain=None,
        current_question_key_points=[],
        evaluations=[],
        hint_count=0,
        current_qa_topic="",
        messages=[],
        display_output=(
            "👋 반도체 면접 준비 에이전트에 오신 걸 환영합니다!\n\n"
            "📋 명령어 안내:\n"
            "  /인터뷰   — 모의 기술 면접 시작\n"
            "  /qa [주제] — 개념 학습 코치 (소크라테스 방식)\n"
            "  /진단     — 이해도 진단 및 시각화\n"
        ),
        chart_png=None,
    )
