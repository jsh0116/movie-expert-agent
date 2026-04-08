---
name: langgraph-agent
description: LangGraph 기반 Python/TypeScript AI 에이전트를 Clean Architecture 구조로 생성할 때 사용. 새 에이전트 프로젝트 셋업, StateGraph 설계, 툴/메모리/스트리밍 구현을 포함.
argument-hint: [language] [agent-name] [description]
---

# LangGraph Agent 생성 (Clean Architecture)

`$ARGUMENTS`를 기반으로 LangGraph 기반 AI 에이전트를 생성한다.
인자가 없으면 사용자에게 에이전트 개발 언어(Python 또는 TypeScript), 에이전트 이름과 목적을 먼저 물어본다.

Clean Architecture 원칙(`clean-architecture` 스킬 참조)을 LangGraph에 맞게 적용한다.

## 공통 원칙
**계층 의존 규칙**: `domain` ← `application` ← `adapters` ← `infrastructure`
LangGraph SDK 및 LangChain 의존성은 `adapters/`, `infrastructure/` 계층에만 존재해야 한다. `domain/`이나 `application/`은 이 프레임워크들을 몰라야 한다.

---

## Python 구현 가이드

### 프로젝트 구조
```text
<agent-name>/
├── src/
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── entities/         # Pydantic 엔티티 (프레임워크 의존성 없음)
│   │   └── ports/            # ABC 인터페이스 (tool_port.py, memory_port.py 등)
│   ├── application/
│   │   ├── __init__.py
│   │   └── use_cases/        # 에이전트 비즈니스 단위 (run_agent_use_case.py)
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── graph/            # LangGraph StateGraph (state.py, nodes.py, agent.py)
│   │   └── tools/            # tool port 구현체
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── config/           # env_config.py (pydantic-settings)
│   │   └── llm/              # 모델 및 LLM 초기화 (model.py)
│   └── main.py               # 진입점
├── .env
└── pyproject.toml
```

### 필수 패키지 (pyproject.toml)
패키지 관리는 `uv`를 사용한다.
```toml
[project]
name = "<agent-name>"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    "langgraph>=0.2",
    "langchain-anthropic>=0.3",
    "langchain-core>=0.3",
    "pydantic>=2.0",
    "pydantic-settings>=2.0",
    "python-dotenv>=1.0",
]
```

### 환경변수 (infrastructure/config/env_config.py)
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class EnvConfig(BaseSettings):
    anthropic_api_key: str
    langchain_api_key: str | None = None
    model: str = "claude-sonnet-4-6"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

config = EnvConfig()  # 임포트 시 검증
```

### 툴 포트와 구현 (domain vs adapters)
```python
# domain/ports/tool_port.py
from abc import ABC, abstractmethod

class ITool(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...
    @abstractmethod
    async def execute(self, **kwargs) -> str: ...

# adapters/tools/my_tool_tool.py
from langchain_core.tools import tool
from ...domain.ports.tool_port import ITool

class MyToolImpl(ITool):
    @property
    def name(self) -> str: return "my_tool"
    async def execute(self, input: str) -> str: return f"result: {input}"

@tool
async def my_langgraph_tool(input: str) -> str:
    """툴 설명"""
    return await MyToolImpl().execute(input=input)
```

### Graph 구성 (adapters/graph/agent.py)
```python
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from .state import AgentState
from .nodes import call_model, should_continue
from ..tools.my_tool_tool import my_langgraph_tool

workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode([my_langgraph_tool]))
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")

graph = workflow.compile(checkpointer=MemorySaver())
```

### 실행
```bash
uv sync
uv run python main.py
```

---

## TypeScript 구현 가이드

### 프로젝트 구조
```text
<agent-name>/
├── src/
│   ├── domain/
│   │   ├── entities/         # 비즈니스 엔티티
│   │   └── ports/            # 인터페이스 (tool.port.ts, memory.port.ts)
│   ├── application/
│   │   └── use-cases/        # Use cases (run-agent.use-case.ts)
│   ├── adapters/
│   │   ├── graph/            # LangGraph (state.ts, nodes.ts, agent.ts)
│   │   └── tools/            # tool 구현체
│   ├── infrastructure/
│   │   ├── config/           # env.config.ts
│   │   └── llm/              # model.ts
│   └── index.ts              # 진입점
├── .env
├── package.json
└── tsconfig.json
```

### 필수 패키지 (package.json)
```json
{
  "dependencies": {
    "@langchain/langgraph": "latest",
    "@langchain/anthropic": "latest",
    "@langchain/core": "latest",
    "zod": "latest",
    "dotenv": "latest"
  },
  "devDependencies": {
    "typescript": "latest",
    "@types/node": "latest",
    "ts-node": "latest"
  }
}
```

### 환경변수 (infrastructure/config/env.config.ts)
```typescript
import "dotenv/config";

export const config = {
  anthropicApiKey: process.env.ANTHROPIC_API_KEY!,
  langsmithApiKey: process.env.LANGCHAIN_API_KEY,
  model: process.env.MODEL ?? "claude-sonnet-4-6",
} as const;

if (!process.env.ANTHROPIC_API_KEY) throw new Error("Missing ANTHROPIC_API_KEY");
```

### 툴 포트와 구현 (domain vs adapters)
```typescript
// domain/ports/tool.port.ts
export interface ITool<TInput = unknown, TOutput = unknown> {
  name: string;
  description: string;
  execute(input: TInput): Promise<TOutput>;
}

// adapters/tools/my-tool.tool.ts
import { tool } from "@langchain/core/tools";
import { z } from "zod";

class MyToolImpl implements ITool<{ input: string }, string> {
  name = "my_tool";
  description = "툴 설명";
  async execute({ input }: { input: string }): Promise<string> {
    return `result: ${input}`;
  }
}

export const myLangchainTool = tool(
  async (input) => new MyToolImpl().execute(input),
  {
    name: "my_tool",
    description: "툴 설명",
    schema: z.object({ input: z.string() }),
  }
);
```

### Graph 구성 (adapters/graph/agent.ts)
```typescript
import { StateGraph, START, MemorySaver } from "@langchain/langgraph";
import { ToolNode } from "@langchain/langgraph/prebuilt";
import { AgentState } from "./state.js";
import { callModel, shouldContinue } from "./nodes.js";
import { myLangchainTool } from "../tools/my-tool.tool.js";

export const graph = new StateGraph(AgentState)
  .addNode("agent", callModel)
  .addNode("tools", new ToolNode([myLangchainTool]))
  .addEdge(START, "agent")
  .addConditionalEdges("agent", shouldContinue)
  .addEdge("tools", "agent")
  .compile({ checkpointer: new MemorySaver() });
```

### 실행
```bash
npm install
npx ts-node --esm src/index.ts
```

## 참고 문서
자세한 프레임워크 문서와 학습 자료는 `references/` 디렉토리를 참고한다.
- [LangChain v0.3](references/langchain.md)
- [LangGraph (Python)](references/langgraph-python.md)
- [LangGraph (TypeScript)](references/langgraph-ts.md)
- [학습 가이드](references/study-guide.md)
