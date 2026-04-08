from ...domain.entities.movie import Movie, MovieCredits
from ...domain.ports.movie_port import IMovieRepository


class GetPopularMoviesUseCase:
    def __init__(self, repo: IMovieRepository):
        self._repo = repo

    async def execute(self) -> list[Movie]:
        return await self._repo.get_popular_movies()


class GetMovieDetailsUseCase:
    def __init__(self, repo: IMovieRepository):
        self._repo = repo

    async def execute(self, movie_id: int) -> Movie:
        return await self._repo.get_movie_details(movie_id)


class GetMovieCreditsUseCase:
    def __init__(self, repo: IMovieRepository):
        self._repo = repo

    async def execute(self, movie_id: int) -> MovieCredits:
        return await self._repo.get_movie_credits(movie_id)
