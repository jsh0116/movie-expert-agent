# Movie Agent

OpenAI Agents SDK + Clean Architecture 기반 영화 전문가 에이전트

## 기능

- 현재 인기 영화 목록 조회
- 영화 상세 정보 조회 (장르, 런타임, 평점, 줄거리 등)
- 영화 출연진/제작진 정보 조회
- 유사한 영화 추천

## Architecture

```
movie-agent/
├── domain/                        # 비즈니스 규칙 (순수 Python, 외부 의존성 없음)
│   ├── entities.py                # Movie, MovieDetail, MovieCredits
│   └── repositories.py            # MovieRepository (ABC 인터페이스)
├── application/                   # 유스케이스 조율
│   ├── context.py                 # AppContext (DI Container)
│   └── use_cases.py               # GetPopularMovies, GetMovieDetails 등
├── infrastructure/                # 외부 시스템 구현체
│   └── api_movie_repository.py    # httpx 기반 API 호출
├── presentation/                  # 사용자 인터페이스
│   ├── agent.py                   # Agent 정의 + ToolCallHooks
│   └── tools.py                   # @function_tool 4개
├── main.py                        # CLI 진입점
└── main.ipynb                     # Jupyter Notebook
```

의존성 방향: `Presentation → Application → Domain ← Infrastructure`

## 설치 및 실행

```bash
uv sync
```

### CLI

```bash
uv run python main.py
```

### Jupyter Notebook

```bash
uv run jupyter notebook main.ipynb
```

또는 VSCode에서 `main.ipynb`을 열고 커널을 `Movie Agent (.venv)`로 선택

## 환경 변수

`.env` 파일에 설정:

```
OPENAI_API_KEY=your-api-key
AI_BASE_URL=https://your-api-endpoint/v1   # 선택: 커스텀 OpenAI 호환 엔드포인트
```

## API

기본 URL: `https://nomad-movies.nomadcoders.workers.dev`

| 엔드포인트 | 도구 | 설명 |
|------------|------|------|
| `/movies` | `get_popular_movies` | 인기 영화 목록 |
| `/movies/:id` | `get_movie_details` | 영화 상세 정보 |
| `/movies/:id/credits` | `get_movie_credits` | 출연진/제작진 |
| `/movies/:id/similar` | `get_similar_movies` | 유사한 영화 |

## 예시 상호작용

```
You: 지금 인기 있는 영화 알려줘
  [get_popular_movies() 호출 중...]
  [get_popular_movies() 완료]
Agent: 현재 인기 영화 목록입니다: 1. Avatar: Fire and Ash ...

You: 첫 번째 영화에 대해 더 알려줘
  [get_movie_details() 호출 중...]
  [get_movie_details() 완료]
Agent: Avatar: Fire and Ash는 ...

You: 비슷한 영화 추천해 줘
  [get_similar_movies() 호출 중...]
  [get_similar_movies() 완료]
Agent: 유사한 영화를 추천드립니다: ...
```
