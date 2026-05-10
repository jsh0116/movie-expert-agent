"""반도체 디바이스 파라미터 계산기 — pure Python, LLM 수학 약점 보완.

Reference: Neamen, "Semiconductor Physics and Devices" Ch. 4-5
"""
from __future__ import annotations

import math

# 물리 상수
_Q = 1.602e-19           # 전자 전하 [C]
_EPS0 = 8.854e-14        # 진공 유전율 [F/cm]
_EPS_OX = 3.9 * _EPS0    # SiO2 유전율 [F/cm]
_EPS_SI = 11.7 * _EPS0   # Si 유전율 [F/cm]
_KT_Q = 0.02585          # 열전압 (300K) [V]
_NI_SI = 1.5e10          # Si 진성 캐리어 농도 [/cm³]


class SemiconductorCalculator:
    """MOSFET 파라미터 계산. 모든 입력은 단위 명시된 SI 변환 후 사용."""

    def oxide_capacitance_per_area(self, tox_nm: float) -> float:
        """Cox [F/cm²] = εox / tox. tox는 nm 단위 입력."""
        if tox_nm <= 0:
            raise ValueError(f"tox는 양수여야 합니다: {tox_nm}")
        tox_cm = tox_nm * 1e-7
        return _EPS_OX / tox_cm

    def fermi_potential_p_substrate(self, na_per_cm3: float) -> float:
        """Φf [V] = (kT/q) · ln(Na / ni). p-type substrate 기준 (NMOS bulk)."""
        if na_per_cm3 <= 0:
            raise ValueError(f"도핑 농도는 양수여야 합니다: {na_per_cm3}")
        return _KT_Q * math.log(na_per_cm3 / _NI_SI)

    def threshold_voltage_nmos(
        self,
        tox_nm: float,
        na_per_cm3: float,
        phi_ms: float,
        qf: float = 0.0,
    ) -> float:
        """NMOS Vth [V].

        Vth = Φms - Qf/Cox + 2Φf + √(2εsi·q·Na·2Φf) / Cox

        Args:
            tox_nm: 산화막 두께 [nm]
            na_per_cm3: p-substrate 도핑 [/cm³]
            phi_ms: metal-semiconductor work function 차이 [V]
            qf: 산화막 고정 전하 [C/cm²], 기본 0

        Returns:
            Threshold voltage [V]
        """
        if tox_nm <= 0:
            raise ValueError(f"tox는 양수여야 합니다: {tox_nm}")
        if na_per_cm3 <= 0:
            raise ValueError(f"도핑 농도는 양수여야 합니다: {na_per_cm3}")

        cox = self.oxide_capacitance_per_area(tox_nm)
        phi_f = self.fermi_potential_p_substrate(na_per_cm3)
        bulk_charge = math.sqrt(2 * _EPS_SI * _Q * na_per_cm3 * 2 * phi_f)

        return phi_ms - qf / cox + 2 * phi_f + bulk_charge / cox

    def drain_current_saturation(
        self,
        mobility_cm2_vs: float,
        cox_f_per_cm2: float,
        w_over_l: float,
        vgs_minus_vth: float,
    ) -> float:
        """Long-channel NMOS 포화 영역 드레인 전류.

        Id = (μn · Cox · (W/L) / 2) · (Vgs - Vth)²
        Vgs < Vth → 컷오프, Id = 0
        """
        if mobility_cm2_vs <= 0:
            raise ValueError(f"이동도는 양수여야 합니다: {mobility_cm2_vs}")
        if cox_f_per_cm2 <= 0:
            raise ValueError(f"Cox는 양수여야 합니다: {cox_f_per_cm2}")
        if w_over_l <= 0:
            raise ValueError(f"W/L는 양수여야 합니다: {w_over_l}")

        if vgs_minus_vth <= 0:
            return 0.0  # 컷오프

        return 0.5 * mobility_cm2_vs * cox_f_per_cm2 * w_over_l * (vgs_minus_vth ** 2)
