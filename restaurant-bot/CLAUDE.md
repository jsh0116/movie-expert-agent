# CLAUDE.md

## Project Overview

OpenAI Agents SDK + Clean Architecture로 구현한 레스토랑 봇. Guardrails와 Complaints Agent를 통해 부적절한 요청을 차단하고, 불만 고객을 세심하게 처리한다.

## Commands

```bash
uv sync                                # 의존성 설치
uv run streamlit run main.py           # Streamlit UI
uv run jupyter notebook main.ipynb     # 노트북 실행
```

## Architecture

Clean Architecture 4계층 구조:

- **Domain** (`domain/`) — 엔티티(`MenuItem`, `Reservation`, `Order`, `Complaint`, `OrderLine`, `ComplaintSeverity`)와 포트(`MenuRepository`, `ReservationRepository`, `OrderRepository`, `ComplaintRepository`)
- **Application** (`application/`) — 유스케이스(`GetMenuUseCase`, `MakeReservationUseCase`, `PlaceOrderUseCase`, `RegisterComplaintUseCase`)와 `AppContext`
- **Infrastructure** (`infrastructure/`) — 인메모리 리포지토리 구현, `load_run_config()`
- **Presentation** (`presentation/`) — 에이전트, 도구, 가드레일, Pydantic 모델

## Agents

| 에이전트 | 역할 | 도구 | 가드레일 |
|---------|------|-----|---------|
| `Triage Agent` | 라우팅 허브 | - | `input_guardrail` |
| `Menu Agent` | 메뉴 안내 | `get_menu` | - |
| `Reservation Agent` | 예약 처리 | `make_reservation` | - |
| `Order Agent` | 주문 처리 | `get_menu`, `place_order` | - |
| `Complaints Agent` | 불만 처리 | `register_complaint`, `offer_discount`, `escalate_to_manager` | `output_guardrail` |

## Guardrails

- **Input Guardrail** (`restaurant_input_guardrail`): 주제 이탈(off-topic), 부적절한 언어를 판단하여 Triage에서 차단
- **Output Guardrail** (`restaurant_output_guardrail`): 비전문적 응답, 내부 정보 노출을 판단하여 Complaints Agent 응답 후 차단

## Key Configuration

- `.env`에 `OPENAI_API_KEY` 필수
- `AI_BASE_URL`이 있으면 `OpenAIProvider(base_url=..., use_responses=False)` 사용 (Chat Completions)
- `RunConfig`에 `tracing_disabled=True` 설정
- 모든 에이전트 모델: `gpt-4o-mini`, 응답 언어: 한국어
