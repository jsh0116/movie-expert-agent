from pydantic import BaseModel


class InputGuardrailOutput(BaseModel):
    """입력 가드레일 판정 결과."""

    is_off_topic: bool
    is_inappropriate: bool
    reason: str


class HandoffData(BaseModel):
    """에이전트 간 핸드오프 데이터."""

    issue_type: str
    reason: str
