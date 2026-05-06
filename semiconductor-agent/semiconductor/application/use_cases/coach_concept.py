from __future__ import annotations

from semiconductor.domain.ports import ICoachLLM

_MAX_HINT_COUNT = 4


class CoachConceptUseCase:
    def __init__(self, coach_llm: ICoachLLM) -> None:
        self._coach = coach_llm

    def execute(
        self,
        topic: str,
        messages: list,
        hint_count: int,
    ) -> tuple[str, int]:
        response = self._coach.get_response(
            topic=topic,
            messages=messages,
            hint_count=hint_count,
        )
        new_hint_count = min(hint_count + 1, _MAX_HINT_COUNT)
        return response, new_hint_count
