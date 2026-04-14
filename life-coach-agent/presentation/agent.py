from agents import Agent, AgentHooks, RunContextWrapper, Tool, WebSearchTool

from presentation.tools import get_coaching_tip

SYSTEM_PROMPT = """\
당신은 전문 라이프 코치입니다. 사용자의 삶의 질을 높이기 위해 동기부여, 습관 형성, \
웰니스, 생산성, 마인드풀니스에 대한 조언을 제공합니다.

## 역할
- 사용자의 고민을 경청하고 공감하며 응답합니다
- 웹 검색을 활용하여 최신 동기부여 콘텐츠, 팁, 습관 관리 방법을 찾아 제공합니다
- 실천 가능한 구체적인 조언을 제공합니다
- 한국어로 응답합니다

## 응답 가이드라인
1. 먼저 사용자의 상황에 공감을 표현하세요
2. 관련 정보가 필요하면 웹 검색을 활용하세요
3. 검색 결과를 바탕으로 실천 가능한 조언을 3-5개 제시하세요
4. 격려와 응원의 메시지로 마무리하세요

## 전문 분야
- 동기부여 및 목표 설정
- 습관 형성 및 관리 (습관 스태킹, 2분 규칙 등)
- 건강 및 웰니스 (수면, 운동, 식단)
- 시간 관리 및 생산성
- 스트레스 관리 및 마인드풀니스
- 자기계발 및 성장 마인드셋
"""


class ToolCallHooks(AgentHooks):
    async def on_tool_start(
        self, context: RunContextWrapper, agent: Agent, tool: Tool
    ) -> None:
        print(f"  [{tool.name} 호출 중...]")

    async def on_tool_end(
        self, context: RunContextWrapper, agent: Agent, tool: Tool, result: str
    ) -> None:
        print(f"  [{tool.name} 완료]")


def create_agent() -> Agent:
    return Agent(
        name="Life Coach",
        model="gpt-4o-mini",
        instructions=SYSTEM_PROMPT,
        tools=[
            WebSearchTool(),
            get_coaching_tip,
        ],
        hooks=ToolCallHooks(),
    )
