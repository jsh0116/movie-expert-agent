from semiconductor.domain.entities import DiagnosticResult, EvaluationResult
from semiconductor.domain.ports import IDiagnosticLLM

_ALL_DOMAINS = ("소자", "공정", "회로", "트렌드")


class DiagnoseSessionUseCase:
    def __init__(self, diagnostic_llm: IDiagnosticLLM) -> None:
        self._llm = diagnostic_llm

    def execute(self, evaluations: list[EvaluationResult]) -> DiagnosticResult:
        if not evaluations:
            raise ValueError("평가 데이터가 없습니다. 먼저 모의면접을 진행해주세요.")

        result = self._llm.analyze(evaluations)

        # Fill missing domains with 0
        for domain in _ALL_DOMAINS:
            result.domain_scores.setdefault(domain, 0)

        return result
