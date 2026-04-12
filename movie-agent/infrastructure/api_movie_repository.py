import httpx

from domain.entities import CastMember, CrewMember, Movie, MovieCredits, MovieDetail
from domain.repositories import MovieRepository

BASE_URL = "https://nomad-movies.nomadcoders.workers.dev"


class ApiMovieRepository(MovieRepository):

    async def get_popular(self) -> list[Movie]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{BASE_URL}/movies")
            resp.raise_for_status()
            data = resp.json()
            items = data if isinstance(data, list) else data.get("results", [])
            return [self._to_movie(item) for item in items]

    async def get_details(self, movie_id: int) -> MovieDetail:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{BASE_URL}/movies/{movie_id}")
            resp.raise_for_status()
            data = resp.json()
            return MovieDetail(
                id=data.get("id", movie_id),
                title=data.get("title", ""),
                overview=data.get("overview", ""),
                poster_path=data.get("poster_path"),
                vote_average=data.get("vote_average", 0),
                release_date=data.get("release_date", ""),
                runtime=data.get("runtime"),
                genres=[g.get("name", "") for g in data.get("genres", [])],
                tagline=data.get("tagline", ""),
                budget=data.get("budget", 0),
                revenue=data.get("revenue", 0),
                original_language=data.get("original_language", ""),
                status=data.get("status", ""),
            )

    async def get_credits(self, movie_id: int) -> MovieCredits:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{BASE_URL}/movies/{movie_id}/credits")
            resp.raise_for_status()
            data = resp.json()
            # API returns a flat list of cast/crew members
            items = data if isinstance(data, list) else data.get("cast", [])
            cast = [
                CastMember(
                    name=c.get("name", ""),
                    character=c.get("character", ""),
                )
                for c in items
                if c.get("character")
            ]
            crew = [
                CrewMember(
                    name=c.get("name", ""),
                    job=c.get("known_for_department", ""),
                    department=c.get("known_for_department", ""),
                )
                for c in items
                if not c.get("character")
            ]
            return MovieCredits(movie_id=movie_id, cast=cast, crew=crew)

    async def get_similar(self, movie_id: int) -> list[Movie]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{BASE_URL}/movies/{movie_id}/similar")
            resp.raise_for_status()
            data = resp.json()
            items = data if isinstance(data, list) else data.get("results", [])
            return [self._to_movie(item) for item in items]

    @staticmethod
    def _to_movie(data: dict) -> Movie:
        return Movie(
            id=data.get("id", 0),
            title=data.get("title", ""),
            overview=data.get("overview", ""),
            poster_path=data.get("poster_path"),
            vote_average=data.get("vote_average", 0),
            release_date=data.get("release_date", ""),
        )
