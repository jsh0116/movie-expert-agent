from agents import Agent, AgentHooks, RunContextWrapper, Tool, handoff
from agents.extensions import handoff_filters
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

from presentation.guardrails import restaurant_input_guardrail
from presentation.models import HandoffData
from presentation.tools import (
    get_menu,
    make_reservation,
    place_order,
)


MODEL = "gpt-4o-mini"


class ToolCallHooks(AgentHooks):
    async def on_tool_start(
        self, context: RunContextWrapper, agent: Agent, tool: Tool
    ) -> None:
        print(f"  [{agent.name} → {tool.name} 호출 중...]")

    async def on_tool_end(
        self, context: RunContextWrapper, agent: Agent, tool: Tool, result: str
    ) -> None:
        print(f"  [{agent.name} → {tool.name} 완료]")

    async def on_handoff(
        self, context: RunContextWrapper, agent: Agent, source: Agent
    ) -> None:
        print(f"  [핸드오프: {source.name} → {agent.name}]")


# ── Menu Agent ─────────────────────────────────────────────────
menu_agent = Agent(
    name="Menu_Agent",
    model=MODEL,
    instructions=(
        RECOMMENDED_PROMPT_PREFIX
        + "\n"
        + "당신은 레스토랑의 메뉴 전문 에이전트입니다. "
        "고객에게 메뉴를 안내하고, 재료와 가격, 추천 메뉴를 설명합니다. "
        "반드시 get_menu 도구를 사용해 실제 메뉴를 확인한 뒤 답하세요. "
        "친근하고 전문적인 한국어로 응답합니다."
    ),
    tools=[get_menu],
    hooks=ToolCallHooks(),
)


# ── Reservation Agent ──────────────────────────────────────────
reservation_agent = Agent(
    name="Reservation_Agent",
    model=MODEL,
    instructions=(
        RECOMMENDED_PROMPT_PREFIX
        + "\n"
        + "당신은 레스토랑 예약 전문 에이전트입니다. "
        "예약을 원하는 고객에게 이름, 날짜(YYYY-MM-DD), 시간(HH:MM), 인원을 "
        "확인한 후 make_reservation 도구로 예약을 생성합니다. "
        "누락된 정보는 친절하게 되물어보세요. 한국어로 응답합니다."
    ),
    tools=[make_reservation],
    hooks=ToolCallHooks(),
)


# ── Order Agent ────────────────────────────────────────────────
order_agent = Agent(
    name="Order_Agent",
    model=MODEL,
    instructions=(
        RECOMMENDED_PROMPT_PREFIX
        + "\n"
        + "당신은 레스토랑 주문 전문 에이전트입니다. "
        "고객의 주문을 받아 place_order 도구로 처리합니다. "
        "메뉴 ID와 수량이 필요하며, 불확실할 때는 get_menu 도구로 먼저 확인하세요. "
        "한국어로 응답합니다."
    ),
    tools=[get_menu, place_order],
    hooks=ToolCallHooks(),
)


# ── Handoff Factory ────────────────────────────────────────────
def _make_handoff(target_agent: Agent):
    def on_handoff_callback(
        wrapper: RunContextWrapper, input_data: HandoffData
    ) -> None:
        print(
            f"  [핸드오프 트리거: {target_agent.name} "
            f"(type={input_data.issue_type}, reason={input_data.reason})]"
        )

    return handoff(
        agent=target_agent,
        on_handoff=on_handoff_callback,
        input_type=HandoffData,
        input_filter=handoff_filters.remove_all_tools,
    )


# ── Triage Agent ───────────────────────────────────────────────
TRIAGE_INSTRUCTIONS = (
    "당신은 레스토랑 봇의 전용 라우터입니다. 당신의 유일한 역할은 고객 문의를 "
    "적절한 전문 에이전트로 핸드오프하는 것입니다.\n"
    "\n"
    "핸드오프 규칙:\n"
    "- 메뉴/재료/가격/채식/알레르기/추천 문의 → Menu Agent로 핸드오프\n"
    "- 예약 관련 문의 → Reservation Agent로 핸드오프\n"
    "- 주문 관련 문의 → Order Agent로 핸드오프\n"
    "\n"
    "당신은 어떤 질문에도 직접 답하지 않습니다. "
    "반드시 적합한 전문 에이전트로 핸드오프하세요. 텍스트 응답을 생성하지 마세요."
)


def create_triage_agent() -> Agent:
    triage = Agent(
        name="Triage_Agent",
        model=MODEL,
        instructions=TRIAGE_INSTRUCTIONS,
        handoffs=[
            _make_handoff(menu_agent),
            _make_handoff(reservation_agent),
            _make_handoff(order_agent),
        ],
        input_guardrails=[restaurant_input_guardrail],
        hooks=ToolCallHooks(),
    )

    return triage
