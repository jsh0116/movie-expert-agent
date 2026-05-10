"""TDD: 반도체 디바이스 파라미터 계산기 — pure Python, 외부 의존 없음."""
import math

import pytest

from semiconductor.infrastructure.tools.calculator import SemiconductorCalculator


class TestThresholdVoltage:
    """Vth = Φms - Qf/Cox + 2Φf + √(2εsi·q·Na·2Φf) / Cox

    표준 NMOS 예시 (Neamen 4.4):
      tox=10nm, Na=1e16/cm³, Φms=-0.5V, Qf=0
      → Vth ≈ 0.4~0.5V 영역
    """

    def test_정상_NMOS_vth_계산(self):
        calc = SemiconductorCalculator()
        vth = calc.threshold_voltage_nmos(
            tox_nm=10.0,
            na_per_cm3=1e16,
            phi_ms=-0.5,
            qf=0.0,
        )
        # 합리적 범위 검증 (정확한 값이 아니라 영역)
        assert 0.0 < vth < 1.0

    def test_도핑_농도_올리면_vth_증가(self):
        calc = SemiconductorCalculator()
        v_low = calc.threshold_voltage_nmos(tox_nm=10, na_per_cm3=1e16, phi_ms=-0.5, qf=0)
        v_high = calc.threshold_voltage_nmos(tox_nm=10, na_per_cm3=5e17, phi_ms=-0.5, qf=0)
        assert v_high > v_low  # 도핑 ↑ → Vth ↑

    def test_산화막_두께_늘리면_vth_증가(self):
        calc = SemiconductorCalculator()
        v_thin = calc.threshold_voltage_nmos(tox_nm=5, na_per_cm3=1e16, phi_ms=-0.5, qf=0)
        v_thick = calc.threshold_voltage_nmos(tox_nm=20, na_per_cm3=1e16, phi_ms=-0.5, qf=0)
        assert v_thick > v_thin  # tox ↑ → Cox ↓ → bulk charge term ↑ → Vth ↑

    def test_음수_도핑_농도는_거부(self):
        calc = SemiconductorCalculator()
        with pytest.raises(ValueError):
            calc.threshold_voltage_nmos(tox_nm=10, na_per_cm3=-1e16, phi_ms=-0.5, qf=0)

    def test_0_또는_음수_tox는_거부(self):
        calc = SemiconductorCalculator()
        with pytest.raises(ValueError):
            calc.threshold_voltage_nmos(tox_nm=0, na_per_cm3=1e16, phi_ms=-0.5, qf=0)


class TestDrainCurrent:
    """Long-channel saturation: Id = (μn·Cox·W/L / 2) · (Vgs - Vth)²"""

    def test_saturation_id_계산(self):
        calc = SemiconductorCalculator()
        # 예시: μn=400 cm²/Vs, Cox=3.45e-7 F/cm² (tox=10nm), W/L=10, Vgs-Vth=1V
        id_a = calc.drain_current_saturation(
            mobility_cm2_vs=400,
            cox_f_per_cm2=3.45e-7,
            w_over_l=10,
            vgs_minus_vth=1.0,
        )
        # 약 6.9e-4 A = 0.69mA 수준
        assert 1e-4 < id_a < 1e-2

    def test_overdrive_2배면_id_4배(self):
        # square-law: Id ∝ (Vov)²
        calc = SemiconductorCalculator()
        id1 = calc.drain_current_saturation(400, 3.45e-7, 10, 0.5)
        id2 = calc.drain_current_saturation(400, 3.45e-7, 10, 1.0)
        assert math.isclose(id2 / id1, 4.0, rel_tol=1e-3)

    def test_w_l_비율_2배면_id_2배(self):
        calc = SemiconductorCalculator()
        id1 = calc.drain_current_saturation(400, 3.45e-7, 5, 1.0)
        id2 = calc.drain_current_saturation(400, 3.45e-7, 10, 1.0)
        assert math.isclose(id2 / id1, 2.0, rel_tol=1e-3)

    def test_negative_overdrive는_id_0_컷오프(self):
        # Vgs < Vth → 컷오프, Id = 0 (표준 long-channel 모델)
        calc = SemiconductorCalculator()
        id_a = calc.drain_current_saturation(400, 3.45e-7, 10, -0.5)
        assert id_a == 0.0


class TestOxideCapacitance:
    """Cox = εox / tox, εox = 3.9·ε0 = 3.45e-13 F/cm"""

    def test_tox_10nm_cox(self):
        calc = SemiconductorCalculator()
        cox = calc.oxide_capacitance_per_area(tox_nm=10)
        # 약 3.45e-7 F/cm²
        assert math.isclose(cox, 3.45e-7, rel_tol=1e-2)

    def test_tox_절반이면_cox_2배(self):
        calc = SemiconductorCalculator()
        c1 = calc.oxide_capacitance_per_area(tox_nm=10)
        c2 = calc.oxide_capacitance_per_area(tox_nm=5)
        assert math.isclose(c2 / c1, 2.0, rel_tol=1e-3)
