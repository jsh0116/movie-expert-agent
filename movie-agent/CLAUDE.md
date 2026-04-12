# CLAUDE.md

## Project Overview

OpenAI Agents SDK + Clean Architecture로 구현한 영화 전문가 에이전트. 외부 영화 API(`https://nomad-movies.nomadcoders.workers.dev`)를 호출하여 인기 영화, 상세 정보, 출연진/제작진, 유사 영화를 조회한다.

## Commands

```bash
uv sync                        # 의존성 설치
uv run python main.py          # CLI 실행
uv run jupyter notebook main.ipynb  # 노트북 실행
```

## Architecture

Clean Architecture 4계층 구조:

- **Domain** (`domain/`) — dataclass 엔티티(`Movie`, `MovieDetail`, `CastMember`, `CrewMember`, `MovieCredits`)와 포트(`MovieRepository` ABC)
- **Application** (`application/`) — 유스케이스 클래스(`GetPopularMoviesUseCase` 등). 포트를 주입받아 실행. `AppContext`로 DI 컨테이너 역할
- **Infrastructure** (`infrastructure/`) — `ApiMovieRepository`(httpx AsyncClient로 외부 API 호출)
- **Presentation** (`presentation/`) — OpenAI Agents SDK 통합. `@function_tool` 데코레이터로 도구 4개 정의, `Agent` 객체 생성, `ToolCallHooks`로 도구 호출 로깅

`main.py`가 Composition Root로 모든 의존성을 조립한다.

## Key Configuration

- `.env`에 `OPENAI_API_KEY`와 `AI_BASE_URL` 설정 필요
- `AI_BASE_URL`이 있으면 `OpenAIProvider(base_url=..., use_responses=False)`로 chat completions API 사용
- `RunConfig`에 `tracing_disabled=True` 설정하여 tracing 인증 에러 방지
- 에이전트 모델: `gpt-4o-mini`, 응답 언어: 한국어

## Tools

| 도구 | API 엔드포인트 | 설명 |
|------|---------------|------|
| `get_popular_movies` | `/movies` | 인기 영화 목록 |
| `get_movie_details(movie_id)` | `/movies/:id` | 영화 상세 정보 |
| `get_movie_credits(movie_id)` | `/movies/:id/credits` | 출연진/제작진 |
| `get_similar_movies(movie_id)` | `/movies/:id/similar` | 유사한 영화 |
