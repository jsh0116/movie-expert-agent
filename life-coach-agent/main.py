import asyncio

import streamlit as st
from agents import Runner

from application.context import AppContext
from application.use_cases import CoachChatUseCase
from domain.entities import CoachingSession
from infrastructure.config import load_run_config
from presentation.agent import create_agent


# ── Streamlit 페이지 설정 ──────────────────────────────────────
st.set_page_config(page_title="Life Coach Agent", page_icon="🌟", layout="centered")
st.title("🌟 Life Coach Agent")
st.caption("동기부여, 습관 형성, 웰니스에 대해 무엇이든 물어보세요!")


# ── 세션 초기화 ────────────────────────────────────────────────
if "agent" not in st.session_state:
    st.session_state["agent"] = create_agent()
if "context" not in st.session_state:
    session = CoachingSession()
    st.session_state["context"] = AppContext(coach_chat=CoachChatUseCase(session))
if "input_items" not in st.session_state:
    st.session_state["input_items"] = []
if "run_config" not in st.session_state:
    st.session_state["run_config"] = load_run_config()


# ── 에이전트 실행 ──────────────────────────────────────────────
async def _run_agent(user_input: str) -> str:
    ctx = st.session_state["context"]
    input_items = ctx.coach_chat.add_user_message(user_input)

    result = await Runner.run(
        st.session_state["agent"],
        input_items,
        run_config=st.session_state["run_config"],
    )

    st.session_state["input_items"] = result.to_input_list()
    ctx.coach_chat.save_assistant_response(result.final_output)
    return result.final_output


# ── 사이드바 ───────────────────────────────────────────────────
with st.sidebar:
    st.header("설정")
    if st.button("🔄 대화 초기화"):
        st.session_state["context"].coach_chat.clear()
        st.session_state["input_items"] = []
        st.rerun()

    st.divider()
    st.markdown(
        "### 질문 예시\n"
        "- 아침마다 일찍 일어나고 싶은데 방법이 있을까요?\n"
        "- 효과적인 습관 만들기 방법을 알려주세요\n"
        "- 스트레스 관리하는 좋은 방법이 있나요?\n"
        "- 생산성을 높이려면 어떻게 해야 할까요?"
    )


# ── 대화 히스토리 표시 ─────────────────────────────────────────
for msg in st.session_state["context"].coach_chat.session.messages:
    with st.chat_message(msg.role):
        st.markdown(msg.content)


# ── 유저 입력 처리 ─────────────────────────────────────────────
if prompt := st.chat_input("메시지를 입력하세요"):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("코치가 답변을 준비하고 있습니다..."):
            response = asyncio.run(_run_agent(prompt))
        st.markdown(response)
