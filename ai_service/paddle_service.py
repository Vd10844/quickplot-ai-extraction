from functools import lru_cache
from typing import List, Dict, Any
from paddleocr import PaddleOCR
import numpy as np

@lru_cache(maxsize=1)
def get_ocr() -> PaddleOCR:
    return PaddleOCR(
        use_angle_cls=True,
        lang="en",
    )

def _to_list_bbox(bb: Any):
    # Convert numpy arrays or other sequences to list of [x, y]
    if bb is None:
        return None
    arr = np.array(bb, dtype=float)
    # Expect shape (4, 2) or similar
    return arr.tolist()

def _safe_get_boxes(page: Dict[str, Any]):
    if "rec_boxes" in page and page["rec_boxes"] is not None:
        return page["rec_boxes"]
    if "rec_polys" in page and page["rec_polys"] is not None:
        return page["rec_polys"]
    return []

def ocr_image(image_path: str) -> List[Dict[str, Any]]:
    ocr = get_ocr()
    try:
        result = ocr.ocr(image_path)
    except Exception as e:
        return [{"text": f"ERROR: {e}", "score": 0.0, "bbox": None}]

    if not result:
        return []

    page = result[0]

    if isinstance(page, dict):
        texts = page.get("rec_texts") or []
        scores = page.get("rec_scores") or []
        boxes = _safe_get_boxes(page)
        out: List[Dict[str, Any]] = []
        for txt, sc, bb in zip(texts, scores, boxes):
            out.append(
                {
                    "text": txt,
                    "score": float(sc),
                    "bbox": _to_list_bbox(bb),
                }
            )
        return out

    out: List[Dict[str, Any]] = []
    for item in page:
        try:
            box, rec = item
            if isinstance(rec, (list, tuple)) and len(rec) >= 2:
                text, score = rec[0], rec[1]
            else:
                text, score = rec, 0.0
            out.append(
                {
                    "text": text,
                    "score": float(score),
                    "bbox": _to_list_bbox(box),
                }
            )
        except Exception as e:
            out.append(
                {
                    "text": f"PARSE_ERROR: {e}",
                    "score": 0.0,
                    "bbox": None,
                }
            )
    return out
