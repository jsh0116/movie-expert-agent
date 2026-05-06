"""Orchestrator node — parses commands and routes to the right sub-agent."""
from __future__ import annotations

from langchain_core.messages import HumanMessage
from langgraph.graph import END

from semiconductor.adapters.state import InterviewState

_INTERVIEW_TRIGGERS = {"/인터뷰", "/interview"}
_QA_TRIGGERS = {"/qa", "/코칭"}
_DIAGNOSTIC_TRIGGERS = {"/진단", "/diagnostic"}


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
            return {"mode": "interview"}

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

    return {}


def route_from_orchestrator(state: InterviewState) -> str:
    mode = state.get("mode", "idle")
    if mode == "interview":
        return "mock_interviewer"
    if mode == "qa":
        return "qa_coach"
    if mode == "diagnostic":
        return "diagnostic"
    return END
