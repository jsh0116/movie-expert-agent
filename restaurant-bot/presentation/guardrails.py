from agents import (
    Agent,
    GuardrailFunctionOutput,
    RunContextWrapper,
    Runner,
    input_guardrail,
)

from presentation.models import InputGuardrailOutput


# ── 입력 가드레일 ───────────────────────────────────────────────
_input_guardrail_agent = Agent(
    name="Input Guardrail",
    model="gpt-4o-mini",
    instructions=(
        "당신은 레스토랑 챗봇의 입력 필터입니다. 사용자 메시지를 분석해서 다음을 판단하세요:\n"
        "- is_off_topic: 레스토랑(메뉴, 주문, 예약, 불만, 영업시간 등)과 무관한 주제면 true\n"
        "- is_inappropriate: 욕설/혐오/성적 표현 등 부적절한 언어가 포함되면 true\n"
        "- reason: 판단 근거를 한국어로 간결히 기술\n"
        "\n"
        "단순 인사(안녕, 감사)는 off-topic이 아닙니다.\n"
        "불만/클레임 메시지는 off-topic이 아닙니다."
    ),
    output_type=InputGuardrailOutput,
)


@input_guardrail
async def restaurant_input_guardrail(
    wrapper: RunContextWrapper,
    agent: Agent,
    input: str | list,
) -> GuardrailFunctionOutput:
    text = input if isinstance(input, str) else str(input)
    result = await Runner.run(_input_guardrail_agent, text)
    output: InputGuardrailOutput = result.final_output
    return GuardrailFunctionOutput(
        output_info=output,
        tripwire_triggered=output.is_off_topic or output.is_inappropriate,
    )

