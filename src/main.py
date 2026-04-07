import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

from agents import Runner, RunConfig
from agents.models.openai_provider import OpenAIProvider

from src.adapters.agent.movie_agent import movie_expert_agent
from src.infrastructure.config.env_config import AI_BASE_URL

run_config = RunConfig(
    model_provider=OpenAIProvider(base_url=AI_BASE_URL),
    tracing_disabled=True,
)


async def main():
    print("영화 전문가 에이전트입니다. 종료하려면 'q'를 입력하세요.\n")
    while True:
        query = input("질문을 입력하세요: ").strip()
        if not query or query.lower() == "q":
            print("종료합니다.")
            break
        result = await Runner.run(movie_expert_agent, query, run_config=run_config)
        print(f"\n{result.final_output}\n")


if __name__ == "__main__":
    asyncio.run(main())
