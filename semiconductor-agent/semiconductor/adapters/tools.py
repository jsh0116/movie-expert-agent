"""LangGraph @tool wrappers — qa_coach ReAct에서 LLM이 호출.

Adapter layer: infrastructure 구현체를 LangChain Tool 시그니처로 노출.
"""
from __future__ import annotations

from langchain_core.tools import tool

from semiconductor.infrastructure.tools.calculator import SemiconductorCalculator
from semiconductor.infrastructure.tools.web_search import IndustrySearchService

# Lazy singleton — module-import 시점에는 외부 의존(DDG) 초기화 회피.
# 첫 tool 호출 시점에 생성됨. 테스트는 patch로 주입.
_calc: SemiconductorCalculator | None = None
_search: IndustrySearchService | None = None


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


# qa_coach에 바인딩할 모든 tool
COACH_TOOLS = [
    industry_trend_search,
    calculate_threshold_voltage,
    calculate_drain_current,
    calculate_oxide_capacitance,
]
