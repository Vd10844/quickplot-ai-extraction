# ai_service/router.py
from fastapi import APIRouter, UploadFile, File, HTTPException
import tempfile
from pathlib import Path

from .service import extract_order_form
from .schemas import ExtractionResponse

router = APIRouter(prefix="/extract", tags=["extraction"])

ALLOWED_SUFFIXES = {".pdf", ".png", ".jpg", ".jpeg", ".bmp", ".tiff"}


@router.post("/order-form", response_model=ExtractionResponse)
async def extract_order_form_endpoint(
    file: UploadFile = File(...)
) -> ExtractionResponse:
    suffix = Path(file.filename).suffix.lower()

    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {suffix}",
        )

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        return extract_order_form(tmp_path)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        try:
            Path(tmp_path).unlink(missing_ok=True)
        except Exception:
            pass
