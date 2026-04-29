# storybook-agent

Google ADK + Clean Architecture로 구현한 어린이 동화책 생성 에이전트.

## Commands

```bash
uv sync
adk web storybook                        # ADK Web UI로 테스트
uv run jupyter notebook main.ipynb      # Jupyter 노트북으로 실행
```

## Architecture

```
SequentialAgent (root_agent)
├── StoryWriter (LlmAgent)          — 테마 → 5페이지 StoryBook 구조화 출력 → state["story_data"]
└── Illustrator (LoopAgent, x5)
    └── PageIllustrator (Agent)     — state에서 현재 페이지 읽기 → Imagen 이미지 생성 → Artifact 저장
```

Clean Architecture 계층:
- **Domain** (`storybook/domain/`) — `StoryPage`, `StoryBook` Pydantic 엔티티
- **Infrastructure** (`storybook/infrastructure/`) — `imagen_client.py` (google.genai Imagen API)
- **Adapters** (`storybook/sub_agents/`) — ADK 에이전트 정의

## Key Configuration

- `.env`에 `GOOGLE_API_KEY` 설정 필요 (Google AI Studio)
- Imagen 3 (`imagen-3.0-generate-002`) 사용 — AI Studio API 키로 접근 가능
- `state["current_page_index"]`로 LoopAgent 페이지 진행 상태 추적
