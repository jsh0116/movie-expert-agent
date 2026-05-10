"""TDD: 산업 동향 웹 검색 — DuckDuckGo wrapper, 외부 호출 mock."""
from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from semiconductor.infrastructure.tools.web_search import IndustrySearchService


class TestIndustrySearchService:
    @patch("semiconductor.infrastructure.tools.web_search.DuckDuckGoSearchRun")
    def test_검색_쿼리에_반도체_도메인_컨텍스트가_부착된다(self, mock_ddg_cls):
        # given: DDG가 검색 결과 반환
        mock_ddg = MagicMock()
        mock_ddg.run.return_value = "HBM3E latest news..."
        mock_ddg_cls.return_value = mock_ddg

        svc = IndustrySearchService()
        svc.search("HBM 동향")

        # when: search 호출 시 검색어가 반도체 컨텍스트로 enhanced
        actual_query = mock_ddg.run.call_args[0][0]
        assert "HBM 동향" in actual_query
        assert "반도체" in actual_query  # context augmentation

    @patch("semiconductor.infrastructure.tools.web_search.DuckDuckGoSearchRun")
    def test_검색_결과_텍스트로_반환(self, mock_ddg_cls):
        mock_ddg = MagicMock()
        mock_ddg.run.return_value = "TSMC announced N2 process at 2nm node..."
        mock_ddg_cls.return_value = mock_ddg

        svc = IndustrySearchService()
        result = svc.search("TSMC N2")

        assert "TSMC" in result

    @patch("semiconductor.infrastructure.tools.web_search.DuckDuckGoSearchRun")
    def test_검색_실패시_빈문자열_또는_에러메시지_반환(self, mock_ddg_cls):
        # graceful degradation: 검색 실패해도 그래프 흐름 안 깨짐
        mock_ddg = MagicMock()
        mock_ddg.run.side_effect = Exception("network timeout")
        mock_ddg_cls.return_value = mock_ddg

        svc = IndustrySearchService()
        result = svc.search("any")

        assert isinstance(result, str)
        assert "검색" in result or result == ""

    @patch("semiconductor.infrastructure.tools.web_search.DuckDuckGoSearchRun")
    def test_빈_쿼리는_거부(self, mock_ddg_cls):
        svc = IndustrySearchService()
        with pytest.raises(ValueError):
            svc.search("")

    @patch("semiconductor.infrastructure.tools.web_search.DuckDuckGoSearchRun")
    def test_오늘_날짜의_연도가_쿼리에_자동_부착된다(self, mock_ddg_cls):
        # 핵심: stale article 회피. 최근 정보 검색은 반드시 today 기준.
        mock_ddg = MagicMock()
        mock_ddg.run.return_value = "results"
        mock_ddg_cls.return_value = mock_ddg

        svc = IndustrySearchService(today=date(2026, 5, 10))
        svc.search("HBM3E 양산")

        actual_query = mock_ddg.run.call_args[0][0]
        assert "2026" in actual_query

    @patch("semiconductor.infrastructure.tools.web_search.DuckDuckGoSearchRun")
    def test_검색_결과에_기준_날짜가_프리픽스로_표시된다(self, mock_ddg_cls):
        # 사용자가 결과의 시점을 알 수 있도록 헤더에 날짜 노출
        mock_ddg = MagicMock()
        mock_ddg.run.return_value = "raw search output"
        mock_ddg_cls.return_value = mock_ddg

        svc = IndustrySearchService(today=date(2026, 5, 10))
        result = svc.search("EUV")

        assert "2026-05-10" in result
        assert "raw search output" in result
