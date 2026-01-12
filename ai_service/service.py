# ai_service/service.py
import tempfile
import time
from pathlib import Path
from typing import Dict
from PIL import Image

from .paddle_service import ocr_image
from .rules import run_all_field_extractors
from .schemas import OrderFormSchema, FieldValue, OCRToken

# LayoutLM imports
from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification

SUPPORTED_IMAGE_TYPES = {".png", ".jpg", ".jpeg", ".bmp", ".tiff"}

# LayoutLMv3 model with apply_ocr=False
processor = LayoutLMv3Processor.from_pretrained("D:/layoutlmv3", apply_ocr=False)
layoutlm_model = LayoutLMv3ForTokenClassification.from_pretrained("D:/layoutlmv3")

def normalize_bbox(bbox, width, height):
    """Normalize bbox coordinates to 0-1000 scale for LayoutLM"""
    return [
        int(1000 * bbox[0] / width),
        int(1000 * bbox[1] / height),
        int(1000 * bbox[2] / width),
        int(1000 * bbox[3] / height),
    ]

def extract_with_layoutlm(image_path: str, tokens: list[OCRToken]) -> Dict[str, FieldValue]:
    """
    Use LayoutLMv3 to extract fields from complex layouts.
    """
    image = Image.open(image_path).convert("RGB")
    width, height = image.size
    
    words = [t.text for t in tokens]
    
    # Convert 4-point polygon bbox to [x_min, y_min, x_max, y_max]
    boxes = []
    for t in tokens:
        bbox = t.bbox
        x_coords = [p[0] for p in bbox]
        y_coords = [p[1] for p in bbox]
        box = [min(x_coords), min(y_coords), max(x_coords), max(y_coords)]
        normalized_box = normalize_bbox(box, width, height)
        boxes.append(normalized_box)
    
    # Encode without OCR
    encoding = processor(
        image,
        text=words,
        boxes=boxes,
        return_tensors="pt",
        padding="max_length",
        truncation=True
    )

    # NOTE: This model is NOT trained for your specific fields
    # It will give random predictions. You need to fine-tune it on your data.
    outputs = layoutlm_model(**encoding)
    predictions = outputs.logits.argmax(-1).squeeze(0).tolist()

    # These labels are placeholders - the pretrained model doesn't know these
    label_map = {
        1: "lot_no",
        2: "block",
        3: "address",
        4: "model_selected",
        5: "elevation",
        6: "garage_swing",
        7: "external_structure",
        8: "optional_notes",
    }

    fields: Dict[str, FieldValue] = {k: FieldValue() for k in label_map.values()}

    for i, (token, pred) in enumerate(zip(tokens, predictions[:len(tokens)])):
        if pred in label_map:
            key = label_map[pred]
            if fields[key].value:
                fields[key].value += " " + token.text
            else:
                fields[key].value = token.text
            fields[key].confidence = 0.5  # Low confidence - model not trained
            fields[key].source = "layoutlm"

    return fields


def extract_order_form_from_image(image_path: str) -> OrderFormSchema:
    start = time.perf_counter()

    tokens = ocr_image(image_path)
    if not tokens:
        raise ValueError("OCR returned no tokens.")

    # Use rule-based extraction (your current working approach)
    rule_fields = run_all_field_extractors(tokens)

    # Try LayoutLM (but it won't work well without training)
    try:
        layout_fields = extract_with_layoutlm(image_path, tokens)
    except Exception as e:
        print(f"LayoutLM failed: {e}")
        layout_fields = {}

    # Prefer rule-based for now since LayoutLM isn't trained
    merged = {}
    for k in rule_fields.keys():
        # Use rule fields first, fallback to layout
        field = rule_fields[k] if rule_fields[k].value else layout_fields.get(k, FieldValue())
        merged[k] = field

    validated = {k: (v.value.strip() if v.value else None) for k, v in merged.items()}

    processing_time = int((time.perf_counter() - start) * 1000)
    
    # Create schema and add processing_ms separately if needed
    schema = OrderFormSchema(**validated)
    if hasattr(schema, 'processing_ms'):
        schema.processing_ms = processing_time
    
    return schema


def extract_order_form(file_path: str) -> OrderFormSchema:
    suffix = Path(file_path).suffix.lower()
    if suffix in SUPPORTED_IMAGE_TYPES:
        return extract_order_form_from_image(file_path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")