"""TDD: Domain entity invariants — write tests FIRST, then implement."""
import pytest
from semiconductor.domain.entities import (
    DiagnosticResult,
    EssayEvaluation,
    EssayPrompt,
    EvaluationResult,
    Question,
)


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

    def test_evaluation_carries_model_answer(self):
        # 모범답안(LLM이 생성한 만점 답변 예시)이 평가 결과에 포함되어야 한다
        ev = EvaluationResult(
            accuracy_score=20, depth_score=10, terminology_score=10,
            total_score=40, feedback="x", strong_points=[], weak_points=[],
            question="FinFET 설명", model_answer="FinFET은 3D 구조의 트랜지스터로...",
        )
        assert ev.model_answer.startswith("FinFET은")

    def test_model_answer_defaults_to_empty(self):
        # 기존 호출자 호환을 위해 model_answer 미지정 시 빈 문자열이어야 한다
        ev = EvaluationResult(
            accuracy_score=20, depth_score=10, terminology_score=10,
            total_score=40, feedback="x", strong_points=[], weak_points=[], question="q"
        )
        assert ev.model_answer == ""

    def test_specialist_commentary_field_exists(self):
        # 도메인 전문가 코멘트(예: "소자 전문가 관점에서…")가 평가에 포함된다
        ev = EvaluationResult(
            accuracy_score=20, depth_score=10, terminology_score=10,
            total_score=40, feedback="x", strong_points=[], weak_points=[],
            question="q", specialist_commentary="소자 전문가 관점에서 게이트 산화막 두께를 더 명확히 언급하면 좋겠습니다.",
        )
        assert "소자 전문가" in ev.specialist_commentary

    def test_specialist_commentary_defaults_to_empty(self):
        ev = EvaluationResult(
            accuracy_score=20, depth_score=10, terminology_score=10,
            total_score=40, feedback="x", strong_points=[], weak_points=[], question="q"
        )
        assert ev.specialist_commentary == ""

    def test_follow_up_question_field_exists(self):
        # 평가 후 약점을 파고드는 후속 질문(real interviewer probing)
        ev = EvaluationResult(
            accuracy_score=20, depth_score=10, terminology_score=10,
            total_score=40, feedback="x", strong_points=[], weak_points=[],
            question="q", follow_up_question="그럼 GAA로 넘어가는 이유는?",
        )
        assert ev.follow_up_question.startswith("그럼 GAA")

    def test_follow_up_question_defaults_to_empty(self):
        ev = EvaluationResult(
            accuracy_score=20, depth_score=10, terminology_score=10,
            total_score=40, feedback="x", strong_points=[], weak_points=[], question="q"
        )
        assert ev.follow_up_question == ""


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


class TestEssayPrompt:
    def test_정상_prompt_생성(self):
        p = EssayPrompt(
            company="samsung_ds", item="지원동기",
            description="삼성 DS에 지원하는 이유와 본인의 강점",
            word_limit=1500,
        )
        assert p.company == "samsung_ds"
        assert p.item == "지원동기"

    def test_잘못된_회사는_거부(self):
        with pytest.raises(ValueError):
            EssayPrompt(company="lg_display", item="지원동기", description="x", word_limit=1500)

    def test_잘못된_항목은_거부(self):
        with pytest.raises(ValueError):
            EssayPrompt(company="samsung_ds", item="이상한항목", description="x", word_limit=1500)

    def test_word_limit_0이하는_거부(self):
        with pytest.raises(ValueError):
            EssayPrompt(company="samsung_ds", item="지원동기", description="x", word_limit=0)


class TestEssayEvaluation:
    def test_정상_평가(self):
        ev = EssayEvaluation(
            fit_score=25, structure_score=20, specificity_score=20, writing_score=15,
            total_score=80, feedback="좋습니다", strong_points=["구체적"],
            weak_points=["서론 약함"], revised_excerpt="서론 예시...",
            culture_alignment="삼성 인재상 '도전' 일치",
        )
        assert ev.total_score == 80
        assert ev.grade == "우수"

    def test_total_score_합계_불일치_거부(self):
        with pytest.raises(ValueError, match="total_score"):
            EssayEvaluation(
                fit_score=20, structure_score=20, specificity_score=20, writing_score=10,
                total_score=99,  # actual sum = 70
                feedback="x", strong_points=[], weak_points=[],
            )

    def test_fit_score_30_초과_거부(self):
        with pytest.raises(ValueError):
            EssayEvaluation(
                fit_score=35, structure_score=20, specificity_score=20, writing_score=15,
                total_score=90, feedback="x", strong_points=[], weak_points=[],
            )

    def test_grade_등급(self):
        cases = [
            (24, 18, 18, 15, 75, "보통"),
            (15, 10, 10, 10, 45, "미흡"),
            (28, 22, 22, 18, 90, "우수"),
        ]
        for fit, struct, spec, write, total, expected_grade in cases:
            ev = EssayEvaluation(
                fit_score=fit, structure_score=struct, specificity_score=spec, writing_score=write,
                total_score=total, feedback="x", strong_points=[], weak_points=[],
            )
            assert ev.grade == expected_grade
