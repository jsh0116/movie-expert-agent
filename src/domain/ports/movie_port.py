from abc import ABC, abstractmethod

from ..entities.movie import Movie, MovieCredits


class IMovieRepository(ABC):
    @abstractmethod
    async def get_popular_movies(self) -> list[Movie]: ...

    @abstractmethod
    async def get_movie_details(self, movie_id: int) -> Movie: ...

    @abstractmethod
    async def get_movie_credits(self, movie_id: int) -> MovieCredits: ...
