---
name: agent-evaluation
description: AI 에이전트 평가 및 테스트 시스템 구축. Evalset 설계, 자동화 테스트, 품질 메트릭 수집, Google ADK eval 통합, 프레임워크별 테스트 패턴 포함.
argument-hint: "framework agent-name"
---

# AI 에이전트 평가 시스템 구축

`$ARGUMENTS`를 기반으로 에이전트 평가 시스템을 구축한다.
인자가 없으면 사용자에게 대상 에이전트의 프레임워크와 평가 목적을 물어본다.

---

## 평가 전략 개요

AI 에이전트 평가는 3가지 측면을 다룬다:

1. **기능 평가**: 에이전트가 올바른 도구를 올바른 순서로 호출하는가?
2. **응답 품질**: 최종 응답이 기대에 부합하는가?
3. **안정성**: 동일 입력에 대해 일관된 결과를 내는가?

---

## Google ADK Evalset 패턴

Google ADK는 JSON 기반 evalset을 제공한다.

### Evalset 구조

```json
{
  "eval_set_id": "MyAgentEval",
  "name": "MyAgentEval",
  "eval_cases": [
    {
      "eval_id": "BasicGreeting",
      "conversation": [
        {
          "invocation_id": "e-001",
          "user_content": {
            "parts": [{"text": "안녕하세요!"}],
            "role": "user"
          },
          "final_response": {
            "parts": [{"text": "안녕하세요! 무엇을 도와드릴까요?"}]
          },
          "intermediate_data": {
            "tool_uses": [],
            "intermediate_responses": []
          }
        },
        {
          "invocation_id": "e-002",
          "user_content": {
            "parts": [{"text": "서울 날씨 알려줘"}],
            "role": "user"
          },
          "final_response": {
            "parts": [{"text": "서울의 현재 날씨는..."}]
          },
          "intermediate_data": {
            "tool_uses": [
              {
                "id": "call_001",
                "name": "get_weather",
                "args": {"location": "Seoul"}
              }
            ]
          }
        }
      ],
      "session_input": {
        "app_name": "my_agent",
        "user_id": "test_user",
        "state": {}
      }
    }
  ]
}
```

### Evalset 파일 위치

```text
<agent-package>/
├── agent.py
├── <AgentName>Eval.evalset.json       # 평가 케이스 정의
└── .adk/
    └── eval_history/                   # 평가 결과 히스토리
        └── <agent>_<eval>_<timestamp>.evalset_result.json
```

### ADK Eval 실행

```bash
# ADK 웹 UI에서 실행
adk web <package-name>
# UI에서 Eval 탭 → Run Eval 클릭

# 프로그래밍 방식
uv run python -c "
from google.adk.evaluation import evaluate_agent
# evaluate_agent(...) 호출
"
```

### Evalset 설계 원칙

| 원칙 | 설명 |
|------|------|
| 멀티턴 대화 | 단일 질문이 아닌 여러 턴의 대화 흐름 테스트 |
| 도구 호출 검증 | `tool_uses`로 올바른 도구가 올바른 인자로 호출됐는지 확인 |
| 엣지 케이스 | 모호한 질문, 범위 밖 요청, 오류 상황 포함 |
| 초기 상태 설정 | `session_input.state`로 테스트별 초기 컨텍스트 설정 |

---

## OpenAI Agents SDK 테스트 패턴

### 단위 테스트 (도구 검증)

```python
import pytest
from tools import lookup_order, run_diagnostic_check
from models import UserAccountContext

@pytest.fixture
def test_context():
    return UserAccountContext(
        customer_id=1, name="테스트유저", tier="premium"
    )

def test_lookup_order(test_context):
    result = lookup_order(test_context, order_id="ORD-123")
    assert "ORD-123" in result
    assert isinstance(result, str)

def test_diagnostic_check(test_context):
    result = run_diagnostic_check(
        test_context, product_name="Widget", issue_description="작동 안됨"
    )
    assert "Widget" in result
```

### 통합 테스트 (에이전트 실행)

```python
import pytest
from agents import Runner
from my_agents.triage_agent import triage_agent
from models import UserAccountContext

@pytest.mark.asyncio
async def test_triage_routes_to_billing():
    ctx = UserAccountContext(customer_id=1, name="테스트", tier="basic")
    result = await Runner.run(
        triage_agent,
        "요금이 잘못 청구됐어요",
        context=ctx,
    )
    # 핸드오프 확인
    assert result.last_agent.name == "Billing Support Agent"

@pytest.mark.asyncio
async def test_guardrail_blocks_off_topic():
    from agents import InputGuardrailTripwireTriggered
    ctx = UserAccountContext(customer_id=1, name="테스트", tier="basic")
    with pytest.raises(InputGuardrailTripwireTriggered):
        await Runner.run(triage_agent, "피자 추천해줘", context=ctx)
```

---

## CrewAI 테스트 패턴

### Crew 출력 검증

```python
from main import MyAgentCrew

def test_crew_produces_output():
    result = MyAgentCrew().crew().kickoff(
        inputs={"topic": "AI Trends"}
    )
    assert result is not None
    assert len(result.tasks_output) > 0

def test_structured_output():
    result = MyAgentCrew().crew().kickoff(
        inputs={"topic": "AI Trends"}
    )
    # Pydantic 모델 검증
    article = result.tasks_output[0].pydantic
    assert article is not None
    assert len(article.title) > 0

def test_output_files_created():
    import os
    MyAgentCrew().crew().kickoff(inputs={"topic": "Test"})
    assert os.path.exists("output/research.md")
    assert os.path.exists("output/article.md")
```

### Flow 상태 검증

```python
from main import MyPipelineFlow

def test_flow_state_transitions():
    flow = MyPipelineFlow()
    flow.kickoff(inputs={"content_type": "blog", "topic": "AI"})
    assert flow.state.score >= 7  # 품질 기준 충족 확인
    assert flow.state.blog_post is not None
```

---

## LangGraph 테스트 패턴

```python
import pytest
from adapters.graph.agent import graph

@pytest.mark.asyncio
async def test_agent_responds():
    config = {"configurable": {"thread_id": "test-1"}}
    result = await graph.ainvoke(
        {"messages": [("user", "안녕하세요")]},
        config=config,
    )
    assert len(result["messages"]) > 1
    assert result["messages"][-1].content

@pytest.mark.asyncio
async def test_tool_invocation():
    config = {"configurable": {"thread_id": "test-2"}}
    result = await graph.ainvoke(
        {"messages": [("user", "서울 날씨 알려줘")]},
        config=config,
    )
    # 도구 호출 메시지 확인
    tool_messages = [m for m in result["messages"] if m.type == "tool"]
    assert len(tool_messages) > 0
```

---

## 공통 평가 메트릭

### 정량 메트릭

| 메트릭 | 측정 방법 |
|--------|----------|
| **도구 호출 정확도** | 기대 도구 vs 실제 호출 도구 비교 |
| **응답 시간** | 첫 응답까지 걸린 시간 (TTFT) |
| **도구 호출 횟수** | 불필요한 중복 호출 감지 |
| **핸드오프 정확도** | 올바른 에이전트로 라우팅됐는지 |
| **가드레일 정확도** | False positive / False negative 비율 |

### 정성 메트릭

| 메트릭 | 평가 방법 |
|--------|----------|
| **응답 관련성** | LLM-as-Judge로 응답 품질 평가 |
| **일관성** | 동일 입력 5회 실행 후 구조적 유사도 비교 |
| **톤/스타일** | 브랜드 가이드라인 준수 여부 |

### LLM-as-Judge 패턴

```python
from anthropic import Anthropic

client = Anthropic()

def evaluate_response(question: str, response: str, criteria: str) -> dict:
    result = client.messages.create(
        model="claude-sonnet-4-6",
        messages=[{
            "role": "user",
            "content": f"""다음 AI 에이전트 응답을 평가하세요.

질문: {question}
응답: {response}

평가 기준: {criteria}

JSON으로 응답하세요:
{{"score": 1-10, "reason": "..."}}"""
        }],
    )
    return json.loads(result.content[0].text)
```

---

## 평가 자동화 (pytest 기반)

### pyproject.toml에 pytest 추가

```toml
[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
]
```

### 테스트 실행

```bash
uv sync
uv run pytest tests/ -v
uv run pytest tests/test_tools.py -v            # 도구 단위 테스트
uv run pytest tests/test_integration.py -v       # 통합 테스트
uv run pytest tests/test_evaluation.py -v        # 평가 테스트
```

### 테스트 디렉토리 구조

```text
tests/
├── test_tools.py              # 도구 함수 단위 테스트
├── test_agents.py             # 에이전트 라우팅/핸드오프 테스트
├── test_guardrails.py         # 가드레일 테스트
├── test_integration.py        # 전체 파이프라인 통합 테스트
└── test_evaluation.py         # LLM-as-Judge 품질 평가
```

---

## 참고 문서

- [평가 패턴 상세](references/eval-patterns.md)
