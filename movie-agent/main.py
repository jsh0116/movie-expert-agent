import asyncio
import os

from dotenv import load_dotenv

from agents import Runner, RunConfig
from agents.models.openai_provider import OpenAIProvider
from application.context import AppContext
from application.use_cases import (
    GetMovieCreditsUseCase,
    GetMovieDetailsUseCase,
    GetPopularMoviesUseCase,
    GetSimilarMoviesUseCase,
)
from infrastructure.api_movie_repository import ApiMovieRepository
from presentation.agent import create_agent


def build_context() -> AppContext:
    """DI Composition Root: 의존성을 조립하고 AppContext를 반환합니다."""
    repo = ApiMovieRepository()
    return AppContext(
        get_popular_movies=GetPopularMoviesUseCase(repo),
        get_movie_details=GetMovieDetailsUseCase(repo),
        get_movie_credits=GetMovieCreditsUseCase(repo),
        get_similar_movies=GetSimilarMoviesUseCase(repo),
    )


def build_run_config() -> RunConfig:
    """RunConfig를 생성합니다. AI_BASE_URL이 있으면 커스텀 provider를 사용합니다."""
    base_url = os.getenv("AI_BASE_URL")
    if base_url:
        return RunConfig(
            model_provider=OpenAIProvider(
                base_url=base_url,
                use_responses=False,
            ),
            tracing_disabled=True,
        )
    return RunConfig()


async def main():
    load_dotenv()

    context = build_context()
    agent = create_agent()
    run_config = build_run_config()

    print("=" * 50)
    print("  Movie Expert Agent")
    print("  영화에 대해 무엇이든 물어보세요!")
    print("  종료: quit / exit / q")
    print("=" * 50)
    print()

    input_items: list = []

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n종료합니다.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("종료합니다.")
            break

        input_items.append({"role": "user", "content": user_input})

        try:
            result = await Runner.run(
                agent,
                input_items,
                context=context,
                run_config=run_config,
            )
            print(f"\nAgent: {result.final_output}\n")
            input_items = result.to_input_list()
        except Exception as e:
            print(f"\n오류 발생: {e}\n")


if __name__ == "__main__":
    asyncio.run(main())
