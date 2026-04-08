# OpenAI Agents SDK 참고 자료

## 공식 문서
- SDK GitHub: https://github.com/openai/openai-agents-python
- PyPI: https://pypi.org/project/openai-agents/

## 핵심 클래스 요약

### Agent
에이전트 정의. `name`, `instructions`, `tools`, `handoffs`, `guardrails`, `hooks`, `mcp_servers`, `output_type` 파라미터.

### Runner
에이전트 실행. `Runner.run()` (동기), `Runner.run_streamed()` (스트리밍). `session`, `context` 파라미터 지원.

### SQLiteSession
SQLite 기반 대화 메모리. `add_items()`, `get_items()`, `clear_session()`.

### Guardrails
- `@input_guardrail`: 입력 검증. `GuardrailFunctionOutput(tripwire_triggered=bool)` 반환.
- `@output_guardrail`: 출력 필터링. 동일 패턴.
- 예외: `InputGuardrailTripwireTriggered`, `OutputGuardrailTripwireTriggered`

### Handoffs
`handoff()` 함수로 에이전트 간 라우팅. `on_handoff` 콜백, `input_type` (Pydantic), `input_filter` (예: `handoff_filters.remove_all_tools`).

### AgentHooks
라이프사이클 콜백: `on_start`, `on_end`, `on_tool_start`, `on_tool_end`, `on_handoff`.

### VoicePipeline
음성 에이전트. `VoiceWorkflowBase` 서브클래스의 `run(transcription)` 메서드가 텍스트 청크를 yield.

### 빌트인 도구
`WebSearchTool`, `FileSearchTool`, `ImageGenerationTool`, `CodeInterpreterTool`, `HostedMCPTool`.

### MCP
`MCPServerStdio(params={"command": ..., "args": [...]})` — `async with` 블록 안에서 사용.
