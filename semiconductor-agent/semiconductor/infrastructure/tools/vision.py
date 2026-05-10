"""Gemini 멀티모달 비전 분석 — 회로도·밴드 다이어그램·도식 입력.

Gemini의 멀티모달 + 1M context window를 활용해 텍스트 LLM이 못 보는
시각적 정보(회로도, 밴드 다이어그램, 레이아웃)를 텍스트로 변환.

사용처:
  - 사용자가 회로도 사진 업로드 → 분석 텍스트 → mock_evaluate에 전달
  - 강의 슬라이드 PDF → 핵심 개념 추출
  - 밴드 다이어그램 → MOSFET 동작 설명
"""
from __future__ import annotations

import base64
import os
from pathlib import Path

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage


_DEFAULT_VISION_MODEL = os.getenv("LLM_MODEL_VISION", "google_genai:gemini-2.5-pro")


def _encode_image(image_path: str) -> tuple[str, str]:
    """이미지 파일 읽어 base64 + mime_type 반환."""
    p = Path(image_path)
    if not p.exists():
        raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {image_path}")
    suffix = p.suffix.lower().lstrip(".")
    if suffix in ("jpg", "jpeg"):
        mime = "image/jpeg"
    elif suffix == "png":
        mime = "image/png"
    elif suffix == "webp":
        mime = "image/webp"
    elif suffix == "pdf":
        mime = "application/pdf"
    else:
        raise ValueError(f"지원하지 않는 파일 형식: {suffix}")
    data = p.read_bytes()
    return base64.standard_b64encode(data).decode("utf-8"), mime


class GeminiVisionAnalyzer:
    """반도체 도식 분석 전용 Gemini 래퍼."""

    def __init__(self, model_spec: str | None = None) -> None:
        self._model_spec = model_spec or _DEFAULT_VISION_MODEL
        self._llm = init_chat_model(self._model_spec, temperature=0.2)

    def analyze(self, image_path: str, prompt: str) -> str:
        """이미지를 전문가 관점으로 분석.

        Args:
            image_path: 로컬 이미지 또는 PDF 파일 경로
            prompt: 분석 요청 텍스트 (예: "이 회로도를 설명하세요")

        Returns:
            Gemini 분석 결과 텍스트.
            실패 시 사용자 안내 메시지 (graceful degradation).
        """
        try:
            b64, mime = _encode_image(image_path)
        except (FileNotFoundError, ValueError) as e:
            return f"❌ 이미지 처리 실패: {e}"

        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime};base64,{b64}"},
                },
            ]
        )
        try:
            response = self._llm.invoke([message])
            return response.content if hasattr(response, "content") else str(response)
        except Exception as exc:
            return f"⚠️ Gemini 분석 일시 실패 ({type(exc).__name__})."
