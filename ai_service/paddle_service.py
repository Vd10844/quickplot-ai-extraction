# ai_service/paddle_service.py
from functools import lru_cache
from typing import List, Dict, Any
import numpy as np
from paddleocr import PaddleOCR

from .schemas import OCRToken


@lru_cache(maxsize=1)
def get_ocr() -> PaddleOCR:
    return PaddleOCR(use_angle_cls=True, lang="en")


def _to_list_bbox(bb: Any):
    if bb is None:
        return None
    return np.array(bb, dtype=int).tolist()


def ocr_image(image_path: str) -> List[OCRToken]:
    print(f"DEBUG paddle_service: Starting OCR for {image_path}")
    ocr = get_ocr()

    try:
        result = ocr.ocr(image_path)
        print(f"DEBUG paddle_service: OCR result type: {type(result)}")
    except Exception as e:
        raise RuntimeError(f"OCR failed: {e}") from e

    if not result:
        return []

    page = result[0]
    print(f"DEBUG paddle_service: Page type: {type(page)}")
    
    tokens: List[OCRToken] = []
    
    # OCRResult is a dict with keys: dt_polys, rec_texts, rec_scores
    if 'dt_polys' in page and 'rec_texts' in page and 'rec_scores' in page:
        dt_polys = page['dt_polys']
        rec_texts = page['rec_texts']
        rec_scores = page['rec_scores']
        
        print(f"DEBUG paddle_service: Found {len(rec_texts)} text items")
        
        for bbox, text, score in zip(dt_polys, rec_texts, rec_scores):
            print(f"DEBUG paddle_service: text={text}, score={score}")
            tokens.append(
                OCRToken(
                    text=text,
                    confidence=float(score),
                    bbox=_to_list_bbox(bbox),
                )
            )
    else:
        print(f"DEBUG paddle_service: Missing expected keys in OCRResult")
        print(f"DEBUG paddle_service: Available keys: {list(page.keys())}")

    print(f"DEBUG paddle_service: Returning {len(tokens)} tokens")
    return tokens