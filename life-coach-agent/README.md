# Life Coach Agent

OpenAI Agents SDK + Clean Architecture 기반 라이프 코치 에이전트

## 기능

- **웹 검색** (`WebSearchTool`) — 동기부여, 습관 형성, 웰니스 관련 최신 정보 검색
- **코칭 팁** (`get_coaching_tip`) — 5개 카테고리별 전문 코칭 팁 제공
- **Streamlit UI** — `st.chat_input` / `st.chat_message` 기반 채팅 인터페이스
- **Jupyter Notebook** — `input()`으로 직접 질의, 대화 히스토리 유지

## Architecture

Clean Architecture 4계층 구조:

```
domain/          → 엔티티 (CoachingSession, CoachingMessage, CoachingCategory)
application/     → Use Cases (CoachChatUseCase), Context (AppContext)
infrastructure/  → 환경 설정 (RunConfig, .env 로딩)
presentation/    → Agent 정의, Tools (WebSearchTool, get_coaching_tip)
```

## 실행 방법

```bash
# 의존성 설치
uv sync

# Streamlit UI
uv run streamlit run main.py

# Jupyter Notebook
uv run jupyter notebook main.ipynb
```

## 환경 설정

`.env` 파일에 OpenAI API 키를 설정합니다:

```env
OPENAI_API_KEY='your-openai-api-key'
AI_BASE_URL=
```

> `WebSearchTool`은 OpenAI Responses API 전용이므로 `AI_BASE_URL`을 비워야 합니다.

## 코칭 카테고리

| 카테고리 | 설명 |
|----------|------|
| `motivation` | 동기부여 및 목표 설정 |
| `habits` | 습관 형성 및 관리 |
| `wellness` | 건강, 수면, 운동, 식단 |
| `productivity` | 시간 관리 및 생산성 |
| `mindfulness` | 스트레스 관리 및 마인드풀니스 |
