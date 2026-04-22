# Restaurant Bot: Guardrails & Complaints

OpenAI Agents SDK + Clean Architecture 기반 레스토랑 봇. 입력/출력 가드레일과 전문 Complaints Agent를 통합했습니다.

## 기능

- **Input Guardrails** — 주제에서 벗어난 질문, 부적절한 언어를 자동으로 필터링
- **Output Guardrails** — 봇이 부적절한 응답을 하지 않도록 보장 (내부 정보 노출 방지)
- **Complaints Agent** — 불만 고객을 세심하게 공감하며 해결책 제시 (할인 쿠폰, 매니저 연락 등)
- **Multi-Agent Handoff** — Triage Agent가 Menu / Reservation / Order / Complaints Agent로 자동 라우팅
- **Streamlit UI** — `st.chat_input` / `st.chat_message` 기반 채팅 인터페이스
- **Jupyter Notebook** — `input()` 기반 대화형 실행

## Architecture

Clean Architecture 4계층:

```
domain/          → 엔티티 (MenuItem, Reservation, Order, Complaint) + 리포지토리 포트
application/     → Use Cases + AppContext
infrastructure/  → 인메모리 리포지토리, RunConfig 로딩
presentation/    → Agents, Tools, Guardrails, Pydantic Models
```

## Agents & Flow

```
        ┌──────────────┐   input_guardrail
        │ Triage Agent │ ◀─────────── 사용자 입력
        └──────┬───────┘
               │ handoff
  ┌────────────┼────────────┬────────────┐
  ▼            ▼            ▼            ▼
Menu     Reservation     Order     Complaints (output_guardrail)
```

## 실행 방법

```bash
uv sync

# Streamlit UI
uv run streamlit run main.py

# Jupyter Notebook
uv run jupyter notebook main.ipynb
```

## 환경 설정

`.env`:

```env
OPENAI_API_KEY='your-openai-api-key'
AI_BASE_URL=                # 커스텀 프록시 사용 시 설정
```

## 예시 대화

### 불만 처리 (Complaints Agent 핸드오프)

```
User: 음식이 너무 별로였고 직원도 불친절했어...
Triage: 정말 죄송합니다. 담당자에게 연결해 드릴게요.
  [Complaints Agent handoff]
Complaints: 불쾌한 경험을 드려 진심으로 사과드립니다.
다음 방문 시 50% 할인 쿠폰을 제공해 드리거나, 매니저가 직접 연락드리도록 하겠습니다.
```

### 주제 이탈 (Input Guardrail 작동)

```
User: 인생의 의미가 뭘까?
Bot: 죄송하지만 레스토랑 관련 질문에만 답변드리고 있어요.
     메뉴 확인, 예약, 주문, 불만 접수를 도와드릴 수 있습니다.
```
