"""LangGraph @tool wrappers — qa_coach ReAct에서 LLM이 호출.

Adapter layer: infrastructure 구현체를 LangChain Tool 시그니처로 노출.
"""
from __future__ import annotations

from langchain_core.tools import tool

from semiconductor.infrastructure.tools.calculator import SemiconductorCalculator
from semiconductor.infrastructure.tools.vision import GeminiVisionAnalyzer
from semiconductor.infrastructure.tools.web_search import IndustrySearchService

# Lazy singleton — module-import 시점에는 외부 의존(DDG, Gemini) 초기화 회피.
# 첫 tool 호출 시점에 생성됨. 테스트는 patch로 주입.
_calc: SemiconductorCalculator | None = None
_search: IndustrySearchService | None = None
_vision: GeminiVisionAnalyzer | None = None


def _get_calc() -> SemiconductorCalculator:
    global _calc
    if _calc is None:
        _calc = SemiconductorCalculator()
    return _calc


def _get_search() -> IndustrySearchService:
    global _search
    if _search is None:
        _search = IndustrySearchService()
    return _search


def _get_vision() -> GeminiVisionAnalyzer:
    global _vision
    if _vision is None:
        _vision = GeminiVisionAnalyzer()
    return _vision


@tool
def industry_trend_search(query: str) -> str:
    """반도체 산업의 최신 동향·뉴스·발표를 검색합니다.

    LLM의 학습 cutoff 이후 정보 (HBM3E 양산, TSMC N2 일정, GAA 양산,
    EUV 도입, 회사 IR 발표 등)를 fetch할 때 사용.

    Args:
        query: 검색하고 싶은 반도체 관련 주제 (한국어/영어 모두 가능).
               예: "HBM3E 양산 시점", "TSMC N2 production"
    """
    return _get_search().search(query)


@tool
def calculate_threshold_voltage(
    tox_nm: float,
    na_per_cm3: float,
    phi_ms: float,
    qf: float = 0.0,
) -> str:
    """NMOS의 Threshold Voltage(Vth)를 계산합니다.

    Vth = Φms − Qf/Cox + 2Φf + √(2εsi·q·Na·2Φf) / Cox

    Args:
        tox_nm: 게이트 산화막 두께 [nm]
        na_per_cm3: p-substrate 도핑 농도 [/cm³] (예: 1e16)
        phi_ms: metal-semiconductor work function 차이 [V] (예: -0.5)
        qf: 산화막 고정 전하 [C/cm²], 기본 0
    """
    try:
        vth = _get_calc().threshold_voltage_nmos(tox_nm, na_per_cm3, phi_ms, qf)
        return f"Vth = {vth:.4f} V (tox={tox_nm}nm, Na={na_per_cm3:.1e}/cm³, Φms={phi_ms}V)"
    except ValueError as e:
        return f"❌ 입력값 오류: {e}"


@tool
def calculate_drain_current(
    mobility_cm2_vs: float,
    cox_f_per_cm2: float,
    w_over_l: float,
    vgs_minus_vth: float,
) -> str:
    """Long-channel NMOS의 saturation 영역 드레인 전류를 계산합니다.

    Id = (μn · Cox · W/L / 2) · (Vgs − Vth)²
    Vgs ≤ Vth → 컷오프, Id = 0.

    Args:
        mobility_cm2_vs: 캐리어 이동도 μn [cm²/V·s] (예: 400)
        cox_f_per_cm2: 단위면적 산화막 capacitance [F/cm²] (tox=10nm → 약 3.45e-7)
        w_over_l: 채널 폭/길이 비 W/L
        vgs_minus_vth: 게이트 overdrive 전압 [V]
    """
    try:
        id_a = _get_calc().drain_current_saturation(mobility_cm2_vs, cox_f_per_cm2, w_over_l, vgs_minus_vth)
        if id_a == 0.0:
            return f"Id = 0 (컷오프, Vgs ≤ Vth)"
        return f"Id = {id_a*1000:.4f} mA = {id_a:.4e} A"
    except ValueError as e:
        return f"❌ 입력값 오류: {e}"


@tool
def calculate_oxide_capacitance(tox_nm: float) -> str:
    """단위면적 산화막 capacitance Cox를 계산합니다.

    Cox = εox / tox, εox = 3.9·ε0

    Args:
        tox_nm: 산화막 두께 [nm]
    """
    try:
        cox = _get_calc().oxide_capacitance_per_area(tox_nm)
        return f"Cox = {cox:.4e} F/cm² (tox = {tox_nm} nm)"
    except ValueError as e:
        return f"❌ 입력값 오류: {e}"


@tool
def analyze_circuit_diagram(image_path: str) -> str:
    """회로도 이미지를 분석합니다 (예: 센스앰프, 차지펌프, 메모리 컨트롤러).

    Gemini 멀티모달이 트랜지스터 종류, 결선, 동작 원리를 텍스트로 풀어 설명합니다.

    Args:
        image_path: 로컬 회로도 파일 경로 (.png/.jpg/.webp)
    """
    prompt = (
        "당신은 반도체 회로 설계 전문가입니다. 이 회로도를 분석하세요:\n"
        "1. 회로 종류 (예: 센스앰프, 차지펌프 등)\n"
        "2. 사용된 트랜지스터·소자\n"
        "3. 신호 흐름과 동작 원리\n"
        "4. 핵심 설계 포인트\n"
        "한국어로 답변하세요."
    )
    return _get_vision().analyze(image_path, prompt)


@tool
def analyze_band_diagram(image_path: str) -> str:
    """에너지 밴드 다이어그램을 분석합니다 (MOSFET, p-n 접합, 헤테로 접합 등).

    Gemini가 페르미 준위, 공핍층, 캐리어 흐름 등을 설명합니다.

    Args:
        image_path: 밴드 다이어그램 이미지 경로
    """
    prompt = (
        "당신은 반도체 소자물리 전문가입니다. 이 에너지 밴드 다이어그램을 분석하세요:\n"
        "1. 어떤 소자/구조의 밴드 다이어그램인가\n"
        "2. EC, EV, EF (페르미 준위) 위치\n"
        "3. 공핍층·축적층 등 핵심 영역\n"
        "4. 캐리어 흐름과 동작 메커니즘\n"
        "한국어로 답변하세요."
    )
    return _get_vision().analyze(image_path, prompt)


@tool
def analyze_engineering_image(image_path: str, query: str) -> str:
    """일반 반도체 공학 이미지(레이아웃, SEM, 공정 단면도 등)를 분석합니다.

    Args:
        image_path: 이미지 파일 경로
        query: 구체적 질문 (예: "이 SEM 사진의 결함 종류는?")
    """
    prompt = (
        f"당신은 반도체 공학 박사 수준의 전문가입니다. 이 이미지를 분석하고 질문에 답하세요.\n"
        f"질문: {query}\n"
        "한국어로 핵심을 짚어 답변하세요."
    )
    return _get_vision().analyze(image_path, prompt)


# qa_coach에 바인딩할 모든 tool — 검색·계산·비전
COACH_TOOLS = [
    industry_trend_search,
    calculate_threshold_voltage,
    calculate_drain_current,
    calculate_oxide_capacitance,
    analyze_circuit_diagram,
    analyze_band_diagram,
    analyze_engineering_image,
]
