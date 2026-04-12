from agents import RunContextWrapper, function_tool

from application.context import AppContext


@function_tool
async def get_popular_movies(ctx: RunContextWrapper[AppContext]) -> str:
    """현재 인기 있는 영화 목록을 조회합니다."""
    movies = await ctx.context.get_popular_movies.execute()
    lines = []
    for i, m in enumerate(movies, 1):
        lines.append(
            f"{i}. {m.title} (ID: {m.id}) - 평점: {m.vote_average}, 개봉일: {m.release_date}"
        )
    return "\n".join(lines)


@function_tool
async def get_movie_details(ctx: RunContextWrapper[AppContext], movie_id: int) -> str:
    """영화 ID로 상세 정보를 조회합니다.

    Args:
        movie_id: 조회할 영화의 ID
    """
    d = await ctx.context.get_movie_details.execute(movie_id)
    return (
        f"제목: {d.title}\n"
        f"태그라인: {d.tagline}\n"
        f"개봉일: {d.release_date}\n"
        f"평점: {d.vote_average}\n"
        f"장르: {', '.join(d.genres)}\n"
        f"런타임: {d.runtime}분\n"
        f"상태: {d.status}\n"
        f"언어: {d.original_language}\n"
        f"예산: ${d.budget:,}\n"
        f"수익: ${d.revenue:,}\n"
        f"줄거리: {d.overview}"
    )


@function_tool
async def get_movie_credits(ctx: RunContextWrapper[AppContext], movie_id: int) -> str:
    """영화의 출연진 및 제작진 정보를 조회합니다.

    Args:
        movie_id: 조회할 영화의 ID
    """
    credits = await ctx.context.get_movie_credits.execute(movie_id)
    lines = ["[출연진]"]
    for c in credits.cast[:10]:
        lines.append(f"  - {c.name} ({c.character})")
    lines.append("\n[제작진]")
    for c in credits.crew[:5]:
        lines.append(f"  - {c.name} ({c.job})")
    return "\n".join(lines)


@function_tool
async def get_similar_movies(ctx: RunContextWrapper[AppContext], movie_id: int) -> str:
    """특정 영화와 유사한 영화를 추천합니다.

    Args:
        movie_id: 기준 영화의 ID
    """
    movies = await ctx.context.get_similar_movies.execute(movie_id)
    lines = []
    for i, m in enumerate(movies, 1):
        lines.append(
            f"{i}. {m.title} (ID: {m.id}) - 평점: {m.vote_average}, 개봉일: {m.release_date}"
        )
    return "\n".join(lines) if lines else "유사한 영화를 찾을 수 없습니다."
