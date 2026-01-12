# ai_service/rules.py
"""
Field extraction rules and strategies.
Converts OCR tokens into extracted field values.
"""
from typing import Dict, Any, List
from .schemas import FieldValue
from .validator import (
    pick_best_lot,
    pick_best_block,
    pick_best_address,
    pick_best_garage,
    pick_best_model,
    pick_best_elevation,
    pick_best_notes,
)


def group_into_lines(ocr_tokens: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Group OCR tokens into lines based on vertical position (y-coordinate).
    
    Args:
        ocr_tokens: List of OCR tokens from paddle_service.ocr_image
    
    Returns:
        List of line dictionaries, each containing grouped tokens
    """
    if not ocr_tokens:
        return []
    
    # Sort by y position
    sorted_tokens = sorted(ocr_tokens, key=lambda t: t.get("bbox", [[0, 0]])[0][1])
    
    lines = []
    current_line = []
    last_y = None
    threshold = 10  # pixels; tokens within this distance belong to same line
    
    for token in sorted_tokens:
        if not token.get("bbox"):
            continue
        
        y = token["bbox"][0][1]  # top-left y of bounding box
        
        if last_y is None or abs(y - last_y) < threshold:
            current_line.append(token)
        else:
            if current_line:
                lines.append({
                    "tokens": current_line,
                    "text": " ".join(t.get("text", "") for t in current_line)
                })
            current_line = [token]
        
        last_y = y
    
    if current_line:
        lines.append({
            "tokens": current_line,
            "text": " ".join(t.get("text", "") for t in current_line)
        })
    
    return lines


def _find_lines_with_keywords(lines: List[Dict], keywords: List[str]) -> List[Dict]:
    """Find all lines that contain any of the keywords."""
    result = []
    for line in lines:
        line_text = line.get("text", "").lower()
        if any(k.lower() in line_text for k in keywords):
            result.append(line)
    return result


def _extract_lot(lines: List[Dict]) -> FieldValue:
    """Extract lot_no from lines."""
    label_keywords = ["lot", "homesite"]
    label_lines = _find_lines_with_keywords(lines, label_keywords)
    candidates = []
    
    for line in label_lines:
        # Get tokens after "lot" keyword
        for i, token in enumerate(line.get("tokens", [])):
            if any(k in token.get("text", "").lower() for k in label_keywords):
                # Take next token(s) after the keyword
                if i + 1 < len(line["tokens"]):
                    next_token = line["tokens"][i + 1].get("text", "")
                    if next_token.strip() and not any(k in next_token.lower() for k in ["lot", "homesite", "no", "number", ":"]):
                        candidates.append((next_token, 0.8))
    
    return pick_best_lot(candidates)


def _extract_block(lines: List[Dict]) -> FieldValue:
    """Extract block from lines."""
    label_keywords = ["block", "blk"]
    label_lines = _find_lines_with_keywords(lines, label_keywords)
    candidates = []
    
    for line in label_lines:
        for i, token in enumerate(line.get("tokens", [])):
            if any(k in token.get("text", "").lower() for k in label_keywords):
                if i + 1 < len(line["tokens"]):
                    next_token = line["tokens"][i + 1].get("text", "")
                    if next_token.strip() and not any(k in next_token.lower() for k in ["block", "blk"]):
                        candidates.append((next_token, 0.8))
    
    return pick_best_block(candidates)


def _extract_address(lines: List[Dict]) -> FieldValue:
    """Extract address from lines."""
    label_keywords = ["address", "addr"]
    label_lines = _find_lines_with_keywords(lines, label_keywords)
    candidates = []
    
    for line in label_lines:
        # Take the whole line text after "address"
        text = line.get("text", "").strip()
        if text:
            candidates.append((text, 0.7))
    
    return pick_best_address(candidates)


def _extract_garage(lines: List[Dict]) -> FieldValue:
    """Extract garage_swing from lines."""
    label_keywords = ["garage", "door", "swing"]
    label_lines = _find_lines_with_keywords(lines, label_keywords)
    candidates = []
    
    for line in label_lines:
        text = line.get("text", "").strip()
        if text:
            candidates.append((text, 0.8))
    
    return pick_best_garage(candidates)


def _extract_model(lines: List[Dict]) -> FieldValue:
    """Extract model_selected from lines."""
    label_keywords = ["model", "home model"]
    label_lines = _find_lines_with_keywords(lines, label_keywords)
    candidates = []
    
    for line in label_lines:
        for i, token in enumerate(line.get("tokens", [])):
            if any(k in token.get("text", "").lower() for k in label_keywords):
                if i + 1 < len(line["tokens"]):
                    next_token = line["tokens"][i + 1].get("text", "")
                    if next_token.strip():
                        candidates.append((next_token, 0.75))
    
    return pick_best_model(candidates)


def _extract_elevation(lines: List[Dict]) -> FieldValue:
    """Extract elevation from lines."""
    label_keywords = ["elevation", "elev"]
    label_lines = _find_lines_with_keywords(lines, label_keywords)
    candidates = []
    
    for line in label_lines:
        for i, token in enumerate(line.get("tokens", [])):
            if any(k in token.get("text", "").lower() for k in label_keywords):
                if i + 1 < len(line["tokens"]):
                    next_token = line["tokens"][i + 1].get("text", "")
                    if next_token.strip():
                        candidates.append((next_token, 0.75))
    
    return pick_best_elevation(candidates)


def _extract_notes(lines: List[Dict]) -> FieldValue:
    """Extract optional_notes from lines."""
    label_keywords = ["notes", "notes:", "remarks"]
    label_lines = _find_lines_with_keywords(lines, label_keywords)
    candidates = []
    
    for line in label_lines:
        text = line.get("text", "").strip()
        if text:
            candidates.append((text, 0.6))
    
    return pick_best_notes(candidates)


def run_all_field_extractors(ocr_tokens: List[Dict[str, Any]]) -> Dict[str, FieldValue]:
    """
    Run all field extractors on OCR tokens.
    
    Args:
        ocr_tokens: List of OCR tokens from paddle_service.ocr_image
    
    Returns:
        Dict mapping field names to FieldValue objects
    """
    # Group tokens into lines first
    lines = group_into_lines(ocr_tokens)
    
    # Extract all fields
    lot = _extract_lot(lines)
    block = _extract_block(lines)
    address = _extract_address(lines)
    garage = _extract_garage(lines)
    model = _extract_model(lines)
    elevation = _extract_elevation(lines)
    notes = _extract_notes(lines)
    
    return {
        "lot_no": lot.value,
        "block": block.value,
        "address": address.value,
        "garage_swing": garage.value,
        "model_selected": model.value,
        "elevation": elevation.value,
        "optional_notes": notes.value,
        "external_structure": None,  # TODO: add extraction logic
    }
