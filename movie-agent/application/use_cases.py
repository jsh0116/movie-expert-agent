from domain.entities import Movie, MovieCredits, MovieDetail
from domain.repositories import MovieRepository


class GetPopularMoviesUseCase:
    def __init__(self, repository: MovieRepository):
        self._repository = repository

    async def execute(self) -> list[Movie]:
        return await self._repository.get_popular()


class GetMovieDetailsUseCase:
    def __init__(self, repository: MovieRepository):
        self._repository = repository

    async def execute(self, movie_id: int) -> MovieDetail:
        return await self._repository.get_details(movie_id)


class GetMovieCreditsUseCase:
    def __init__(self, repository: MovieRepository):
        self._repository = repository

    async def execute(self, movie_id: int) -> MovieCredits:
        return await self._repository.get_credits(movie_id)


class GetSimilarMoviesUseCase:
    def __init__(self, repository: MovieRepository):
        self._repository = repository

    async def execute(self, movie_id: int) -> list[Movie]:
        return await self._repository.get_similar(movie_id)
