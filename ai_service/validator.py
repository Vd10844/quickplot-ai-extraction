# ai_service/validator.py
"""
Validation and field extraction helpers.
"""
from typing import Dict, Optional, List, Tuple
from .schemas import FieldValue


def validate_fields(fields_dict: Dict[str, Optional[str]]) -> Dict[str, Optional[str]]:
    """
    Validate and clean extracted fields.
    
    Args:
        fields_dict: Raw extracted fields from rules
    
    Returns:
        Cleaned and validated fields_dict
    """
    validated = {}
    for key, value in fields_dict.items():
        # Strip whitespace and handle None
        if value is None or value == "":
            validated[key] = None
        else:
            validated[key] = str(value).strip()
    
    return validated


# ============================================================================
# FIELD-SPECIFIC PICKER FUNCTIONS
# ============================================================================

def pick_best_lot(candidates: List[Tuple[str, float]]) -> FieldValue:
    """
    Pick the best lot_no candidate from a list of (text, confidence) tuples.
    
    Args:
        candidates: List of (text, confidence_score) tuples
    
    Returns:
        FieldValue with best candidate or None
    """
    if not candidates:
        return FieldValue(value=None, confidence=0.0)
    
    # Sort by confidence descending, take best
    best = max(candidates, key=lambda x: x[1])
    return FieldValue(value=best[0], confidence=best[1])


def pick_best_block(candidates: List[Tuple[str, float]]) -> FieldValue:
    """Pick the best block candidate."""
    if not candidates:
        return FieldValue(value=None, confidence=0.0)
    
    best = max(candidates, key=lambda x: x[1])
    return FieldValue(value=best[0], confidence=best[1])


def pick_best_address(candidates: List[Tuple[str, float]]) -> FieldValue:
    """Pick the best address candidate."""
    if not candidates:
        return FieldValue(value=None, confidence=0.0)
    
    # Prefer longer strings (more likely to be full address)
    best = max(candidates, key=lambda x: (x[1], len(x[0])))
    return FieldValue(value=best[0], confidence=best[1])


def pick_best_garage(candidates: List[Tuple[str, float]]) -> FieldValue:
    """Pick the best garage_swing candidate."""
    if not candidates:
        return FieldValue(value=None, confidence=0.0)
    
    best = max(candidates, key=lambda x: x[1])
    return FieldValue(value=best[0], confidence=best[1])


def pick_best_model(candidates: List[Tuple[str, float]]) -> FieldValue:
    """Pick the best model_selected candidate."""
    if not candidates:
        return FieldValue(value=None, confidence=0.0)
    
    best = max(candidates, key=lambda x: x[1])
    return FieldValue(value=best[0], confidence=best[1])


def pick_best_elevation(candidates: List[Tuple[str, float]]) -> FieldValue:
    """Pick the best elevation candidate."""
    if not candidates:
        return FieldValue(value=None, confidence=0.0)
    
    best = max(candidates, key=lambda x: x[1])
    return FieldValue(value=best[0], confidence=best[1])


def pick_best_notes(candidates: List[Tuple[str, float]]) -> FieldValue:
    """Pick the best optional_notes candidate."""
    if not candidates:
        return FieldValue(value=None, confidence=0.0)
    
    # For notes, prefer longer text (more info)
    best = max(candidates, key=lambda x: (x[1], len(x[0])))
    return FieldValue(value=best[0], confidence=best[1])


def is_valid_lot(lot_no: Optional[str]) -> bool:
    """Check if lot_no is valid format."""
    if not lot_no:
        return True  # Optional field
    return len(lot_no) > 0


def is_valid_block(block: Optional[str]) -> bool:
    """Check if block is valid format."""
    if not block:
        return True  # Optional field
    return len(block) > 0


def is_valid_address(address: Optional[str]) -> bool:
    """Check if address is valid format."""
    if not address:
        return True  # Optional field
    return len(address) > 5


def is_valid_phone(phone: Optional[str]) -> bool:
    """Check if phone number looks valid."""
    if not phone:
        return True  # Optional field
    return any(c.isdigit() for c in phone)
