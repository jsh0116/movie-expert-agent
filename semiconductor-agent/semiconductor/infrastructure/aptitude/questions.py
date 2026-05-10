"""GSAT/SKCT 정적 문제 풀 — Phase 2B.

문제는 실제 적성검사 형식을 모방한 자체 작성 (저작권 안전). LLM 미사용.
"""
from __future__ import annotations

from semiconductor.domain.entities import AptitudeQuestion

_QUESTIONS: list[AptitudeQuestion] = [
    # ── GSAT ────────────────────────────────────────────────────
    AptitudeQuestion(
        test_type="GSAT", domain="수리",
        question="서로 다른 5개의 책을 책꽂이에 일렬로 배열할 때 영어책 2권이 서로 이웃하게 배열하는 경우의 수는?",
        choices=["24", "48", "60", "120"],
        correct_index=1,
        explanation="영어책 2권을 한 묶음으로 보면 4개를 배열 = 4! = 24, 영어책 내부 순서 = 2! = 2 → 24 × 2 = 48",
    ),
    AptitudeQuestion(
        test_type="GSAT", domain="수리",
        question="A, B 두 사람이 일을 한다. A 혼자 6시간, B 혼자 12시간이 걸리는 일을 두 사람이 함께 하면 몇 시간 걸리는가?",
        choices=["3시간", "4시간", "5시간", "6시간"],
        correct_index=1,
        explanation="A의 시간당 일량 = 1/6, B = 1/12. 합 = 1/6 + 1/12 = 3/12 = 1/4. 따라서 4시간.",
    ),
    AptitudeQuestion(
        test_type="GSAT", domain="추리",
        question="다음 도형의 규칙: △ → ◇ → ○ → △ → ◇ → ? 다음에 올 도형은?",
        choices=["△", "◇", "○", "□"],
        correct_index=2,
        explanation="3개 도형이 △→◇→○ 순으로 반복되므로 ◇ 다음은 ○.",
    ),
    AptitudeQuestion(
        test_type="GSAT", domain="언어",
        question="다음 중 ‘반도체’와 가장 관련이 깊은 단어는?",
        choices=["광합성", "트랜지스터", "코어", "분자운동"],
        correct_index=1,
        explanation="반도체의 가장 핵심적인 응용은 트랜지스터(스위치/증폭 소자). 다른 단어는 무관.",
    ),
    AptitudeQuestion(
        test_type="GSAT", domain="공간",
        question="정육면체를 펼친 전개도에서 마주보는 두 면의 위치 관계는?",
        choices=["인접", "이격(서로 떨어짐)", "포개짐", "대각"],
        correct_index=1,
        explanation="정육면체 전개도에서 마주보는 두 면은 한 면을 사이에 두고 떨어져 있다(이격).",
    ),
    # ── SKCT ────────────────────────────────────────────────────
    AptitudeQuestion(
        test_type="SKCT", domain="수리",
        question="원가 2000원의 상품에 25% 이익을 붙여 정가를 매겼다가 정가의 10%를 할인해 판매했다. 이익은?",
        choices=["50원", "200원", "250원", "500원"],
        correct_index=2,
        explanation="정가 = 2000 × 1.25 = 2500. 판매가 = 2500 × 0.9 = 2250. 이익 = 2250 - 2000 = 250원.",
    ),
    AptitudeQuestion(
        test_type="SKCT", domain="수리",
        question="3, 6, 11, 18, 27, ?, 다음 수는?",
        choices=["34", "36", "38", "40"],
        correct_index=2,
        explanation="차이가 3, 5, 7, 9 (홀수 증가). 다음 차이는 11 → 27 + 11 = 38.",
    ),
    AptitudeQuestion(
        test_type="SKCT", domain="추리",
        question="모든 A는 B이다. 어떤 B는 C가 아니다. 따라서?",
        choices=[
            "모든 A는 C이다",
            "어떤 A는 C가 아닐 수도 있다",
            "모든 A는 C가 아니다",
            "어떤 B는 A이다",
        ],
        correct_index=1,
        explanation="‘모든 A는 B이다’와 ‘어떤 B는 C가 아니다’만으로는 A와 C의 관계를 확정할 수 없다. ‘어떤 A는 C가 아닐 수도 있다’가 가능한 결론.",
    ),
    AptitudeQuestion(
        test_type="SKCT", domain="언어",
        question="‘메모리 셀(memory cell)’의 의미와 가장 가까운 것은?",
        choices=["반도체 회로의 작은 저장 단위", "RAM의 외형", "CPU 내부 레지스터", "PCB 패턴"],
        correct_index=0,
        explanation="메모리 셀은 1비트를 저장하는 반도체 회로의 가장 작은 단위. RAM·NAND 모두 셀 어레이로 구성.",
    ),
    AptitudeQuestion(
        test_type="SKCT", domain="공간",
        question="입체 도형을 90도 회전시켰을 때 위에서 본 모양은? (정육면체 위에 사각뿔이 얹어진 도형)",
        choices=["원", "정사각형 + 마름모", "정사각형만", "삼각형"],
        correct_index=2,
        explanation="위에서 보면 정육면체의 윗면(정사각형)이 그대로 보이고, 사각뿔의 꼭짓점은 점으로 보여 정사각형만 보임.",
    ),
]


def get_questions(test_type: str | None = None) -> list[AptitudeQuestion]:
    if test_type is None:
        return list(_QUESTIONS)
    return [q for q in _QUESTIONS if q.test_type == test_type]


def pick_question(test_type: str | None, asked_count: int) -> AptitudeQuestion | None:
    pool = get_questions(test_type)
    if not pool:
        return None
    return pool[asked_count % len(pool)]
