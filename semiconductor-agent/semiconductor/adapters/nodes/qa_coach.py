"""Q&A Coach with ReAct tool-calling — Socratic method + tool augmentation.

Loop:
  qa_coach (LLM with tools bound) ──tool_calls?──▶ coach_tools (ToolNode) ──▶ qa_coach
                                  └─no──▶ END

Provider: anthropic:claude-sonnet-4-6 by default (한국어 + tool use 강점).
LLM_MODEL_COACH env var로 자유롭게 변경 가능.
"""
from __future__ import annotations

import os

from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langgraph.graph import END
from langgraph.prebuilt import ToolNode

from semiconductor.adapters.state import InterviewState
from semiconductor.adapters.tools import COACH_TOOLS


def _resolve_coach_model() -> str:
    """tier 또는 명시 env로 결정. llm_service의 _resolve_model_spec과 동일 정책."""
    from semiconductor.infrastructure.llm.tiers import model_for_role
    explicit = os.getenv("LLM_MODEL_COACH")
    if explicit:
        return explicit if ":" in explicit else f"openai:{explicit}"
    tier = os.getenv("LLM_TIER", "premium")
    return model_for_role(tier, "coach")

_COACH_RULES = {
    0: "선행 지식을 파악하세요. '어디까지 알고 있어요?' 같은 탐색 질문으로 시작. 절대 직접 답하지 마세요.",
    1: "힌트 1회차: 핵심 키워드나 유추(analogy) 하나만 제시. 직접 답은 주지 마세요.",
    2: "힌트 2회차: 관련 물리 원리나 수식 힌트를 줄 수 있습니다. 아직 직접 답은 주지 마세요.",
    3: "힌트 3회차 초과: 이제 명확하게 설명 (3-5문장). 설명 후 이해 확인 질문 1개 추가.",
}

_COACH_SYSTEM = """당신은 반도체 공학 전문 학습 코치입니다. 소크라테스 방식으로 가르칩니다.

현재 학습 주제: {topic}
현재 힌트 횟수: {hint_count}/3

규칙:
{rules}

도구 사용 가이드:
- 사용자가 "최근 X 동향" / "요즘 X" / "현재 X" 같이 최신 정보를 물으면 → industry_trend_search
- 사용자가 구체적 수치 계산을 요청하면 (예: "tox=10nm일 때 Vth?") → calculate_* 도구
- 단순 개념 설명이면 도구 호출 없이 한국어로 직접 답변

도구 결과를 받으면 이를 자연스러운 한국어 코칭 문장에 녹여 답변하세요."""


def _build_system(state: InterviewState) -> str:
    topic = state.get("current_qa_topic") or "반도체 기초"
    hint = state.get("hint_count", 0)
    rule_key = min(hint, 3)
    return _COACH_SYSTEM.format(topic=topic, hint_count=hint, rules=_COACH_RULES[rule_key])


def _to_chat_messages(msgs: list[BaseMessage]) -> list[dict]:
    """LangChain BaseMessage → ChatOpenAI invoke format."""
    out: list[dict] = []
    for m in msgs[-15:]:  # 최근 15개만 (컨텍스트 부풀림 방지)
        if isinstance(m, HumanMessage):
            out.append({"role": "user", "content": m.content})
        elif isinstance(m, AIMessage):
            entry: dict = {"role": "assistant", "content": m.content or ""}
            if m.tool_calls:
                entry["tool_calls"] = [
                    {"id": tc["id"], "type": "function",
                     "function": {"name": tc["name"], "arguments": str(tc["args"])}}
                    for tc in m.tool_calls
                ]
            out.append(entry)
        elif isinstance(m, ToolMessage):
            out.append({"role": "tool", "tool_call_id": m.tool_call_id, "content": m.content})
    return out


def qa_coach_node(state: InterviewState) -> dict:
    """Coach LLM with bound tools. May emit tool_calls (loop) or final text (END)."""
    topic = state.get("current_qa_topic") or ""
    if not topic:
        return {
            "display_output": "학습할 주제를 알려주세요. 예시: `/qa TSV 구조`",
        }

    model_spec = _resolve_coach_model()
    kwargs: dict = {"temperature": 0.5}
    base_url = os.getenv("AI_BASE_URL")
    if base_url and model_spec.startswith("openai:"):
        kwargs["base_url"] = base_url
    llm = init_chat_model(model_spec, **kwargs).bind_tools(COACH_TOOLS)

    chat_msgs: list[dict] = [{"role": "system", "content": _build_system(state)}]
    chat_msgs.extend(_to_chat_messages(state.get("messages", [])))

    response: AIMessage = llm.invoke(chat_msgs)

    update: dict = {"messages": [response]}

    # tool_calls가 없을 때만 hint_count 증가 + 화면 출력
    if not response.tool_calls:
        new_hint = min(state.get("hint_count", 0) + 1, 4)
        update["hint_count"] = new_hint
        update["display_output"] = response.content or ""

    return update


def route_after_coach(state: InterviewState) -> str:
    """qa_coach 응답에 tool_calls 있으면 tools 실행, 없으면 END."""
    msgs = state.get("messages", [])
    if not msgs:
        return END
    last = msgs[-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "coach_tools"
    return END


# ToolNode — COACH_TOOLS의 모든 @tool을 자동 실행 + ToolMessage로 반환
coach_tools_node = ToolNode(COACH_TOOLS)
