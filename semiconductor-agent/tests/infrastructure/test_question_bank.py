"""TDD: Question bank infrastructure tests."""
import pytest
from semiconductor.infrastructure.question_bank import InMemoryQuestionRepository


class TestInMemoryQuestionRepository:
    def setup_method(self):
        self.repo = InMemoryQuestionRepository()

    def test_samsung_ds_has_all_four_domains(self):
        for domain in ("소자", "공정", "회로", "트렌드"):
            questions = self.repo.get_questions("samsung_ds", domain)
            assert len(questions) >= 3, f"삼성DS {domain} 질문이 부족합니다"

    def test_sk_hynix_has_all_four_domains(self):
        for domain in ("소자", "공정", "회로", "트렌드"):
            questions = self.repo.get_questions("sk_hynix", domain)
            assert len(questions) >= 3, f"SK하이닉스 {domain} 질문이 부족합니다"

    def test_unknown_company_returns_empty(self):
        questions = self.repo.get_questions("unknown_company")
        assert questions == []

    def test_unknown_domain_returns_empty(self):
        questions = self.repo.get_questions("samsung_ds", "없는도메인")
        assert questions == []

    def test_no_domain_filter_returns_all_questions(self):
        all_qs = self.repo.get_questions("samsung_ds")
        assert len(all_qs) >= 12  # 4 domains × 3+ questions

    def test_questions_have_non_empty_key_points(self):
        questions = self.repo.get_questions("samsung_ds", "소자")
        for q in questions:
            assert len(q.key_points) >= 2, f"질문 '{q.question[:30]}...'의 key_points가 부족합니다"

    def test_sk_hynix_questions_differ_from_samsung(self):
        samsung_texts = {q.question for q in self.repo.get_questions("samsung_ds")}
        sk_texts = {q.question for q in self.repo.get_questions("sk_hynix")}
        overlap = samsung_texts & sk_texts
        # Some overlap is OK (shared fundamentals), but not all questions should be the same
        assert len(overlap) < len(samsung_texts), "삼성DS와 SK하이닉스 질문 풀이 동일합니다"
