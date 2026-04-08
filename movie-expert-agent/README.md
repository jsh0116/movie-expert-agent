# Movie Expert Agent

OpenAI Agents SDK + Clean Architecture로 구현한 영화 전문가 에이전트.

## API

`https://nomad-movies.nomadcoders.workers.dev`

| 도구 | 엔드포인트 | 설명 |
|------|-----------|------|
| `get_popular_movies()` | `/movies` | 인기 영화 목록 |
| `get_movie_details(id)` | `/movies/:id` | 영화 상세 정보 |
| `get_movie_credits(id)` | `/movies/:id/credits` | 출연진 및 제작진 |

## 아키텍처

```
src/
├── domain/          # 엔티티(Movie, Credits) + 포트(IMovieRepository)
├── application/     # Use Cases
├── infrastructure/  # API 호출 구현체
└── adapters/        # OpenAI Agent + @function_tool 정의
```

## 실행

```bash
uv sync

# .env 파일 설정 (OPENAI_API_KEY 필수)
echo "OPENAI_API_KEY=sk-..." > .env

# 커스텀 API 엔드포인트 사용 시 (선택, 미설정 시 OpenAI 기본 도메인 사용)
echo "AI_BASE_URL=https://your-custom-endpoint/v1" >> .env

# CLI 실행
uv run python src/main.py

# Jupyter Notebook
uv run jupyter notebook main.ipynb
```
