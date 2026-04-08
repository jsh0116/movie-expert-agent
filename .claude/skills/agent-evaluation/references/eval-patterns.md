# 에이전트 평가 패턴 참고

## 평가 접근법

### 1. Golden Dataset
- 입력-기대출력 쌍을 미리 정의
- 자동화 비교로 회귀 감지
- 새 기능 추가 시 기존 케이스 유지

### 2. LLM-as-Judge
- 다른 LLM이 응답 품질을 평가
- 정량화하기 어려운 메트릭(톤, 유용성)에 적합
- Judge 프롬프트를 세심하게 설계해야 함

### 3. A/B 테스트
- 프롬프트/모델 변경 전후 비교
- 동일 입력셋에 대해 두 버전 실행
- 통계적 유의성 확인

## 프레임워크별 테스트 유틸

### OpenAI Agents SDK
- `Runner.run()` — 동기 실행으로 결과 즉시 확인
- `result.final_output` — 최종 응답
- `result.last_agent` — 마지막 활성 에이전트 (핸드오프 검증)
- `InputGuardrailTripwireTriggered` / `OutputGuardrailTripwireTriggered` — 가드레일 예외

### CrewAI
- `crew.kickoff()` — 동기 실행
- `result.tasks_output` — 태스크별 출력 리스트
- `result.tasks_output[i].pydantic` — 구조화 출력 접근
- `result.tasks_output[i].raw` — 원시 텍스트 출력

### Google ADK
- `.evalset.json` — 평가 케이스 정의
- `.adk/eval_history/` — 실행 결과 히스토리
- `tool_uses` — 도구 호출 추적
- `intermediate_data` — 중간 처리 데이터

### LangGraph
- `graph.ainvoke()` — 비동기 실행
- `result["messages"]` — 전체 메시지 히스토리
- `message.type == "tool"` — 도구 호출 메시지 필터
- `config.configurable.thread_id` — 스레드별 격리

## 메트릭 수집 도구

| 도구 | 용도 |
|------|------|
| LangSmith | LangChain/LangGraph 트레이싱 및 평가 |
| Braintrust | LLM 앱 평가 플랫폼 |
| Promptfoo | 프롬프트/모델 벤치마크 |
| pytest | Python 단위/통합 테스트 |
