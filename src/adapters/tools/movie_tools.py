from agents import function_tool

from ...application.use_cases.movie_use_case import (
    GetMovieCreditsUseCase,
    GetMovieDetailsUseCase,
    GetPopularMoviesUseCase,
)
from ...infrastructure.repositories.movie_repository import MovieAPIRepository

repo = MovieAPIRepository()


@function_tool
async def get_popular_movies() -> str:
    """현재 인기 있는 영화 목록을 가져옵니다. 인기 영화, 최신 영화, 트렌드 영화를 알고 싶을 때 사용합니다."""
    use_case = GetPopularMoviesUseCase(repo)
    movies = await use_case.execute()
    lines = []
    for m in movies:
        rating = f" (평점: {m.vote_average})" if m.vote_average else ""
        lines.append(f"- [{m.id}] {m.title}{rating}")
    return "\n".join(lines)


@function_tool
async def get_movie_details(movie_id: int) -> str:
    """특정 영화의 상세 정보를 조회합니다. 영화 ID를 사용하여 제목, 줄거리, 평점 등을 확인할 수 있습니다.

    Args:
        movie_id: 조회할 영화의 ID
    """
    use_case = GetMovieDetailsUseCase(repo)
    movie = await use_case.execute(movie_id)
    return (
        f"제목: {movie.title}\n"
        f"개봉일: {movie.release_date or 'N/A'}\n"
        f"평점: {movie.vote_average or 'N/A'}\n"
        f"줄거리: {movie.overview or 'N/A'}"
    )


@function_tool
async def get_movie_credits(movie_id: int) -> str:
    """특정 영화의 출연진 및 제작진 정보를 조회합니다. 영화에 누가 출연하는지, 감독이 누구인지 알고 싶을 때 사용합니다.

    Args:
        movie_id: 조회할 영화의 ID
    """
    use_case = GetMovieCreditsUseCase(repo)
    credits = await use_case.execute(movie_id)
    lines = ["## 출연진"]
    for c in credits.cast:
        role = f" ({c.character})" if c.character else ""
        lines.append(f"- {c.name}{role}")
    lines.append("\n## 제작진")
    for c in credits.crew:
        job = f" - {c.job}" if c.job else ""
        lines.append(f"- {c.name}{job}")
    return "\n".join(lines)
