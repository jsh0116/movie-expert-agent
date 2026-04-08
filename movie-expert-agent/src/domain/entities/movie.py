from pydantic import BaseModel


class Movie(BaseModel):
    id: int
    title: str
    overview: str | None = None
    vote_average: float | None = None
    release_date: str | None = None
    poster_path: str | None = None


class CastMember(BaseModel):
    name: str
    character: str | None = None
    known_for_department: str | None = None


class CrewMember(BaseModel):
    name: str
    job: str | None = None
    department: str | None = None


class MovieCredits(BaseModel):
    movie_id: int
    cast: list[CastMember]
    crew: list[CrewMember]
