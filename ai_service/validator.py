# ai_service/validator.py
from typing import Dict
from .schemas import FieldValue


def validate_fields(fields: Dict[str, FieldValue]) -> Dict[str, FieldValue]:
    validated = {}

    for name, field in fields.items():
        if field.value is None:
            validated[name] = field
            continue

        clean = field.value.strip()
        validated[name] = FieldValue(
            value=clean if clean else None,
            confidence=field.confidence,
            source=field.source,
        )

    return validated
