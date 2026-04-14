# CLAUDE.md

## Project Overview

OpenAI Agents SDK + Clean Architecture로 구현한 라이프 코치 에이전트. 웹 검색(`WebSearchTool`)을 활용하여 동기부여, 습관 형성, 웰니스, 생산성, 마인드풀니스에 대한 최신 정보와 조언을 제공한다.

## Commands

```bash
uv sync                                # 의존성 설치
uv run streamlit run main.py           # Streamlit UI 실행
uv run jupyter notebook main.ipynb     # 노트북 실행
```

## Architecture

Clean Architecture 4계층 구조:

- **Domain** (`domain/`) — dataclass 엔티티(`CoachingSession`, `CoachingMessage`, `CoachingCategory`)
- **Application** (`application/`) — 유스케이스 클래스(`CoachChatUseCase`). 대화 세션 관리. `AppContext`로 DI 컨테이너 역할
- **Infrastructure** (`infrastructure/`) — `load_run_config()`로 환경 변수 기반 RunConfig 생성
- **Presentation** (`presentation/`) — OpenAI Agents SDK 통합. `WebSearchTool`(빌트인 웹 검색), `get_coaching_tip`(카테고리별 코칭 팁) 도구 정의, `Agent` 객체 생성

`main.py`가 Streamlit UI + Composition Root로 모든 의존성을 조립한다.

## Key Configuration

- `.env`에 `OPENAI_API_KEY`와 `AI_BASE_URL` 설정 필요
- `AI_BASE_URL`이 있으면 `OpenAIProvider(base_url=..., use_responses=False)`로 chat completions API 사용
- `RunConfig`에 `tracing_disabled=True` 설정하여 tracing 인증 에러 방지
- 에이전트 모델: `gpt-4o-mini`, 응답 언어: 한국어

## Tools

| 도구 | 타입 | 설명 |
|------|------|------|
| `WebSearchTool` | 빌트인 | 동기부여, 습관, 웰니스 관련 최신 웹 검색 |
| `get_coaching_tip(category)` | 커스텀 | 카테고리별 코칭 팁 (motivation, habits, wellness, productivity, mindfulness) |
