"""TDD: Domain entity invariants — write tests FIRST, then implement."""
import pytest
from semiconductor.domain.entities import DiagnosticResult, EvaluationResult, Question


class TestQuestion:
    def test_question_has_required_fields(self):
        q = Question(domain="소자", question="FinFET 설명하세요", key_points=["게이트", "채널"])
        assert q.domain == "소자"
        assert q.question == "FinFET 설명하세요"
        assert q.key_points == ["게이트", "채널"]

    def test_question_domain_must_be_valid(self):
        with pytest.raises(ValueError):
            Question(domain="잘못된도메인", question="질문", key_points=[])

    def test_question_text_cannot_be_empty(self):
        with pytest.raises(ValueError):
            Question(domain="소자", question="", key_points=[])


class TestEvaluationResult:
    def test_valid_evaluation(self):
        ev = EvaluationResult(
            accuracy_score=30,
            depth_score=20,
            terminology_score=20,
            total_score=70,
            feedback="좋은 답변입니다.",
            strong_points=["정확한 정의"],
            weak_points=["깊이 부족"],
            question="FinFET 설명",
        )
        assert ev.total_score == 70

    def test_total_score_must_equal_sum(self):
        with pytest.raises(ValueError, match="total_score"):
            EvaluationResult(
                accuracy_score=30,
                depth_score=20,
                terminology_score=20,
                total_score=99,  # wrong
                feedback="x",
                strong_points=[],
                weak_points=[],
                question="q",
            )

    def test_accuracy_score_range(self):
        with pytest.raises(ValueError):
            EvaluationResult(
                accuracy_score=50,  # max is 40
                depth_score=20,
                terminology_score=20,
                total_score=90,
                feedback="x",
                strong_points=[],
                weak_points=[],
                question="q",
            )

    def test_depth_score_range(self):
        with pytest.raises(ValueError):
            EvaluationResult(
                accuracy_score=40,
                depth_score=40,  # max is 30
                terminology_score=20,
                total_score=100,
                feedback="x",
                strong_points=[],
                weak_points=[],
                question="q",
            )

    def test_terminology_score_range(self):
        with pytest.raises(ValueError):
            EvaluationResult(
                accuracy_score=40,
                depth_score=30,
                terminology_score=35,  # max is 30
                total_score=105,
                feedback="x",
                strong_points=[],
                weak_points=[],
                question="q",
            )

    def test_grade_property_excellent(self):
        ev = EvaluationResult(
            accuracy_score=35, depth_score=25, terminology_score=25,
            total_score=85, feedback="x", strong_points=[], weak_points=[], question="q"
        )
        assert ev.grade == "우수"

    def test_grade_property_average(self):
        ev = EvaluationResult(
            accuracy_score=20, depth_score=15, terminology_score=15,
            total_score=50, feedback="x", strong_points=[], weak_points=[], question="q"
        )
        assert ev.grade == "보통"

    def test_grade_property_poor(self):
        ev = EvaluationResult(
            accuracy_score=10, depth_score=5, terminology_score=5,
            total_score=20, feedback="x", strong_points=[], weak_points=[], question="q"
        )
        assert ev.grade == "미흡"


class TestDiagnosticResult:
    def test_valid_diagnostic(self):
        dr = DiagnosticResult(
            domain_scores={"소자": 80, "공정": 45, "회로": 60, "트렌드": 70},
            weak_topics=["ALD"],
            strong_topics=["DRAM 셀"],
            recommended_next="ALD 복습 추천",
        )
        assert dr.weakest_domain == "공정"

    def test_domain_scores_must_be_0_to_100(self):
        with pytest.raises(ValueError):
            DiagnosticResult(
                domain_scores={"소자": 150},  # > 100
                weak_topics=[],
                strong_topics=[],
                recommended_next="x",
            )

    def test_weakest_domain_with_all_zeros(self):
        dr = DiagnosticResult(
            domain_scores={"소자": 0, "공정": 0, "회로": 0, "트렌드": 0},
            weak_topics=[],
            strong_topics=[],
            recommended_next="전반적 학습 필요",
        )
        assert dr.weakest_domain in ("소자", "공정", "회로", "트렌드")
