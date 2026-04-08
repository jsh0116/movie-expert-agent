---
name: mcp-server
description: MCP(Model Context Protocol) 도구 서버 생성 및 에이전트 통합. 커스텀 MCP 서버 구현, MCPServerStdio/HostedMCPTool 연동, 도구 노출 패턴 포함.
argument-hint: "server-name description"
---

# MCP 도구 서버 생성

`$ARGUMENTS`를 기반으로 MCP 도구 서버를 생성한다.
인자가 없으면 사용자에게 서버 이름, 제공할 도구, 사용할 언어(Python/TypeScript)를 물어본다.

## MCP 개요

MCP(Model Context Protocol)는 AI 에이전트에 도구, 리소스, 프롬프트를 제공하는 표준 프로토콜이다.
MCP 서버를 만들면 OpenAI Agents SDK, Claude, LangChain 등 다양한 클라이언트에서 동일한 도구를 사용할 수 있다.

---

## Python MCP 서버

### 필수 패키지

```toml
[project]
name = "<server-name>"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    "mcp>=1.0.0",
]

[project.scripts]
<server-name> = "<package>.server:main"
```

### 프로젝트 구조

```text
<server-name>/
├── src/
│   └── <package>/
│       ├── __init__.py
│       └── server.py      # MCP 서버 구현
├── pyproject.toml
└── .env
```

### 서버 구현

```python
# server.py
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("<server-name>")

@server.list_tools()
async def list_tools():
    """사용 가능한 도구 목록을 반환한다."""
    return [
        Tool(
            name="search_docs",
            description="문서를 검색합니다",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "검색할 키워드",
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_status",
            description="시스템 상태를 확인합니다",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """도구를 실행한다."""
    if name == "search_docs":
        query = arguments["query"]
        # 실제 검색 로직
        results = f"'{query}'에 대한 검색 결과: ..."
        return [TextContent(type="text", text=results)]
    
    elif name == "get_status":
        return [TextContent(type="text", text="시스템 정상 운영 중")]
    
    raise ValueError(f"Unknown tool: {name}")

def main():
    asyncio.run(run_server())

async def run_server():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)

if __name__ == "__main__":
    main()
```

### 실행 및 테스트

```bash
uv sync
uv run <server-name>                    # 직접 실행
uvx <server-name>                        # uvx로 실행 (에이전트에서 사용)
```

---

## TypeScript MCP 서버

### 필수 패키지

```json
{
  "name": "<server-name>",
  "version": "0.1.0",
  "type": "module",
  "bin": { "<server-name>": "dist/index.js" },
  "dependencies": {
    "@modelcontextprotocol/sdk": "latest"
  },
  "devDependencies": {
    "typescript": "latest",
    "@types/node": "latest"
  }
}
```

### 서버 구현

```typescript
// src/index.ts
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  ListToolsRequestSchema,
  CallToolRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

const server = new Server(
  { name: "<server-name>", version: "0.1.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "search_docs",
      description: "문서를 검색합니다",
      inputSchema: {
        type: "object" as const,
        properties: {
          query: { type: "string", description: "검색 키워드" },
        },
        required: ["query"],
      },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "search_docs") {
    return {
      content: [{ type: "text", text: `결과: ${args?.query}` }],
    };
  }

  throw new Error(`Unknown tool: ${name}`);
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

---

## 에이전트에서 MCP 서버 사용

### OpenAI Agents SDK — MCPServerStdio (로컬 프로세스)

```python
from agents.mcp.server import MCPServerStdio

# Python MCP 서버
my_server = MCPServerStdio(
    params={
        "command": "uvx",
        "args": ["<server-name>"],
    },
    cache_tools_list=True,  # 도구 목록 캐싱 (성능 향상)
)

# Node.js MCP 서버
node_server = MCPServerStdio(
    params={
        "command": "npx",
        "args": ["-y", "<server-name>"],
    },
)

# 사용 (반드시 async with 블록 안에서)
async with my_server:
    agent = Agent(
        mcp_servers=[my_server],
        name="My Agent",
        instructions="...",
    )
    result = await Runner.run(agent, "문서에서 MCP 관련 내용 찾아줘")
```

### OpenAI Agents SDK — HostedMCPTool (원격 HTTP)

```python
from agents import HostedMCPTool

hosted_tool = HostedMCPTool(
    tool_config={
        "server_url": "https://mcp.example.com/mcp",
        "type": "mcp",
        "server_label": "MyRemoteTool",
        "server_description": "원격 MCP 서버 도구",
        "require_approval": "never",  # "always" | "never"
    }
)

agent = Agent(
    tools=[hosted_tool],
    ...
)
```

### Claude Code에서 MCP 서버 사용

`~/.claude/settings.json` 또는 프로젝트 `.claude/settings.json`에 추가:

```json
{
  "mcpServers": {
    "<server-name>": {
      "command": "uvx",
      "args": ["<server-name>"]
    }
  }
}
```

---

## MCP 리소스 (선택)

도구 외에 읽기 전용 데이터를 제공할 수 있다:

```python
from mcp.types import Resource

@server.list_resources()
async def list_resources():
    return [
        Resource(
            uri="docs://api/reference",
            name="API Reference",
            description="API 문서",
            mimeType="text/markdown",
        ),
    ]

@server.read_resource()
async def read_resource(uri: str):
    if uri == "docs://api/reference":
        return "# API Reference\n..."
```

---

## MCP 프롬프트 (선택)

재사용 가능한 프롬프트 템플릿 제공:

```python
from mcp.types import Prompt, PromptArgument, PromptMessage, TextContent

@server.list_prompts()
async def list_prompts():
    return [
        Prompt(
            name="analyze",
            description="코드 분석 프롬프트",
            arguments=[
                PromptArgument(name="code", description="분석할 코드", required=True),
            ],
        ),
    ]

@server.get_prompt()
async def get_prompt(name: str, arguments: dict):
    if name == "analyze":
        return [
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=f"다음 코드를 분석해주세요:\n{arguments['code']}",
                ),
            ),
        ]
```

---

## 참고 문서

- [MCP 프로토콜 참고](references/mcp-reference.md)
