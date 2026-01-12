# ai_service/ocr_adaptor.py
from typing import List
from .schemas import OCRToken


class OCRAdapter:
    @staticmethod
    def normalize(raw_tokens: List[dict]) -> List[OCRToken]:
        """
        Normalize raw OCR dicts into OCRToken objects.
        Ensures bbox is always [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
        """
        tokens: List[OCRToken] = []

        for t in raw_tokens:
            try:
                text = t.get("text", "").strip()
                if not text:
                    continue

                bbox = t.get("bbox") or [[0, 0]] * 4
                # Ensure bbox is list of 4 points
                if len(bbox) != 4:
                    bbox = [[0, 0]] * 4

                confidence = float(t.get("score") or 0.0)

                token = OCRToken(text=text, bbox=bbox, confidence=confidence)
                tokens.append(token)
            except Exception:
                # Skip malformed token
                continue

        return tokens
