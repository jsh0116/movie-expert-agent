"""Infrastructure: IQuestionRepository implementation backed by in-memory data."""
from __future__ import annotations

from typing import Optional

from semiconductor.domain.entities import Question
from semiconductor.domain.ports import IQuestionRepository
from semiconductor.infrastructure.question_bank._samsung_ds import QUESTIONS as _SAMSUNG_DS
from semiconductor.infrastructure.question_bank._sk_hynix import QUESTIONS as _SK_HYNIX

_BANK: dict[str, dict[str, list[Question]]] = {
    "samsung_ds": _SAMSUNG_DS,
    "sk_hynix": _SK_HYNIX,
}


class InMemoryQuestionRepository(IQuestionRepository):
    def get_questions(self, company: str, domain: Optional[str] = None) -> list[Question]:
        bank = _BANK.get(company, {})
        if domain:
            return list(bank.get(domain, []))
        all_qs: list[Question] = []
        for qs in bank.values():
            all_qs.extend(qs)
        return all_qs
