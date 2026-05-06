# CLAUDE.md — semiconductor-agent

## Project Overview

LangGraph 기반 반도체 취준생 AI 학습 에이전트. 삼성DS/SK하이닉스 기술면접 특화.  
Clean Architecture (4-layer) + TDD (pytest) 로 구현됨.

## Commands

```bash
uv sync --dev                          # 의존성 + pytest 설치
uv run pytest tests/ -v                # 전체 테스트 실행 (31개)
uv run jupyter notebook main.ipynb    # 데모 노트북 실행
```

## Architecture (Clean Architecture)

```
semiconductor/
├── domain/              # 레이어 1: 순수 비즈니스 규칙 (외부 의존성 없음)
│   ├── entities.py      #   Question, EvaluationResult, DiagnosticResult
│   └── ports.py         #   IQuestionRepository, ILLMJudge, ICoachLLM, IDiagnosticLLM
│
├── application/         # 레이어 2: 유스케이스 (포트에만 의존)
│   └── use_cases/
│       ├── evaluate_answer.py   # EvaluateAnswerUseCase
│       ├── next_question.py     # GetNextQuestionUseCase
│       ├── coach_concept.py     # CoachConceptUseCase
│       └── diagnose_session.py  # DiagnoseSessionUseCase
│
├── infrastructure/      # 레이어 3: 포트 구현체 (LangChain / in-memory)
│   ├── llm/
│   │   └── llm_service.py      # OpenAILLMJudge, OpenAICoachLLM, OpenAIDiagnosticLLM
│   └── question_bank/
│       ├── _samsung_ds.py      # 삼성DS 질문 풀 (4도메인 × 5문제)
│       └── _sk_hynix.py        # SK하이닉스 질문 풀 (4도메인 × 4~5문제)
│
└── adapters/            # 레이어 4: LangGraph 어댑터 (thin wrappers)
    ├── state.py                # InterviewState TypedDict + create_initial_state()
    ├── graph.py                # create_app() → (app, state)
    └── nodes/
        ├── orchestrator.py     # 명령어 파싱 + 라우팅
        ├── mock_interviewer.py # 질문 출력 + LLM judge 평가
        ├── qa_coach.py         # 소크라테스 코칭 응답
        └── diagnostic.py      # 도메인 점수 분석 + matplotlib 차트
```

## Graph Topology

```
START → orchestrator → [conditional]
    → mock_interviewer → END
    → qa_coach         → END
    → diagnostic       → END
    → END (idle)
```

## Key Configuration

- `.env`에 `OPENAI_API_KEY` 필수
- `AI_BASE_URL` 설정 시 커스텀 엔드포인트 사용
- 모델: `gpt-4o-mini` (모든 LLM 노드)
- LLM judge 루브릭: 정확성 40 + 깊이 30 + 전문용어 30 = 100점

## User Commands (in notebook)

| 입력 | 동작 |
|------|------|
| `/인터뷰` | 모의면접 시작 (회사별 질문 출제) |
| `/qa [주제]` | 소크라테스 코칭 시작 |
| `/진단` | 도메인별 이해도 진단 + 차트 |
| `quit` | 세션 종료 |
