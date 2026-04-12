from dataclasses import dataclass, field


@dataclass
class Movie:
    id: int
    title: str
    overview: str
    poster_path: str | None = None
    vote_average: float = 0.0
    release_date: str = ""


@dataclass
class MovieDetail:
    id: int
    title: str
    overview: str
    poster_path: str | None = None
    vote_average: float = 0.0
    release_date: str = ""
    runtime: int | None = None
    genres: list[str] = field(default_factory=list)
    tagline: str = ""
    budget: int = 0
    revenue: int = 0
    original_language: str = ""
    status: str = ""


@dataclass
class CastMember:
    name: str
    character: str


@dataclass
class CrewMember:
    name: str
    job: str
    department: str = ""


@dataclass
class MovieCredits:
    movie_id: int
    cast: list[CastMember] = field(default_factory=list)
    crew: list[CrewMember] = field(default_factory=list)
