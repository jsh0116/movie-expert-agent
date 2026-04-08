# Google ADK 참고 자료

## 공식 문서
- GitHub: https://github.com/google/adk-python
- PyPI: https://pypi.org/project/google-adk/

## 핵심 클래스

### Agent 타입
| 클래스 | 용도 |
|--------|------|
| `Agent` | 표준 LLM 에이전트 |
| `LlmAgent` | 경량 에이전트 |
| `SequentialAgent` | 순차 실행 파이프라인 |
| `ParallelAgent` | 병렬 실행 |

### Agent 생성자 파라미터
| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `name` | `str` | 에이전트 이름 |
| `description` | `str` | 에이전트 설명 (AgentTool에서 사용) |
| `instruction` | `str` | 시스템 프롬프트 |
| `model` | `LiteLlm` | LLM 모델 |
| `tools` | `list` | 도구 함수 또는 AgentTool |
| `sub_agents` | `list` | SequentialAgent/ParallelAgent용 |
| `output_schema` | `BaseModel` | Pydantic 출력 스키마 |
| `output_key` | `str` | 출력을 state에 저장할 키 |
| `before_model_callback` | `Callable` | LLM 호출 전 콜백 |

### ToolContext API
| 메서드/속성 | 설명 |
|-------------|------|
| `tool_context.state` | 세션 상태 딕셔너리 (읽기/쓰기) |
| `await tool_context.save_artifact(filename, artifact)` | 아티팩트 저장 |
| `await tool_context.load_artifact(filename=name)` | 아티팩트 로드 |
| `await tool_context.list_artifacts()` | 아티팩트 목록 |

### 아티팩트 생성
```python
artifact = types.Part(
    inline_data=types.Blob(mime_type="...", data=bytes_data)
)
```

### LiteLlm 모델 설정
```python
from google.adk.models.lite_llm import LiteLlm
MODEL = LiteLlm(model="openai/gpt-4o")        # OpenAI
MODEL = LiteLlm(model="anthropic/claude-sonnet-4-6")  # Anthropic
```

### Runner 이벤트 API
| 메서드 | 설명 |
|--------|------|
| `event.is_final_response()` | 최종 응답 여부 |
| `event.content.parts[0].text` | 응답 텍스트 |
| `event.get_function_calls()` | 도구 호출 목록 |
| `event.get_function_responses()` | 도구 응답 목록 |

### 세션 서비스
- `DatabaseSessionService(db_url="sqlite:///./session.db")` — SQLite 영속
- `InMemorySessionService()` — 인메모리 (테스트용)
- `create_session(app_name, user_id, state={})` — 초기 상태 전달

### 배포 (Vertex AI)
1. `vertexai.init(project, location, staging_bucket)`
2. `reasoning_engines.AdkApp(agent, enable_tracing=True)`
3. `vertexai.agent_engines.create(display_name, agent_engine, requirements, extra_packages, env_vars)`
