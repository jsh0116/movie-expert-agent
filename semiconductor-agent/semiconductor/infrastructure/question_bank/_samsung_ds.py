"""Samsung DS technical interview question pool (공정/소자 심화 중심)."""
from semiconductor.domain.entities import Question

QUESTIONS: dict[str, list[Question]] = {
    "소자": [
        Question(
            domain="소자",
            question="MOSFET의 문턱전압(Vth)이 무엇인지 설명하고, 온도가 올라가면 Vth가 어떻게 변하는지 이유와 함께 설명하세요.",
            key_points=[
                "Vth: 채널이 형성되기 시작하는 최소 게이트 전압",
                "온도 상승 → 캐리어 이동도 감소 + 페르미 준위 이동 → Vth 감소",
                "threshold voltage roll-off와 DIBL 연결",
            ],
        ),
        Question(
            domain="소자",
            question="FinFET과 GAA(Gate-All-Around) 트랜지스터의 구조적 차이를 설명하고, GAA가 FinFET보다 스케일링에 유리한 이유를 설명하세요.",
            key_points=[
                "FinFET: 게이트가 핀(fin) 3면 감싸는 구조",
                "GAA: 나노시트/나노와이어 4면 전체를 게이트가 감싸는 구조",
                "GAA의 우수한 전기장 제어 → SCE(Short Channel Effect) 억제",
                "삼성 3nm GAA(MBCFET) 도입",
            ],
        ),
        Question(
            domain="소자",
            question="DRAM 셀의 기본 구조(1T1C)에서 커패시터 용량을 확보하기 위해 사용되는 주요 기법들을 설명하세요.",
            key_points=[
                "1T1C: 액세스 트랜지스터 1개 + 스토리지 커패시터 1개",
                "High-k 유전체(ZrO2, HfO2) 도입으로 EOT 감소",
                "실린더형 3D 커패시터 → 표면적 증가",
                "셀 피치 축소에 따른 종횡비 증가 문제",
            ],
        ),
        Question(
            domain="소자",
            question="NAND 플래시에서 플로팅 게이트(FG)와 CTF(Charge Trap Flash)의 차이점을 설명하고, 3D NAND에서 CTF가 선호되는 이유를 말씀해 주세요.",
            key_points=[
                "FG: 전도성 폴리실리콘에 전하 저장 → 인접 셀 간섭(coupling) 심함",
                "CTF: 질화물 절연층에 전하 포획 → 더 얇은 공정 가능",
                "3D NAND에서 CTF가 수직 스택 구조와 호환성 우수",
                "삼성 V-NAND = CTF 기반",
            ],
        ),
        Question(
            domain="소자",
            question="짧은 채널 효과(SCE) 중 DIBL과 punch-through의 물리적 원인과 FinFET/GAA에서의 억제 메커니즘을 설명하세요.",
            key_points=[
                "DIBL: 드레인 전압이 소스측 에너지 장벽을 낮춤",
                "Punch-through: 소스-드레인 공핍 영역이 만나 채널 제어 불능",
                "FinFET/GAA: 게이트 wrap-around → 전기장 제어 강화 → SCE 억제",
            ],
        ),
    ],
    "공정": [
        Question(
            domain="공정",
            question="CVD(Chemical Vapor Deposition)와 ALD(Atomic Layer Deposition)의 메커니즘 차이를 설명하고, ALD가 고종횡비 구조에 유리한 이유를 말씀해 주세요.",
            key_points=[
                "CVD: 가스 반응물이 동시에 표면에 도달 → 컨포말성 제한",
                "ALD: 전구체 A 포화 흡착 → 퍼지 → 전구체 B → 한 원자층씩 성장(자기제한)",
                "ALD의 self-limiting 반응 → 고종횡비에서도 균일한 컨포말 증착",
            ],
        ),
        Question(
            domain="공정",
            question="포토리소그래피에서 레일리 기준(Rayleigh criterion)을 설명하고, EUV(13.5nm)가 ArF 액침(193nm) 대비 해상도를 향상시키는 원리를 말씀해 주세요.",
            key_points=[
                "Rayleigh: R = k1 × λ / NA",
                "EUV: λ = 13.5nm → 파장 단축 → 해상도 향상",
                "EUV: 반사 광학계 사용 (투과 불가)",
                "멀티패터닝 단계 감소",
            ],
        ),
        Question(
            domain="공정",
            question="CMP(Chemical Mechanical Planarization) 공정의 역할과 원리, 그리고 적용되는 대표적인 단계 두 가지를 설명하세요.",
            key_points=[
                "CMP: 화학적 식각 + 기계적 연마로 표면 평탄화",
                "슬러리(연마재 + 산화제) + 패드",
                "STI 평탄화, Cu damascene 후 평탄화",
                "dishing, erosion 문제",
            ],
        ),
        Question(
            domain="공정",
            question="건식 식각(Dry Etch)에서 이방성 식각과 등방성 식각의 차이를 설명하고, DRAM 트렌치 커패시터 식각 시 이방성이 필요한 이유를 설명하세요.",
            key_points=[
                "이방성: 수직 방향 선택적 식각 (플라즈마 이온 bombard)",
                "등방성: 모든 방향 균일 식각",
                "트렌치 커패시터: 깊은 수직 홀 → 이방성 필수",
                "RIE 메커니즘",
            ],
        ),
        Question(
            domain="공정",
            question="PVD(Physical Vapor Deposition)와 CVD의 차이를 설명하고, 각각이 주로 사용되는 반도체 공정 응용 분야를 말씀해 주세요.",
            key_points=[
                "PVD: 물리적 방법(스퍼터링) → line-of-sight",
                "CVD: 화학 반응 → 컨포말성 우수",
                "PVD: 금속 배선(Al, Cu 시드층), TiN 배리어",
                "CVD: 산화막, 질화막, 폴리실리콘",
            ],
        ),
    ],
    "회로": [
        Question(
            domain="회로",
            question="DRAM에서 센스앰프(Sense Amplifier)의 역할과 동작 원리를 설명하고, 교차결합 인버터 구조가 사용되는 이유를 말씀해 주세요.",
            key_points=[
                "센스앰프: 비트라인의 미세한 전압차(ΔV) 감지·증폭",
                "교차결합 인버터: 양의 피드백으로 ΔV → 풀스윙",
                "ΔV: 셀 커패시터 전하 공유 후 비트라인 전압 변화",
                "폴디드 비트라인 구조",
            ],
        ),
        Question(
            domain="회로",
            question="차지 펌프(Charge Pump)의 동작 원리를 설명하고, NAND 플래시 프로그램/소거에 왜 필요한지 말씀해 주세요.",
            key_points=[
                "차지 펌프: 클락 + 커패시터로 전압 배수 상승",
                "Dickson charge pump 구조",
                "NAND 프로그램: 터널 산화막 통과 위해 15~20V 필요",
                "소거: Fowler-Nordheim 터널링",
            ],
        ),
        Question(
            domain="회로",
            question="메모리 컨트롤러에서 ECC(SECDED)가 필요한 이유와 동작 원리를 설명하세요.",
            key_points=[
                "ECC: 소프트 에러(방사선), 공정 결함으로 인한 비트 오류 수정",
                "SECDED: 해밍 코드 기반, 1비트 수정 + 2비트 감지",
                "64비트 데이터에 8비트 패리티",
                "HBM/DDR5 인라인 ECC",
            ],
        ),
    ],
    "트렌드": [
        Question(
            domain="트렌드",
            question="3D NAND에서 레이어 수를 늘려가는 이유와 발생하는 주요 기술적 과제를 두 가지 이상 설명하세요.",
            key_points=[
                "평면 스케일링 한계 → 수직 적층으로 집적도 증가",
                "과제: 깊은 채널홀 식각 정밀도",
                "층간 전기적 특성 균일성 확보",
                "워드라인 저항 증가 → RC 지연",
            ],
        ),
        Question(
            domain="트렌드",
            question="EUV 리소그래피 도입이 삼성 반도체 공정에서 가지는 기술적 의미와 주요 과제를 설명하세요.",
            key_points=[
                "EUV: 멀티패터닝 단계 축소 → 수율 개선",
                "과제: 광원 출력 부족 → 스루풋 제한",
                "포토레지스트 감도 및 LER 문제",
                "반사 마스크 결함 검사 어려움",
            ],
        ),
        Question(
            domain="트렌드",
            question="CoWoS(Chip on Wafer on Substrate)와 HBM의 관계를 설명하고, AI 가속기에서 이 패키징 기술이 필수적인 이유를 설명하세요.",
            key_points=[
                "HBM: DRAM 다이를 TSV로 수직 적층 → 고대역폭",
                "CoWoS: HBM + GPU/NPU를 인터포저 위에 결합하는 2.5D 패키징",
                "AI 가속기 병목: 메모리 대역폭 (bandwidth wall)",
                "HBM3E: 1.2TB/s, AI 훈련 필수",
            ],
        ),
        Question(
            domain="트렌드",
            question="CXL(Compute Express Link)의 개념과 차세대 데이터센터 메모리 아키텍처에서의 의미를 설명하세요.",
            key_points=[
                "CXL: PCIe 기반 고속 캐시 코히어런트 인터커넥트",
                "메모리 풀링: 여러 호스트가 메모리 공유",
                "메모리 용량 확장 + TCO 절감",
                "삼성 CXL DRAM 모듈 개발",
            ],
        ),
    ],
}
