"""TDD: Gemini vision analyzer — 외부 API mock."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from semiconductor.infrastructure.tools.vision import GeminiVisionAnalyzer, _encode_image


# ── _encode_image ────────────────────────────────────────────────


class TestEncodeImage:
    def test_png_파일_정상_인코딩(self, tmp_path: Path):
        f = tmp_path / "test.png"
        f.write_bytes(b"\x89PNG\r\n\x1a\nfake")
        b64, mime = _encode_image(str(f))
        assert mime == "image/png"
        assert isinstance(b64, str) and len(b64) > 0

    def test_jpg_jpeg_둘다_인식(self, tmp_path: Path):
        for ext in ("jpg", "jpeg"):
            f = tmp_path / f"test.{ext}"
            f.write_bytes(b"\xff\xd8\xff\xe0fake")
            _, mime = _encode_image(str(f))
            assert mime == "image/jpeg"

    def test_webp_인식(self, tmp_path: Path):
        f = tmp_path / "test.webp"
        f.write_bytes(b"RIFFfake")
        _, mime = _encode_image(str(f))
        assert mime == "image/webp"

    def test_pdf_인식(self, tmp_path: Path):
        f = tmp_path / "doc.pdf"
        f.write_bytes(b"%PDF-1.4 fake")
        _, mime = _encode_image(str(f))
        assert mime == "application/pdf"

    def test_파일_없으면_FileNotFoundError(self):
        with pytest.raises(FileNotFoundError):
            _encode_image("/nonexistent/x.png")

    def test_지원하지_않는_확장자_거부(self, tmp_path: Path):
        f = tmp_path / "test.bmp"
        f.write_bytes(b"BM fake")
        with pytest.raises(ValueError, match="지원하지 않는 파일 형식"):
            _encode_image(str(f))


# ── GeminiVisionAnalyzer ─────────────────────────────────────────


class TestGeminiVisionAnalyzer:
    @patch("semiconductor.infrastructure.tools.vision.init_chat_model")
    def test_생성시_init_chat_model_호출_default_gemini(self, mock_init):
        mock_init.return_value = MagicMock()
        GeminiVisionAnalyzer()
        spec = mock_init.call_args.args[0]
        assert spec == "google_genai:gemini-2.5-pro"

    @patch("semiconductor.infrastructure.tools.vision.init_chat_model")
    def test_명시_model_spec으로_재정의_가능(self, mock_init):
        # 명시 인자가 env var 보다 명확. flash 등 가성비 모델 선택 가능.
        mock_init.return_value = MagicMock()
        GeminiVisionAnalyzer(model_spec="google_genai:gemini-2.5-flash")
        spec = mock_init.call_args.args[0]
        assert spec == "google_genai:gemini-2.5-flash"

    @patch("semiconductor.infrastructure.tools.vision.init_chat_model")
    def test_analyze_이미지를_base64로_변환해_invoke에_전달(
        self, mock_init, tmp_path: Path
    ):
        llm = MagicMock()
        response = MagicMock()
        response.content = "회로 분석 결과"
        llm.invoke.return_value = response
        mock_init.return_value = llm

        f = tmp_path / "circuit.png"
        f.write_bytes(b"\x89PNG\r\n\x1a\nfake")

        analyzer = GeminiVisionAnalyzer()
        result = analyzer.analyze(str(f), "이 회로를 분석해줘")

        assert result == "회로 분석 결과"
        # invoke에 전달된 메시지에 image_url이 포함되어야 함
        call_args = llm.invoke.call_args
        msgs = call_args.args[0]
        content = msgs[0].content
        assert any(
            block.get("type") == "image_url" for block in content if isinstance(block, dict)
        )

    @patch("semiconductor.infrastructure.tools.vision.init_chat_model")
    def test_파일_없으면_안내_메시지(self, mock_init):
        mock_init.return_value = MagicMock()
        analyzer = GeminiVisionAnalyzer()
        result = analyzer.analyze("/nonexistent.png", "분석")
        assert "❌" in result
        assert "찾을 수 없습니다" in result

    @patch("semiconductor.infrastructure.tools.vision.init_chat_model")
    def test_LLM_실패시_graceful_degradation(self, mock_init, tmp_path: Path):
        llm = MagicMock()
        llm.invoke.side_effect = Exception("API timeout")
        mock_init.return_value = llm

        f = tmp_path / "x.png"
        f.write_bytes(b"\x89PNGfake")

        analyzer = GeminiVisionAnalyzer()
        result = analyzer.analyze(str(f), "분석")
        assert "⚠️" in result
        assert "Gemini" in result
