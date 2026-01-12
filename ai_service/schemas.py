# ai_service/schemas.py
"""
Unified schema definitions for order form extraction.
Includes both input/output types and internal field representations.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List


# ============================================================================
# FIELD-LEVEL SCHEMA (used internally and in response)
# ============================================================================

class FieldValue(BaseModel):
    """Represents a single extracted field with confidence score."""
    value: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    source: Optional[str] = None  # "regex", "layout", "llm", "manual"


# ============================================================================
# ORDER FORM SCHEMA (the 8 target fields)
# ============================================================================

class OrderFormSchema(BaseModel):
    """Final extracted order form data."""
    lot_no: Optional[str] = None
    block: Optional[str] = None
    address: Optional[str] = None
    model_selected: Optional[str] = None
    elevation: Optional[str] = None
    garage_swing: Optional[str] = None
    external_structure: Optional[str] = None
    optional_notes: Optional[str] = None


# ============================================================================
# API RESPONSE SCHEMA (wraps OrderFormSchema with metadata)
# ============================================================================

class ExtractionResponse(BaseModel):
    """Full API response for extraction endpoint."""
    ok: bool
    engine: str = "ocr_rules_llm_v1"
    schema_version: str = "1.0"
    data: OrderFormSchema
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    errors: List[str] = Field(default_factory=list)
    processing_ms: Optional[int] = None  # latency tracking
