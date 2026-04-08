---
name: openai-agents
description: OpenAI Agents SDK 기반 Python AI 에이전트 생성. Agent/Runner, 가드레일, 핸드오프, MCP 서버, Voice 파이프라인, Streamlit UI 통합 포함.
argument-hint: "agent-name description"
---

# OpenAI Agents SDK 에이전트 생성

`$ARGUMENTS`를 기반으로 OpenAI Agents SDK 에이전트를 생성한다.
인자가 없으면 사용자에게 에이전트 이름과 목적을 먼저 물어본다.

## 필수 패키지 (pyproject.toml)

패키지 관리는 `uv`를 사용한다.

```toml
[project]
name = "<agent-name>"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    "openai-agents>=0.2.6",
    "python-dotenv>=1.1.1",
]
```

UI가 필요하면 `streamlit>=1.48.0` 추가. 음성이 필요하면 `openai-agents[voice]>=0.2.8`, `numpy`, `sounddevice` 추가.

## 프로젝트 구조

```text
<agent-name>/
├── main.py                # 진입점 (Streamlit 또는 CLI)
├── my_agents/
│   ├── triage_agent.py    # 메인 에이전트 (핸드오프 허브)
│   ├── specialist_a.py    # 전문 에이전트 A
│   └── specialist_b.py    # 전문 에이전트 B
├── tools.py               # @function_tool 정의
├── models.py              # Pydantic 모델 (가드레일 출력, 핸드오프 데이터)
├── output_guardrails.py   # 출력 가드레일 (선택)
├── workflow.py            # VoiceWorkflow (음성 사용 시)
├── .env
└── pyproject.toml
```

단일 에이전트 프로젝트는 `my_agents/` 없이 `main.py`에 에이전트를 직접 정의해도 된다.

## 에이전트 정의

### 기본 에이전트

```python
from agents import Agent, Runner
from dotenv import load_dotenv
load_dotenv()

agent = Agent(
    name="My Agent",
    instructions="You are a helpful assistant.",
    tools=[my_tool],
)
```

### 동적 인스트럭션 (컨텍스트 기반)

```python
from agents import Agent, RunContextWrapper

def dynamic_instructions(
    wrapper: RunContextWrapper[MyContext],
    agent: Agent[MyContext],
):
    return f"고객 {wrapper.context.name}을 돕고 있습니다. 등급: {wrapper.context.tier}"

agent = Agent(
    name="Support Agent",
    instructions=dynamic_instructions,
    tools=[...],
)
```

### Agent 생성자 주요 파라미터

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `name` | `str` | 에이전트 식별자 |
| `instructions` | `str \| Callable` | 시스템 프롬프트 (문자열 또는 동적 함수) |
| `tools` | `list` | `@function_tool` 또는 빌트인 도구 |
| `hooks` | `AgentHooks` | 라이프사이클 콜백 |
| `input_guardrails` | `list[InputGuardrail]` | 입력 검증 |
| `output_guardrails` | `list[OutputGuardrail]` | 출력 검증 |
| `handoffs` | `list[Handoff]` | 에이전트 핸드오프 |
| `mcp_servers` | `list[MCPServerStdio]` | MCP 서버 |
| `output_type` | `BaseModel` | 구조화된 JSON 출력 스키마 |

---

## 도구 정의 (@function_tool)

```python
from agents import function_tool

@function_tool
def lookup_order(
    context: MyContext,         # 자동 주입 (첫 번째 파라미터)
    order_id: str,
) -> str:
    """주문 정보를 조회합니다.
    
    Args:
        order_id: 조회할 주문 ID
    """
    return f"주문 {order_id}: 배송중"
```

- 첫 번째 파라미터가 컨텍스트 타입이면 자동 주입됨
- Docstring이 OpenAI 도구 스키마로 변환됨
- 반환 타입 어노테이션 필수

### 빌트인 도구

```python
from agents import WebSearchTool, FileSearchTool, ImageGenerationTool, CodeInterpreterTool

agent = Agent(
    tools=[
        WebSearchTool(),
        FileSearchTool(vector_store_ids=["vs_xxx"], max_num_results=3),
        ImageGenerationTool(),
        CodeInterpreterTool(),
    ],
)
```

---

## 실행 패턴

### 동기 실행

```python
result = await Runner.run(agent, "안녕하세요", context=my_context)
print(result.final_output)
```

### 스트리밍 실행

```python
stream = Runner.run_streamed(
    agent,
    message,
    session=session,
    context=my_context,
)

async for event in stream.stream_events():
    if event.type == "raw_response_event":
        if event.data.type == "response.output_text.delta":
            print(event.data.delta, end="")
```

주요 이벤트 타입:
- `response.output_text.delta` — 텍스트 스트리밍
- `response.web_search_call.completed` — 웹 검색 완료
- `response.code_interpreter_call_code.delta` — 코드 실행
- `response.image_generation_call.partial_image` — 이미지 생성
- `response.mcp_call.completed` — MCP 도구 호출 완료

---

## 메모리 (SQLiteSession)

```python
from agents.extensions import SQLiteSession

session = SQLiteSession("chat-history", "memory.db")

# 아이템 추가
await session.add_items([{"role": "user", "content": "안녕"}])

# 대화 이력 조회
messages = await session.get_items()

# 세션 초기화
await session.clear_session()

# Runner에 전달
stream = Runner.run_streamed(agent, message, session=session)
```

---

## 컨텍스트 타입

```python
from pydantic import BaseModel

class UserContext(BaseModel):
    customer_id: int
    name: str
    tier: str = "basic"
    email: str | None = None

# Runner 실행 시 전달
result = await Runner.run(agent, input, context=UserContext(
    customer_id=123, name="홍길동", tier="premium"
))
```

---

## 가드레일

### 입력 가드레일 (off-topic 차단)

```python
from agents import Agent, Runner, input_guardrail, GuardrailFunctionOutput, RunContextWrapper, InputGuardrailTripwireTriggered

class GuardrailOutput(BaseModel):
    is_off_topic: bool
    reason: str

guardrail_agent = Agent(
    name="Input Guardrail",
    instructions="사용자 요청이 고객 지원과 관련 없으면 is_off_topic=True",
    output_type=GuardrailOutput,
)

@input_guardrail
async def off_topic_guardrail(wrapper, agent, input: str):
    result = await Runner.run(guardrail_agent, input, context=wrapper.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_off_topic,
    )

# 에이전트에 적용
agent = Agent(input_guardrails=[off_topic_guardrail], ...)

# 예외 처리
try:
    result = await Runner.run(agent, input)
except InputGuardrailTripwireTriggered:
    print("관련 없는 요청입니다.")
```

### 출력 가드레일 (응답 필터링)

```python
from agents import output_guardrail, OutputGuardrailTripwireTriggered

@output_guardrail
async def content_filter(wrapper, agent, output: str):
    result = await Runner.run(filter_agent, output, context=wrapper.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.contains_violation,
    )

agent = Agent(output_guardrails=[content_filter], ...)
```

---

## 에이전트 핸드오프 (Triage → Specialist)

```python
from agents import handoff
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from agents.extensions import handoff_filters

class HandoffData(BaseModel):
    to_agent_name: str
    issue_type: str
    reason: str

def on_handoff(wrapper: RunContextWrapper[MyContext], input_data: HandoffData):
    print(f"핸드오프: {input_data.to_agent_name} (사유: {input_data.reason})")

def make_handoff(agent):
    return handoff(
        agent=agent,
        on_handoff=on_handoff,
        input_type=HandoffData,
        input_filter=handoff_filters.remove_all_tools,
    )

triage_agent = Agent(
    name="Triage Agent",
    instructions=RECOMMENDED_PROMPT_PREFIX + "적절한 전문 에이전트로 라우팅하세요.",
    handoffs=[
        make_handoff(billing_agent),
        make_handoff(technical_agent),
    ],
)
```

핸드오프 후 `result.last_agent`로 마지막 활성 에이전트를 추적할 수 있다:
```python
stream = Runner.run_streamed(st.session_state["agent"], message, ...)
# 스트림 완료 후
st.session_state["agent"] = stream.last_agent
```

---

## 라이프사이클 훅 (AgentHooks)

```python
from agents import AgentHooks, RunContextWrapper, Agent, Tool

class LoggingHooks(AgentHooks):
    async def on_start(self, context, agent):
        print(f"{agent.name} 시작")

    async def on_end(self, context, agent, output):
        print(f"{agent.name} 완료")

    async def on_tool_start(self, context, agent, tool: Tool):
        print(f"도구 실행: {tool.name}")

    async def on_tool_end(self, context, agent, tool: Tool, result: str):
        print(f"도구 결과: {result}")

    async def on_handoff(self, context, agent, source):
        print(f"핸드오프: {source.name} → {agent.name}")

agent = Agent(hooks=LoggingHooks(), ...)
```

---

## MCP 서버 통합

```python
from agents.mcp.server import MCPServerStdio
from agents import HostedMCPTool

# 로컬 MCP 서버 (프로세스 실행)
yfinance_server = MCPServerStdio(
    params={"command": "uvx", "args": ["mcp-yahoo-finance"]},
    cache_tools_list=True,
)

# 원격 MCP 서버 (HTTP)
hosted_tool = HostedMCPTool(tool_config={
    "server_url": "https://mcp.example.com/mcp",
    "type": "mcp",
    "server_label": "MyMCP",
    "require_approval": "never",
})

# 사용 (async with 필수)
async with yfinance_server:
    agent = Agent(
        mcp_servers=[yfinance_server],
        tools=[hosted_tool],
    )
    result = await Runner.run(agent, "AAPL 주가 알려줘")
```

---

## Voice 파이프라인 (음성 에이전트)

```python
from agents.voice import AudioInput, VoicePipeline, VoiceWorkflowBase

class MyWorkflow(VoiceWorkflowBase):
    def __init__(self, context):
        self.context = context

    async def run(self, transcription):
        result = Runner.run_streamed(agent, transcription, context=self.context)
        async for chunk in VoiceWorkflowHelper.stream_text_from(result):
            yield chunk

# 실행
audio = AudioInput(buffer=audio_numpy_array)
pipeline = VoicePipeline(workflow=MyWorkflow(context=my_ctx))
result = await pipeline.run(audio)

async for event in result.stream():
    if event.type == "voice_stream_event_audio":
        player.write(event.data)
```

---

## Streamlit 통합 패턴

```python
import streamlit as st
import asyncio

if "session" not in st.session_state:
    st.session_state["session"] = SQLiteSession("chat", "memory.db")
    st.session_state["agent"] = triage_agent

if prompt := st.chat_input("메시지를 입력하세요"):
    with st.chat_message("user"):
        st.write(prompt)
    with st.chat_message("ai"):
        status = st.status("처리 중...")
        response = asyncio.run(run_agent(prompt))
        st.write(response)
```

---

## 실행

```bash
cd <agent-name>
uv sync
uv run python main.py                # CLI
uv run streamlit run main.py         # Streamlit UI
```
