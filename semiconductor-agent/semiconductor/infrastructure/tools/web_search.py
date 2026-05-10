"""반도체 산업 동향 웹 검색 — DuckDuckGo 래퍼.

LLM 2024 cutoff 이후 (HBM3E 양산, TSMC N2, GAA 양산 시점 등) 최신 정보를 fetch.
교수의 "2~3년 lag" 약점 직접 보완.

핵심: 모든 쿼리에 **오늘 날짜의 연도**를 자동 주입해 검색 엔진이 최신 결과를
랭킹 상단에 올리도록 한다. "최근 HBM3E"는 그 자체로 모호하므로 "2026 HBM3E"
같이 명시해야 stale article을 피할 수 있다.
"""
from __future__ import annotations

from datetime import date

from langchain_community.tools import DuckDuckGoSearchRun


class IndustrySearchService:
    """반도체 산업 동향 검색. 쿼리에 도메인 + 현재 연도 자동 부착."""

    def __init__(self, today: date | None = None) -> None:
        self._ddg = DuckDuckGoSearchRun()
        # 테스트에서 today 주입 가능. 기본은 시스템 시간.
        self._today_provider = (lambda: today) if today else date.today

    def search(self, query: str) -> str:
        """반도체 + 현재 연도 컨텍스트 부착된 검색 결과 텍스트.

        실패 시 안내 메시지 반환 (graceful degradation).
        """
        if not query or not query.strip():
            raise ValueError("검색어가 비어있을 수 없습니다.")

        today = self._today_provider()
        # 연도 명시 → DuckDuckGo가 최신 article 랭킹 ↑
        enhanced = f"반도체 산업 {query.strip()} {today.year}"

        try:
            raw = self._ddg.run(enhanced)
            return f"[검색 기준 {today.isoformat()}]\n{raw}"
        except Exception as exc:
            return f"⚠️ 검색을 일시적으로 사용할 수 없습니다 ({type(exc).__name__})."
