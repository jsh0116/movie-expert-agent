from __future__ import annotations

from typing import Optional

from semiconductor.domain.entities import Question
from semiconductor.domain.ports import IQuestionRepository


class GetNextQuestionUseCase:
    def __init__(self, question_repo: IQuestionRepository) -> None:
        self._repo = question_repo

    def execute(
        self,
        company: str,
        domain: Optional[str],
        asked_count: int,
        max_questions: int,
    ) -> Optional[Question]:
        if asked_count >= max_questions:
            return None
        pool = self._repo.get_questions(company, domain)
        if not pool:
            return None
        idx = asked_count % len(pool)
        return pool[idx]
