# CrewAI 참고 자료

## 공식 문서
- 문서: https://docs.crewai.com/
- GitHub: https://github.com/crewAIInc/crewAI
- PyPI: https://pypi.org/project/crewai/

## 핵심 개념

### CrewBase 데코레이터
`@CrewBase`로 클래스를 Crew로 만듦. `config/agents.yaml`, `config/tasks.yaml` 자동 로드.
- `self.agents_config["agent_name"]` — YAML 에이전트 설정 접근
- `self.tasks_config["task_name"]` — YAML 태스크 설정 접근
- `self.agents` — 모든 `@agent` 메서드의 리스트
- `self.tasks` — 모든 `@task` 메서드의 리스트

### Agent YAML 필드
| 필드 | 설명 |
|------|------|
| `role` | 에이전트 역할 (직함) |
| `goal` | 주요 목표 |
| `backstory` | 전문성/배경 서술 |
| `verbose` | 상세 로그 (bool) |
| `inject_date` | 현재 날짜 주입 (bool) |
| `llm` | 모델 (예: `openai/o4-mini-2025-04-16`) |
| `respect_context_window` | 컨텍스트 윈도우 관리 (bool) |

### Task YAML 필드
| 필드 | 설명 |
|------|------|
| `description` | 태스크 상세 설명 (`{변수}` 지원) |
| `expected_output` | 기대 출력 형식 |
| `agent` | 담당 에이전트 이름 |
| `markdown` | 마크다운 출력 (bool) |
| `output_file` | 출력 파일 경로 |
| `create_directory` | 출력 디렉토리 자동 생성 (bool) |

### Task Python 파라미터
| 파라미터 | 설명 |
|----------|------|
| `config` | YAML 설정 딕셔너리 |
| `output_pydantic` | Pydantic 모델 클래스 (구조화 출력) |
| `context` | 의존 태스크 리스트 |

### Flow 데코레이터
| 데코레이터 | 설명 |
|-----------|------|
| `@start()` | 플로우 시작점 |
| `@listen(method_or_string)` | 특정 메서드 완료 시 실행 |
| `@router(method)` | 조건 분기 (문자열 반환) |
| `or_(a, b)` | 여러 이벤트 중 하나라도 발생하면 트리거 |
| `and_(a, b)` | 모든 이벤트가 발생해야 트리거 |

### Knowledge Sources
- `TextFileKnowledgeSource(file_paths=[...])` — 텍스트 파일
- `PDFKnowledgeSource` — PDF 문서
- `CSVKnowledgeSource` — CSV 데이터
- 에이전트의 `knowledge_sources` 파라미터에 전달
