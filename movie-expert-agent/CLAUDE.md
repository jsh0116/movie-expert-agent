# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OpenAI Agents SDK + Clean Architecture로 구현한 영화 전문가 에이전트. 외부 영화 API(`https://nomad-movies.nomadcoders.workers.dev`)를 호출하여 인기 영화, 상세 정보, 출연진/제작진을 조회한다.

## Commands

```bash
uv sync                        # 의존성 설치
uv run python src/main.py      # CLI 실행
uv run jupyter notebook main.ipynb  # 노트북 실행
```

## Architecture

Clean Architecture 4계층 구조:

- **Domain** (`src/domain/`) — Pydantic 엔티티(`Movie`, `CastMember`, `CrewMember`, `MovieCredits`)와 포트(`IMovieRepository` ABC)
- **Application** (`src/application/use_cases/`) — 유스케이스 클래스. 포트를 주입받아 비즈니스 로직 실행
- **Infrastructure** (`src/infrastructure/`) — `MovieAPIRepository`(httpx AsyncClient로 외부 API 호출), `env_config.py`(환경변수)
- **Adapters** (`src/adapters/`) — OpenAI Agents SDK 통합. `@function_tool` 데코레이터로 도구 정의, `Agent` 객체 생성

`main.ipynb`은 동일한 아키텍처를 노트북 형태로 재현한 것.

## Key Configuration

- `.env`에 `OPENAI_API_KEY`와 `AI_BASE_URL` 설정 필요
- `AI_BASE_URL`을 통해 커스텀 OpenAI-호환 엔드포인트 사용 (OpenAIProvider의 base_url로 전달)
- `RunConfig`에 `tracing_disabled=True` 설정하여 tracing 인증 에러 방지
- 에이전트 모델: `gpt-4o-mini`, 응답 언어: 한국어
