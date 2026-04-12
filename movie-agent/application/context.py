from dataclasses import dataclass

from application.use_cases import (
    GetMovieCreditsUseCase,
    GetMovieDetailsUseCase,
    GetPopularMoviesUseCase,
    GetSimilarMoviesUseCase,
)


@dataclass
class AppContext:
    get_popular_movies: GetPopularMoviesUseCase
    get_movie_details: GetMovieDetailsUseCase
    get_movie_credits: GetMovieCreditsUseCase
    get_similar_movies: GetSimilarMoviesUseCase
