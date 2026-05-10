"""Orchestrator node — parses commands and routes to the right sub-agent."""
from __future__ import annotations

from langchain_core.messages import HumanMessage
from langgraph.graph import END

from semiconductor.adapters.state import InterviewState

_INTERVIEW_TRIGGERS = {"/인터뷰", "/interview"}
_QA_TRIGGERS = {"/qa", "/코칭"}
_DIAGNOSTIC_TRIGGERS = {"/진단", "/diagnostic"}
_ESSAY_TRIGGERS = {"/자소서", "/essay"}


def orchestrator_node(state: InterviewState) -> dict:
    """Parse the latest human message for mode-switch commands."""
    msgs = state.get("messages", [])
    human_msgs = [m for m in msgs if isinstance(m, HumanMessage)]
    if not human_msgs:
        return {}

    text = human_msgs[-1].content.strip()
    lower = text.lower()

    for cmd in _INTERVIEW_TRIGGERS:
        if lower.startswith(cmd):
            return {"mode": "interview", "interview_phase": "present"}

    for cmd in _QA_TRIGGERS:
        if lower.startswith(cmd):
            if state.get("mode") == "interview" and state.get("current_question_text"):
                return {
                    "display_output": (
                        "⚠️ 현재 면접 진행 중입니다.\n"
                        "면접을 완료한 후 /qa를 사용해주세요.\n"
                        "면접을 중단하려면 /진단 으로 결과를 먼저 확인하세요."
                    )
                }
            topic = text[len(cmd):].strip()
            updates: dict = {"mode": "qa", "hint_count": 0}
            if topic:
                updates["current_qa_topic"] = topic
            return updates

    for cmd in _DIAGNOSTIC_TRIGGERS:
        if lower.startswith(cmd):
            return {"mode": "diagnostic"}

    for cmd in _ESSAY_TRIGGERS:
        if lower.startswith(cmd):
            # /자소서 [회사] [항목] — args 파싱
            args = text[len(cmd):].strip().split(maxsplit=1)
            updates: dict = {"mode": "essay", "essay_phase": "present"}
            if len(args) >= 2:
                updates["essay_company"] = args[0]
                updates["essay_item"] = args[1]
            else:
                # 인자 부족 — present_node가 사용 가이드 표시
                updates["essay_company"] = None
                updates["essay_item"] = None
            return updates

    return {}


def route_from_orchestrator(state: InterviewState) -> str:
    mode = state.get("mode", "idle")
    if mode == "interview":
        # phase 기반 분기: present(질문 출제) vs evaluate(답변 평가)
        phase = state.get("interview_phase", "present")
        return "mock_present" if phase == "present" else "mock_evaluate"
    if mode == "essay":
        # phase 기반: present(prompt 표시) vs evaluate(자소서 평가)
        phase = state.get("essay_phase", "present")
        return "essay_present" if phase == "present" else "essay_evaluate"
    if mode == "qa":
        return "qa_coach"
    if mode == "diagnostic":
        return "diagnostic"
    return END
