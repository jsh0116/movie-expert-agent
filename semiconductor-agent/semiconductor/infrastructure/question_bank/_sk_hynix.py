"""SK Hynix technical interview question pool (메모리/HBM/패키징 중심)."""
from semiconductor.domain.entities import Question

QUESTIONS: dict[str, list[Question]] = {
    "소자": [
        Question(
            domain="소자",
            question="DRAM 셀에서 리프레시(Refresh)가 필요한 물리적 이유와 리프레시 주기(tREF)와 온도의 관계를 설명하세요.",
            key_points=[
                "커패시터 전하: 접합 누설 전류(junction leakage)로 자연 방전",
                "tREF = 64ms at 85°C",
                "온도 상승 → 누설 전류 증가 → tREF 단축 필요",
                "리프레시 오버헤드: 메모리 접근 불가 시간",
            ],
        ),
        Question(
            domain="소자",
            question="TSV(Through Silicon Via)의 구조와 제조 방법을 설명하고, SK하이닉스 HBM에서 TSV의 역할을 설명하세요.",
            key_points=[
                "TSV: 실리콘 다이를 수직으로 관통하는 전도성 비아",
                "Via-first / Via-middle / Via-last 공정",
                "HBM: TSV로 DRAM 다이 다단 적층 → 수직 연결",
                "TSV 밀도: HBM 메모리 대역폭 결정",
                "KGD + 웨이퍼 씨닝 필요",
            ],
        ),
        Question(
            domain="소자",
            question="HBM 스택에서 Base Die(Logic Die)와 Core Die의 역할 차이와 Base Die가 필요한 이유를 설명하세요.",
            key_points=[
                "Core Die: 실제 DRAM 셀 어레이 + 주변 회로",
                "Base Die: I/O 버퍼, 전력 관리, TSV 인터페이스",
                "Base Die: 호스트와 고속 인터페이스 + 다이 간 신호 드라이빙",
                "HBM3E: Base Die에 ECC, 온-다이 터미네이션 통합 추세",
            ],
        ),
        Question(
            domain="소자",
            question="LPDDR5가 이전 세대 대비 전력 소비를 줄이기 위해 사용하는 주요 기법들을 설명하세요.",
            key_points=[
                "전압 스케일링: VDD 감소 (1.05V)",
                "PASR: 사용 중인 영역만 리프레시",
                "Deep Power Down 모드",
                "데이터 버스 인버전(DBI): 스위칭 활동 감소",
            ],
        ),
        Question(
            domain="소자",
            question="TDDB(Time-Dependent Dielectric Breakdown)란 무엇이고, DRAM 게이트 산화막 신뢰성에 어떤 영향을 미치는지 설명하세요.",
            key_points=[
                "TDDB: 전계 인가 시 시간 경과에 따른 산화막 절연 파괴",
                "E-model / 1/E-model 수명 예측",
                "DRAM 액세스 트랜지스터 Vth 이동 및 고장 원인",
                "박막화 추세와 TDDB 가속 관계",
            ],
        ),
    ],
    "공정": [
        Question(
            domain="공정",
            question="HBM 제조에서 하이브리드 본딩(Hybrid Bonding)이 기존 마이크로범프 방식 대비 가지는 장점을 설명하세요.",
            key_points=[
                "하이브리드 본딩: Cu-Cu 직접 금속 접합 (범프 없음)",
                "마이크로범프 대비 피치 미세화 가능 (< 10μm)",
                "기생 저항·인덕턴스 감소 → 신호 품질 향상",
                "다이 높이 감소 → 적층 두께 최소화",
            ],
        ),
        Question(
            domain="공정",
            question="DRAM 공정에서 Self-Aligned Contact(SAC) 기술이 필요한 이유와 핵심 원리를 설명하세요.",
            key_points=[
                "SAC: 리소그래피 정렬 오차 허용 → 미세 피치에서 컨택 형성",
                "질화막(SiN) 스페이서: 워드라인 보호 + 셀프얼라인",
                "오버랩 마진 확보",
                "고종횡비 컨택 홀 식각 + ALD 라이너",
            ],
        ),
        Question(
            domain="공정",
            question="웨이퍼 본딩의 종류(다이렉트/접착제)를 비교하고, HBM 제조 시 웨이퍼 씨닝이 중요한 이유를 설명하세요.",
            key_points=[
                "다이렉트 본딩: 공유결합 → 고강도, 고열전도",
                "접착제 본딩: 폴리머 → 낮은 공정 온도",
                "HBM 씨닝: 두께 50μm 이하 → 총 스택 높이 제한",
                "TSV 노출을 위한 백사이드 연마",
            ],
        ),
        Question(
            domain="공정",
            question="DRAM 커패시터 공정에서 High-k 유전체(ZrO2 계열)를 ALD로 증착하는 이유를 연결하여 설명하세요.",
            key_points=[
                "SiO2 한계: 두께 축소 시 직접 터널링 누설 전류 급증",
                "High-k(ZrO2): 더 두꺼운 물리적 두께에서도 높은 커패시턴스",
                "ALD: 고종횡비 실린더 커패시터 내부 균일 증착 필수",
                "EOT 감소 → 커패시턴스 향상",
            ],
        ),
    ],
    "회로": [
        Question(
            domain="회로",
            question="HBM 인터페이스에서 넓은 버스 폭(1024-bit+)이 메모리 대역폭에 어떻게 기여하는지 DDR 인터페이스(64-bit)와 비교하여 설명하세요.",
            key_points=[
                "대역폭 = 버스 폭 × 데이터 속도",
                "HBM3E: 1024-bit × 약 9.6Gbps/pin ≈ 1.2TB/s",
                "DDR5: 64-bit × 8.4Gbps ≈ 67GB/s",
                "HBM의 낮은 동작 주파수 → 전력 효율 우수",
            ],
        ),
        Question(
            domain="회로",
            question="온-다이 터미네이션(ODT)이 고속 메모리 인터페이스에서 왜 필요한지 임피던스 정합 관점에서 설명하세요.",
            key_points=[
                "고속 신호: 임피던스 불연속 → 반사(reflection) 발생",
                "ODT: 다이 내부에서 종단 저항 제공 → 반사 억제",
                "전력 소비 vs 신호 무결성 트레이드오프",
                "HBM: 짧은 TSV 경로 → ODT 설계 최적화",
            ],
        ),
        Question(
            domain="회로",
            question="DRAM 리프레시 동작 중 Refresh Collision이란 무엇이고, 이를 처리하기 위한 회로적 방법을 설명하세요.",
            key_points=[
                "Refresh Collision: 호스트 접근과 리프레시 동작이 동시에 발생",
                "해결책 1: tRFC 동안 접근 지연",
                "해결책 2: PASR로 충돌 최소화",
                "LPDDR5: DSM으로 리프레시 오버헤드 감소",
            ],
        ),
    ],
    "트렌드": [
        Question(
            domain="트렌드",
            question="HBM 세대별 발전(HBM1 → HBM3E)을 대역폭과 적층 수 관점에서 설명하고, AI 가속기 시장에서 HBM 수요가 급증하는 이유를 말씀해 주세요.",
            key_points=[
                "HBM1: 128GB/s, 4-hi / HBM2: 256GB/s, 8-hi",
                "HBM3E: 1.2TB/s, 12-hi",
                "AI 훈련: 파라미터 이동 → 메모리 대역폭이 병목",
                "LLM 규모 증가 → HBM 탑재량 증가",
                "SK하이닉스 HBM3E 엔비디아 공급",
            ],
        ),
        Question(
            domain="트렌드",
            question="PIM(Processing-In-Memory) 기술의 개념과 SK하이닉스 AiMX 같은 PIM DRAM이 AI 추론에서 가지는 장점을 설명하세요.",
            key_points=[
                "PIM: 메모리 내부에 연산 유닛 내장",
                "데이터 이동 최소화 → 메모리 대역폭 병목 해소",
                "AiMX: HBM2E 기반 + 연산 유닛 → 대규모 행렬-벡터 연산",
                "Roofline model: memory-bound 해소",
            ],
        ),
        Question(
            domain="트렌드",
            question="DDR5와 LPDDR5X의 차이를 주요 사용 환경과 전력/성능 관점에서 비교하고, 각각의 주요 응용 분야를 설명하세요.",
            key_points=[
                "DDR5: 데스크탑/서버 → 고성능, 높은 전력 허용",
                "LPDDR5X: 모바일/엣지 → 저전력, 낮은 전압(1.05V)",
                "모바일 AI 온디바이스 추론: LPDDR5X 핵심 역할",
            ],
        ),
        Question(
            domain="트렌드",
            question="CXL(Compute Express Link)의 개념과 SK하이닉스가 CXL 메모리 모듈을 개발하는 전략적 이유를 설명하세요.",
            key_points=[
                "CXL: CPU-메모리 간 캐시 코히어런트 인터커넥트 (PCIe 기반)",
                "메모리 풀링: 여러 호스트가 메모리 공유",
                "데이터센터 TCO 절감",
                "SK하이닉스: CXL 2.0 DRAM 모듈 → 서버 메모리 시장 확대",
            ],
        ),
    ],
}
