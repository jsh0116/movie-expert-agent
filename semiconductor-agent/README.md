# 반도체 면접 준비 AI 에이전트

삼성DS / SK하이닉스 기술면접을 준비하는 취준생을 위한 AI 학습 에이전트.  
LangGraph 기반 멀티 에이전트 구조로 모의면접, 개념 코칭, 이해도 진단을 제공합니다.

---

## 주요 기능

| 기능 | 명령어 | 설명 |
|------|--------|------|
| 모의 기술면접 | `/인터뷰` | 회사별 질문 출제 + LLM judge 40/30/30 루브릭 자동 채점 |
| 개념 학습 코치 | `/qa [주제]` | 소크라테스 방식 — 직접 답 대신 힌트로 사고 유도 |
| 이해도 진단 | `/진단` | 도메인별 점수 분석 + matplotlib 바 차트 시각화 |

### 회사별 특화 질문 풀

- **삼성DS**: FinFET/GAA 소자, EUV 리소그래피, CVD/ALD 공정, 센스앰프 회로 심화
- **SK하이닉스**: HBM 스택 구조, TSV 기술, 하이브리드 본딩, LPDDR5/CXL 트렌드

### LLM Judge 평가 루브릭

```
정확성 (accuracy)    0–40점  핵심 개념이 올바르게 기술되었는가
깊이 (depth)         0–30점  원리·메커니즘까지 설명했는가
전문용어 (term.)     0–30점  반도체 공학 용어를 정확하게 사용했는가
──────────────────────────
합계                 0–100점  80+ 우수 / 50+ 보통 / 50미만 미흡
```

---

## 빠른 시작

### 1. 의존성 설치

```bash
cd semiconductor-agent
uv sync --dev
```

### 2. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일에 OPENAI_API_KEY 입력
```

### 3. 데모 노트북 실행

```bash
uv run jupyter notebook main.ipynb
```

노트북 2번 셀에서 회사와 최대 문제 수를 설정할 수 있습니다:

```python
COMPANY = "samsung_ds"   # "samsung_ds" | "sk_hynix"
DOMAIN  = None           # None=전체 | "소자" | "공정" | "회로" | "트렌드"
MAX_Q   = 5
```

### 4. 세션 예시

```
>>> /인터뷰
📝 [공정] 문제 1/5

CVD와 ALD의 메커니즘 차이를 설명하고, ALD가 고종횡비 구조에 유리한 이유를 말씀해 주세요.

>>> CVD는 가스가 동시에 반응하고, ALD는 전구체를 순서대로 흘려 한 층씩 쌓습니다.

📊 평가 결과 [보통] 58/100점

  정확성 28/40 | 깊이 16/30 | 전문용어 14/30

💬 self-limiting 반응 메커니즘과 컨포말성 우위에 대한 설명이 더 필요합니다.
✅ 잘한 점: ALD의 순차적 증착 방식, 기본 개념 이해
📌 보완점:  자기제한 반응 원리, 고종횡비 균일성 메커니즘

>>> /qa TSV 구조
코치: TSV가 왜 필요한지 알고 있나요? 먼저 HBM의 구조를 어디까지 이해하고 있는지 말씀해 주세요.

>>> /진단
🔬 이해도 진단 결과

  🟡 소자: 55점
  🟡 공정: 62점
  🔴 회로: 38점
  🟢 트렌드: 74점

💪 강점 영역: 트렌드, 공정
📚 보완 필요: 회로
🎯 다음 학습 추천: DRAM 센스앰프 동작 원리와 교차결합 인버터 구조를 집중적으로 학습하세요.
```

---

## 아키텍처

Clean Architecture 4-layer 구조 + LangGraph StateGraph 패턴.

```
semiconductor/
├── domain/              # Layer 1 — 순수 비즈니스 규칙 (외부 의존성 없음)
│   ├── entities.py          Question, EvaluationResult, DiagnosticResult
│   └── ports.py             IQuestionRepository, ILLMJudge, ICoachLLM, IDiagnosticLLM
│
├── application/         # Layer 2 — 유스케이스 (포트에만 의존)
│   └── use_cases/
│       ├── evaluate_answer.py
│       ├── next_question.py
│       ├── coach_concept.py
│       └── diagnose_session.py
│
├── infrastructure/      # Layer 3 — 포트 구현체
│   ├── llm/llm_service.py       LangChain gpt-4o-mini 기반 구현
│   └── question_bank/           삼성DS / SK하이닉스 질문 풀 (in-memory)
│
└── adapters/            # Layer 4 — LangGraph 어댑터
    ├── state.py             InterviewState TypedDict
    ├── graph.py             StateGraph 조립 + create_app()
    └── nodes/
        ├── orchestrator.py      명령어 파싱 + 라우팅
        ├── mock_interviewer.py  질문 출제 / 평가
        ├── qa_coach.py          소크라테스 코칭
        └── diagnostic.py        진단 + 시각화
```

### 그래프 토폴로지

```
START → orchestrator ──► mock_interviewer ──► END
                     ├──► qa_coach        ──► END
                     ├──► diagnostic      ──► END
                     └──► END  (idle)
```

---

## 테스트

```bash
uv run pytest tests/ -v
```

```
31 passed in 0.03s
```

Domain, Application, Infrastructure 3개 레이어를 단위 테스트로 커버합니다. 외부 LLM 의존성은 mock으로 격리되어 API 키 없이도 실행됩니다.

---

## 기술 스택

| 분류 | 라이브러리 |
|------|-----------|
| 에이전트 오케스트레이션 | [LangGraph](https://github.com/langchain-ai/langgraph) |
| LLM | [LangChain OpenAI](https://github.com/langchain-ai/langchain) + gpt-4o-mini |
| 시각화 | matplotlib |
| 테스트 | pytest |
| 패키지 관리 | uv |

---

## 요구사항

- Python 3.13+
- OpenAI API 키 (또는 OpenAI 호환 엔드포인트)
- uv
