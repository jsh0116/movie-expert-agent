from agents import Agent, AgentHooks, RunContextWrapper, Tool

from application.context import AppContext
from presentation.tools import (
    get_movie_credits,
    get_movie_details,
    get_popular_movies,
    get_similar_movies,
)

SYSTEM_PROMPT = """\
당신은 영화 전문가 AI 에이전트입니다.
사용자의 영화 관련 질문에 친절하고 상세하게 답변합니다.

할 수 있는 일:
- 현재 인기 영화 목록 조회 (get_popular_movies)
- 특정 영화의 상세 정보 조회 (get_movie_details)
- 영화 출연진/제작진 정보 조회 (get_movie_credits)
- 유사한 영화 추천 (get_similar_movies)

규칙:
- 항상 한국어로 답변하세요.
- 영화 정보를 제공할 때는 반드시 도구를 사용하세요.
- 사용자가 영화 이름을 언급하면, 먼저 인기 영화 목록에서 해당 영화를 찾아 ID를 확인하세요.
- 영화 ID를 알고 있다면 상세 정보, 출연진, 유사 영화 등을 조회할 수 있습니다.
"""


class ToolCallHooks(AgentHooks[AppContext]):
    async def on_tool_start(
        self,
        context: RunContextWrapper[AppContext],
        agent: Agent[AppContext],
        tool: Tool,
    ):
        print(f"  [{tool.name}() 호출 중...]")

    async def on_tool_end(
        self,
        context: RunContextWrapper[AppContext],
        agent: Agent[AppContext],
        tool: Tool,
        result: str,
    ):
        print(f"  [{tool.name}() 완료]")


def create_agent() -> Agent[AppContext]:
    return Agent(
        name="Movie Expert",
        model="gpt-4o-mini",
        instructions=SYSTEM_PROMPT,
        tools=[
            get_popular_movies,
            get_movie_details,
            get_movie_credits,
            get_similar_movies,
        ],
        hooks=ToolCallHooks(),
    )
