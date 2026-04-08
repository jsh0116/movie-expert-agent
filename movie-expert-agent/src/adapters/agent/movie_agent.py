from agents import Agent

from ..tools.movie_tools import get_movie_credits, get_movie_details, get_popular_movies

movie_expert_agent = Agent(
    name="Movie Expert Agent",
    model="gpt-4o-mini",
    instructions="""당신은 영화 전문가 에이전트입니다.
사용자의 질문에 따라 적절한 도구를 선택하여 영화 정보를 제공합니다.

- 인기 영화를 물어보면 get_popular_movies를 사용하세요.
- 특정 영화의 상세 정보를 물어보면 get_movie_details를 사용하세요.
- 특정 영화의 출연진/제작진을 물어보면 get_movie_credits를 사용하세요.

항상 한국어로 친절하게 답변하세요.""",
    tools=[get_popular_movies, get_movie_details, get_movie_credits],
)
