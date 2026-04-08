---
name: google-adk-agent
description: Google ADK(Agent Development Kit) 기반 Python AI 에이전트 생성. 계층적 sub-agent, AgentTool, ToolContext 상태/아티팩트, 콜백, Vertex AI 배포 포함.
argument-hint: [agent-name] [description]
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Task
dependencies: []
triggers:
  - google adk
  - adk agent
  - agent development kit
  - agenttool
  - toolcontext
  - vertex ai agent
  - litellm agent
  - root_agent
  - sub agent hierarchy
  - parallel agent
  - sequential agent
---

# Google ADK 에이전트 생성

`$ARGUMENTS`를 기반으로 Google ADK 에이전트를 생성한다.
인자가 없으면 사용자에게 에이전트 이름과 목적을 먼저 물어본다.

## 필수 패키지 (pyproject.toml)

```toml
[project]
name = "<agent-name>"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    "google-adk>=1.12.0",
    "google-genai>=1.31.0",
    "litellm>=1.76.0",
    "python-dotenv>=1.1.1",
]
```

Vertex AI 배포 시 `google-cloud-aiplatform[adk,agent-engines]>=1.111.0` 추가.

## 프로젝트 구조

```text
<agent-name>/
├── <package-name>/           # 패키지 디렉토리 (adk web에서 사용)
│   ├── __init__.py           # 'from .agent import root_agent' 포함
│   ├── agent.py              # 메인 에이전트 + root_agent
│   ├── prompt.py             # 프롬프트 분리
│   └── sub_agents/           # 하위 에이전트들
│       ├── __init__.py
│       ├── analyst.py
│       └── researcher.py
├── .env
└── pyproject.toml
```

**핵심 컨벤션**: `root_agent` 변수를 반드시 정의해야 ADK 프레임워크가 인식함.

```python
# __init__.py
from .agent import root_agent
```

---

## 에이전트 정의

### 기본 에이전트 (도구 직접 사용)

```python
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.tool_context import ToolContext
from .prompt import AGENT_DESCRIPTION, AGENT_INSTRUCTION

MODEL = LiteLlm(model="openai/gpt-4o")

async def my_tool(tool_context: ToolContext, query: str):
    """도구 설명 - docstring이 도구 스키마가 됨."""
    return {"result": f"처리 결과: {query}"}

my_agent = Agent(
    name="MyAgent",
    description=AGENT_DESCRIPTION,
    instruction=AGENT_INSTRUCTION,
    tools=[my_tool],
    model=MODEL,
)

root_agent = my_agent
```

### 계층적 에이전트 (sub-agent 조합)

```python
from google.adk.tools.agent_tool import AgentTool
from .sub_agents.analyst import analyst_agent
from .sub_agents.researcher import researcher_agent

orchestrator = Agent(
    name="Orchestrator",
    instruction=PROMPT,
    model=MODEL,
    tools=[
        AgentTool(agent=analyst_agent),
        AgentTool(agent=researcher_agent),
        save_report,  # 일반 도구도 혼합 가능
    ],
)

root_agent = orchestrator
```

---

## 에이전트 타입

| 타입 | 임포트 | 용도 |
|------|--------|------|
| `Agent` | `google.adk.agents.Agent` | 표준 LLM 에이전트 (도구/sub-agent) |
| `LlmAgent` | `google.adk.agents.LlmAgent` | 경량 에이전트 (간단한 태스크) |
| `SequentialAgent` | `google.adk.agents.SequentialAgent` | 순차 실행 (파이프라인) |
| `ParallelAgent` | `google.adk.agents.ParallelAgent` | 병렬 실행 |

```python
from google.adk.agents import SequentialAgent, ParallelAgent

# 순차: prompt_builder → image_builder
image_pipeline = SequentialAgent(
    name="ImagePipeline",
    sub_agents=[prompt_builder_agent, image_builder_agent],
)

# 병렬: 이미지 + 음성 동시 생성
asset_generator = ParallelAgent(
    name="AssetGenerator",
    description="이미지와 음성을 병렬 생성",
    sub_agents=[image_pipeline, voice_generator_agent],
)
```

---

## 프롬프트 분리 (prompt.py)

```python
# prompt.py
AGENT_DESCRIPTION = "주식 투자 조언을 제공하는 금융 어드바이저"

AGENT_INSTRUCTION = """
You are a Professional Financial Advisor.
분석 결과를 종합하여 투자 조언을 제공하세요.

항상 다음 도구를 순서대로 사용하세요:
1. DataAnalyst - 기본 데이터 수집
2. FinancialAnalyst - 재무제표 분석
3. NewsAnalyst - 뉴스/이슈 분석
4. save_advice_report - 최종 보고서 저장
"""
```

---

## 도구 정의 (ToolContext)

### 기본 도구

```python
from google.adk.tools.tool_context import ToolContext

async def get_weather(tool_context: ToolContext, location: str):
    """특정 위치의 날씨 정보를 조회합니다."""
    return {
        "location": location,
        "temperature": "22°C",
        "condition": "Partly cloudy",
    }
```

- 첫 번째 파라미터는 반드시 `tool_context: ToolContext`
- Docstring이 도구 설명으로 사용됨
- 반환값은 dict 또는 문자열

### 상태 관리 (tool_context.state)

```python
async def save_report(tool_context: ToolContext, summary: str, ticker: str):
    """분석 보고서를 저장합니다."""
    state = tool_context.state
    
    # 다른 에이전트의 결과 읽기
    data_result = state.get("data_analyst_result")
    financial_result = state.get("financial_analyst_result")
    
    # 상태에 결과 저장
    state["report"] = f"Summary: {summary}\nData: {data_result}"
    
    return {"success": True}
```

### 아티팩트 저장/로드

```python
from google.genai import types

async def save_artifact_example(tool_context: ToolContext):
    # 마크다운 아티팩트
    md_artifact = types.Part(
        inline_data=types.Blob(
            mime_type="text/markdown",
            data=report.encode("utf-8"),
        )
    )
    await tool_context.save_artifact("report.md", md_artifact)

    # 이미지 아티팩트
    img_artifact = types.Part(
        inline_data=types.Blob(
            mime_type="image/jpeg",
            data=image_bytes,
        )
    )
    await tool_context.save_artifact("scene_1_image.jpeg", img_artifact)

    # 아티팩트 목록 조회
    existing = await tool_context.list_artifacts()

    # 아티팩트 로드
    loaded = await tool_context.load_artifact(filename="scene_1_image.jpeg")
    raw_bytes = loaded.inline_data.data
```

지원 MIME 타입: `text/markdown`, `image/jpeg`, `audio/mpeg`, `video/mp4`

---

## 구조화 출력 (output_schema)

```python
from pydantic import BaseModel

class ContentPlan(BaseModel):
    topic: str
    total_duration: int
    scenes: list[dict]

planner_agent = Agent(
    name="ContentPlanner",
    instruction="콘텐츠 계획을 JSON으로 출력하세요.",
    model=MODEL,
    output_schema=ContentPlan,
    output_key="content_planner_output",  # state에 저장될 키
)
```

`output_key`로 지정하면 하위 에이전트 도구에서 `tool_context.state.get("content_planner_output")`으로 접근 가능.

---

## 콜백 (Guardrail 용도)

```python
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse

def before_model_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
):
    """LLM 호출 전 요청을 검사/차단할 수 있다."""
    history = llm_request.contents
    last_message = history[-1]
    
    if last_message.role == "user":
        text = last_message.parts[0].text
        if "차단할키워드" in text:
            return LlmResponse(
                content=types.Content(
                    parts=[types.Part(text="죄송합니다. 해당 요청은 처리할 수 없습니다.")],
                    role="model",
                )
            )
    return None  # None 반환 시 정상 LLM 호출 진행

agent = Agent(
    before_model_callback=before_model_callback,
    ...
)
```

---

## 세션 관리 & Runner

```python
from google.adk.sessions import DatabaseSessionService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.genai import types

# 세션 서비스
session_service = DatabaseSessionService(db_url="sqlite:///./session.db")

# 아티팩트 서비스
artifact_service = InMemoryArtifactService()

# 세션 생성 (초기 상태 포함)
session = await session_service.create_session(
    app_name="my_agent",
    user_id="u_123",
    state={"user_name": "홍길동"},
)

# Runner 생성
runner = Runner(
    agent=root_agent,
    session_service=session_service,
    app_name="my_agent",
    artifact_service=artifact_service,
)

# 실행
message = types.Content(
    role="user",
    parts=[types.Part(text="AAPL 분석해줘")],
)

async for event in runner.run_async(
    user_id="u_123",
    session_id=session.id,
    new_message=message,
):
    if event.is_final_response():
        print(event.content.parts[0].text)
    else:
        print(event.get_function_calls())
```

---

## Vertex AI 배포

```python
import vertexai
from vertexai.preview import reasoning_engines

vertexai.init(
    project="my-project-id",
    location="us-central1",
    staging_bucket="gs://my-bucket",
)

app = reasoning_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)

remote_app = vertexai.agent_engines.create(
    display_name="My Agent",
    agent_engine=app,
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]",
        "litellm",
    ],
    extra_packages=["<package-name>"],
    env_vars={"OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY")},
)
```

배포 관리:
```python
# 조회
remote_app = vertexai.agent_engines.get(DEPLOYMENT_ID)

# 쿼리
for event in remote_app.stream_query(
    user_id="u_123", session_id=SESSION_ID, message="질문"
):
    print(event)

# 삭제
remote_app.delete(force=True)
```

---

## 실행

```bash
cd <agent-name>
uv sync

# ADK 웹 UI (개발용)
adk web <package-name>

# 프로그래밍 방식 (Runner 사용)
uv run python -c "import asyncio; from <package>.agent import root_agent; ..."
```

## 참고 문서

- [Google ADK 참고](references/adk-reference.md)
