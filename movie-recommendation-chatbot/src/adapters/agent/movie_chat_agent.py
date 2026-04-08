from agents import Agent, Runner, RunConfig
from agents.models.openai_provider import OpenAIProvider

from src.domain.ports.chat_port import IChatAgent
from src.infrastructure.config.env_config import AI_BASE_URL

run_config = RunConfig(
    model_provider=OpenAIProvider(base_url=AI_BASE_URL),
    tracing_disabled=True,
)

movie_chatbot_agent = Agent(
    name="Movie Recommendation Chatbot",
    model="gpt-4o-mini",
    instructions="""당신은 영화 추천 챗봇입니다.

대화를 통해 다음 정보를 기억하고 활용하세요:
1. 사용자가 좋아하는 장르
2. 사용자가 이미 본 영화

규칙:
- 이미 본 영화는 절대 추천하지 마세요.
- 추천 시 사용자의 취향(장르)을 반영하세요.
- 사용자가 이전 대화 내용을 물어보면 대화 기록을 기반으로 정확히 답변하세요.
- 항상 한국어로 친절하게 답변하세요.
- 답변은 간결하게 해주세요.""",
)


class OpenAIChatAgent(IChatAgent):
    """OpenAI Agents SDK 기반 IChatAgent 구현."""

    async def run(self, messages: list[dict]) -> str:
        result = await Runner.run(
            movie_chatbot_agent,
            messages,
            run_config=run_config,
        )
        return result.final_output
