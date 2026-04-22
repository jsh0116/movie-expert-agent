import asyncio

import streamlit as st
from agents import InputGuardrailTripwireTriggered, Runner

from application.context import AppContext
from application.use_cases import (
    GetMenuUseCase,
    MakeReservationUseCase,
    PlaceOrderUseCase,
)
from infrastructure.config import load_run_config
from infrastructure.memory_repositories import (
    InMemoryMenuRepository,
    InMemoryOrderRepository,
    InMemoryReservationRepository,
)
from presentation.agents import create_triage_agent


# ── Streamlit 페이지 설정 ──────────────────────────────────────
st.set_page_config(page_title="Restaurant Bot", page_icon="🍽️", layout="centered")
st.title("🍽️ Restaurant Bot")
st.caption("메뉴, 예약, 주문을 도와드립니다.")


# ── 세션 초기화 ────────────────────────────────────────────────
def _build_context() -> AppContext:
    menu_repo = InMemoryMenuRepository()
    return AppContext(
        get_menu=GetMenuUseCase(menu_repo),
        make_reservation=MakeReservationUseCase(InMemoryReservationRepository()),
        place_order=PlaceOrderUseCase(menu_repo, InMemoryOrderRepository()),
    )


if "triage_agent" not in st.session_state:
    st.session_state["triage_agent"] = create_triage_agent()
if "current_agent" not in st.session_state:
    st.session_state["current_agent"] = st.session_state["triage_agent"]
if "context" not in st.session_state:
    st.session_state["context"] = _build_context()
if "input_items" not in st.session_state:
    st.session_state["input_items"] = []
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "run_config" not in st.session_state:
    st.session_state["run_config"] = load_run_config()


# ── 에이전트 실행 ──────────────────────────────────────────────
async def _run_agent(user_input: str) -> tuple[str, str]:
    items = st.session_state["input_items"] + [{"role": "user", "content": user_input}]
    try:
        result = await Runner.run(
            st.session_state["triage_agent"],
            items,
            context=st.session_state["context"],
            run_config=st.session_state["run_config"],
        )
    except InputGuardrailTripwireTriggered as e:
        info = e.guardrail_result.output.output_info
        reason = getattr(info, "reason", "부적절한 입력")
        return (
            f"죄송하지만 레스토랑 관련 질문에만 답변드리고 있어요.\n\n_사유: {reason}_",
            "Guardrail",
        )

    st.session_state["input_items"] = result.to_input_list()
    st.session_state["current_agent"] = result.last_agent
    return result.final_output, result.last_agent.name


# ── 사이드바 ───────────────────────────────────────────────────
with st.sidebar:
    st.header("설정")
    st.markdown(f"**현재 에이전트**: `{st.session_state['current_agent'].name}`")

    if st.button("🔄 대화 초기화"):
        st.session_state["input_items"] = []
        st.session_state["messages"] = []
        st.session_state["current_agent"] = st.session_state["triage_agent"]
        st.rerun()

    st.divider()
    st.markdown(
        "### 질문 예시\n"
        "- 메뉴 뭐 있어요?\n"
        "- 채식 메뉴 있나요?\n"
        "- 내일 7시에 2명 예약할게요\n"
        "- 파스타 하나, 티라미수 하나 주문할게요\n"
        "- 인생의 의미가 뭘까? (← 가드레일 작동)"
    )


# ── 대화 히스토리 표시 ─────────────────────────────────────────
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant" and msg.get("agent"):
            st.caption(f"🤖 {msg['agent']}")
        st.markdown(msg["content"])


# ── 유저 입력 처리 ─────────────────────────────────────────────
if prompt := st.chat_input("메시지를 입력하세요"):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("응답 준비 중..."):
            response, agent_name = asyncio.run(_run_agent(prompt))
        st.caption(f"🤖 {agent_name}")
        st.markdown(response)
        st.session_state["messages"].append(
            {"role": "assistant", "content": response, "agent": agent_name}
        )
