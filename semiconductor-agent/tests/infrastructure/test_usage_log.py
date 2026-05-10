"""TDD: 사용량 로깅."""
from __future__ import annotations

from pathlib import Path

from semiconductor.infrastructure.observability.usage_log import (
    _estimate_cost,
    log_usage,
    read_usage,
)


class TestEstimateCost:
    def test_gpt_4o_input_output_가격(self):
        # openai:gpt-4o = (2.5, 10.0) per 1M
        cost = _estimate_cost("openai:gpt-4o", 1000, 500)
        assert abs(cost - 0.0075) < 1e-9

    def test_gpt_4o_mini_저렴(self):
        cost_4o = _estimate_cost("openai:gpt-4o", 1000, 500)
        cost_mini = _estimate_cost("openai:gpt-4o-mini", 1000, 500)
        assert cost_mini < cost_4o / 10

    def test_unknown_model_은_0(self):
        assert _estimate_cost("unknown:model", 1000, 500) == 0.0


class TestLogUsage:
    def test_jsonl에_한_줄_append(self, tmp_path: Path):
        log_path = str(tmp_path / "u.jsonl")
        record = log_usage(
            thread_id="hans", node="judge", model="openai:gpt-4o",
            tokens_in=1500, tokens_out=400, log_path=log_path,
        )
        assert record["thread_id"] == "hans"
        assert record["cost_usd"] > 0
        data = read_usage(log_path)
        assert len(data) == 1

    def test_연속_호출_누적(self, tmp_path: Path):
        log_path = str(tmp_path / "u.jsonl")
        for _ in range(3):
            log_usage(thread_id="hans", node="judge", model="openai:gpt-4o",
                      tokens_in=1000, tokens_out=200, log_path=log_path)
        assert len(read_usage(log_path)) == 3

    def test_extra_메타_포함(self, tmp_path: Path):
        log_path = str(tmp_path / "u.jsonl")
        log_usage(thread_id="hans", node="judge", model="openai:gpt-4o",
                  tokens_in=100, tokens_out=50,
                  extra={"cache_hit": True, "latency_ms": 1234},
                  log_path=log_path)
        data = read_usage(log_path)
        assert data[0]["extra"]["cache_hit"] is True

    def test_읽기_없으면_빈_리스트(self, tmp_path: Path):
        assert read_usage(str(tmp_path / "nonexistent.jsonl")) == []

    def test_USAGE_LOG_PATH_env로_경로_재정의(self, tmp_path: Path, monkeypatch):
        custom = tmp_path / "custom.jsonl"
        monkeypatch.setenv("USAGE_LOG_PATH", str(custom))
        log_usage(thread_id="hans", node="x", model="openai:gpt-4o-mini",
                  tokens_in=10, tokens_out=5)
        assert custom.exists()
