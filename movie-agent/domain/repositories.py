from abc import ABC, abstractmethod

from domain.entities import Movie, MovieCredits, MovieDetail


class MovieRepository(ABC):
    @abstractmethod
    async def get_popular(self) -> list[Movie]: ...

    @abstractmethod
    async def get_details(self, movie_id: int) -> MovieDetail: ...

    @abstractmethod
    async def get_credits(self, movie_id: int) -> MovieCredits: ...

    @abstractmethod
    async def get_similar(self, movie_id: int) -> list[Movie]: ...
