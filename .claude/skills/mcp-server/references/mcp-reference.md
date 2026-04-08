# MCP (Model Context Protocol) 참고 자료

## 공식 문서
- 스펙: https://modelcontextprotocol.io/
- Python SDK: https://github.com/modelcontextprotocol/python-sdk
- TypeScript SDK: https://github.com/modelcontextprotocol/typescript-sdk
- 서버 목록: https://github.com/modelcontextprotocol/servers

## MCP 구성 요소

| 구성 요소 | 설명 | 용도 |
|-----------|------|------|
| **Tools** | 실행 가능한 함수 | 검색, API 호출, 데이터 처리 |
| **Resources** | 읽기 전용 데이터 | 문서, 설정, 스키마 |
| **Prompts** | 재사용 템플릿 | 분석, 요약, 코드 리뷰 |

## 전송 방식

| 방식 | 클래스 | 용도 |
|------|--------|------|
| **Stdio** | `StdioServerTransport` | 로컬 프로세스 (가장 일반적) |
| **SSE** | `SSEServerTransport` | HTTP 기반 원격 서버 |

## 인기 MCP 서버 (uvx로 실행 가능)

| 서버 | 명령어 |
|------|--------|
| Yahoo Finance | `uvx mcp-yahoo-finance` |
| Time/Timezone | `uvx mcp-server-time --local-timezone=Asia/Seoul` |
| GitHub | `uvx mcp-server-github` |
| SQLite | `uvx mcp-server-sqlite --db-path ./data.db` |
| Filesystem | `uvx mcp-server-filesystem /path/to/dir` |

## 에이전트 연동 패턴

### MCPServerStdio (로컬)
- `params.command`: 실행 명령어 (`uvx`, `npx`, `python`)
- `params.args`: 명령어 인자
- `cache_tools_list`: 도구 목록 캐싱 (bool)
- 반드시 `async with` 컨텍스트 매니저 안에서 사용

### HostedMCPTool (원격)
- `tool_config.server_url`: MCP 서버 HTTP URL
- `tool_config.type`: `"mcp"` 고정
- `tool_config.server_label`: 표시 이름
- `tool_config.require_approval`: `"always"` | `"never"`
