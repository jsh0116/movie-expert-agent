import httpx

from ...domain.entities.movie import CastMember, CrewMember, Movie, MovieCredits
from ...domain.ports.movie_port import IMovieRepository
from ..config.env_config import API_BASE_URL


class MovieAPIRepository(IMovieRepository):
    def __init__(self):
        self._base_url = API_BASE_URL

    async def get_popular_movies(self) -> list[Movie]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self._base_url}/movies")
            resp.raise_for_status()
            data = resp.json()
            return [Movie(**m) for m in data]

    async def get_movie_details(self, movie_id: int) -> Movie:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self._base_url}/movies/{movie_id}")
            resp.raise_for_status()
            return Movie(**resp.json())

    async def get_movie_credits(self, movie_id: int) -> MovieCredits:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self._base_url}/movies/{movie_id}/credits")
            resp.raise_for_status()
            data = resp.json()
            # API returns a flat list of cast members (no crew)
            items = data if isinstance(data, list) else data.get("cast", [])
            cast = [CastMember(**c) for c in items[:10]]
            return MovieCredits(movie_id=movie_id, cast=cast, crew=[])
