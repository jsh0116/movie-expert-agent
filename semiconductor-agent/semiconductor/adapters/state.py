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
    interview_phase: str  # "present" | "evaluate" — 면접 내 단계 (mode=interview일 때만 의미)

    # ── Mock Interviewer tracking ─────────────────────────────────
    asked_count: int
    current_question_text: Optional[str]
    current_question_domain: Optional[str]
    current_question_key_points: list[str]
    evaluations: list[dict]  # serialized EvaluationResult dicts
    pending_evaluation: Optional[dict]  # judge 결과, critic이 받아 검증 (turn 내에서만 유효)
    web_enrichment: Optional[str]  # 트렌드 도메인 평가 시 병렬 웹검색 결과 (Send API)

    # ── Q&A Coach tracking ────────────────────────────────────────
    hint_count: int
    current_qa_topic: str

    # ── Essay Coach tracking ──────────────────────────────────────
    essay_company: Optional[str]   # "samsung_ds" | "sk_hynix"
    essay_item: Optional[str]      # "지원동기" | ...
    essay_phase: str               # "present" | "evaluate"
    essays_evaluated: list[dict]   # 누적 자소서 평가 결과

    # ── Behavioral Interview tracking ─────────────────────────────
    behavioral_company: Optional[str]
    behavioral_question_text: Optional[str]
    behavioral_competency: Optional[str]
    behavioral_phase: str          # "present" | "evaluate"
    behavioral_asked_count: int
    behaviorals_evaluated: list[dict]

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
        interview_phase="present",
        asked_count=0,
        current_question_text=None,
        current_question_domain=None,
        current_question_key_points=[],
        evaluations=[],
        pending_evaluation=None,
        web_enrichment=None,
        hint_count=0,
        current_qa_topic="",
        essay_company=None,
        essay_item=None,
        essay_phase="present",
        essays_evaluated=[],
        behavioral_company=None,
        behavioral_question_text=None,
        behavioral_competency=None,
        behavioral_phase="present",
        behavioral_asked_count=0,
        behaviorals_evaluated=[],
        messages=[],
        display_output=(
            "👋 반도체 면접 준비 에이전트에 오신 걸 환영합니다!\n\n"
            "📋 명령어 안내:\n"
            "  /인터뷰   — 모의 기술 면접 시작\n"
            "  /qa [주제] — 개념 학습 코치 (소크라테스 방식)\n"
            "  /자소서 [회사] [항목] — 자소서 첨삭 (예: /자소서 samsung_ds 지원동기)\n"
            "  /인성 [회사] — 인성면접 STAR 기법 평가 (예: /인성 samsung_ds)\n"
            "  /진단     — 이해도 진단 및 시각화\n"
        ),
        chart_png=None,
    )
