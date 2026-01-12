# ai_service/schemas.py
from typing import Optional, List
from pydantic import BaseModel, Field


class OCRToken(BaseModel):
    """Canonical OCR token representation."""
    text: str
    bbox: List[List[int]]
    confidence: float
    page: Optional[int] = None


class FieldValue(BaseModel):
    """Single extracted field with confidence and source."""
    value: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    source: Optional[str] = None  # regex | layout | llm | manual


class OrderFormSchema(BaseModel):
    lot_no: Optional[str] = None
    block: Optional[str] = None
    address: Optional[str] = None
    model_selected: Optional[str] = None
    elevation: Optional[str] = None
    garage_swing: Optional[str] = None
    external_structure: Optional[str] = None
    optional_notes: Optional[str] = None


class ExtractionResponse(BaseModel):
    ok: bool
    engine: str = "ocr_rules_v1"
    schema_version: str = "1.0"
    data: OrderFormSchema
    confidence: float = Field(ge=0.0, le=1.0)
    processing_ms: int
    errors: List[str] = []
