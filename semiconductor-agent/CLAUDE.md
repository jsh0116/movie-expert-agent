# CLAUDE.md — semiconductor-agent

## Project Overview

LangGraph 기반 반도체 취준생 AI 학습 에이전트. 삼성DS/SK하이닉스 기술면접 특화.  
Clean Architecture (4-layer) + TDD (pytest) 로 구현됨.

## Commands

```bash
uv sync --dev                          # 의존성 + pytest 설치
uv run pytest tests/ -v                # 전체 테스트 실행 (85개)
uv run jupyter notebook main.ipynb     # 데모 노트북 실행
uv run chainlit run chainlit_app.py    # Chainlit 웹 UI
```

## Architecture (Clean Architecture)

```
semiconductor/
├── domain/              # 레이어 1: 순수 비즈니스 규칙 (외부 의존성 없음)
│   ├── entities.py      #   Question, EvaluationResult, DiagnosticResult
│   └── ports.py         #   IQuestionRepository, ILLMJudge, ILLMCritic, ICoachLLM, IDiagnosticLLM
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
│   │   └── llm_service.py      # OpenAILLMJudge, OpenAIEvaluationCritic, OpenAICoachLLM, OpenAIDiagnosticLLM
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
- 모델 차등화 (env var로 오버라이드 가능):
  - `LLM_MODEL_JUDGE` (기본 `gpt-4o`, temp=0.0) — 면접 답변 평가, 결정론적
  - `LLM_MODEL_CRITIC` (기본 `gpt-4o`, temp=0.0) — Self-Critique 평가 검증
  - `LLM_MODEL_DIAGNOSTIC` (기본 `gpt-4o`, temp=0.0) — 도메인별 진단, 결정론적
  - `LLM_MODEL_COACH` (기본 `gpt-4o-mini`, temp=0.5) — 소크라테스 코칭, 약간의 다양성
- LLM judge 루브릭: 정확성 40 + 깊이 30 + 전문용어 30 = 100점

## 평가 파이프라인 ("교수 초과" 메커니즘)

```
질문 + 답변
   ↓
[Specialty Judge]  ← 도메인별 전문가 페르소나 (소자/공정/회로/트렌드)
   ↓ initial_evaluation
[Critic]           ← Self-Critique: 평가의 평가, 과대/과소 식별
   ↓ final_evaluation
출력:
  - 점수 (40/30/30 = 100)
  - feedback
  - strong_points / weak_points
  - 🔬 specialist_commentary  (도메인 전문가 코멘트)
  - 📚 model_answer           (만점 모범답안, LaTeX 수식 포함 가능)
  - 💡 follow_up_question     (약점 파고드는 후속 질문)
```

도메인 페르소나:
- **소자**: 삼성종합기술원 출신 MOSFET/FinFET/GAA 박사 — 1차 원리 중시
- **공정**: SK하이닉스 청주 fab CVD/ALD 박사 — step coverage, conformality 중시
- **회로**: 메모리 컨트롤러 회로 설계자 — 센스앰프/차지펌프 마진 중시
- **트렌드**: TSMC/Samsung Foundry 산업 분석가 — EUV/HBM/GAA 로드맵 중시

## User Commands (in notebook)

| 입력 | 동작 |
|------|------|
| `/인터뷰` | 모의면접 시작 (회사별 질문 출제) |
| `/qa [주제]` | 소크라테스 코칭 시작 |
| `/진단` | 도메인별 이해도 진단 + 차트 |
| `quit` | 세션 종료 |
