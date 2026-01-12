# ai_service/router.py
from fastapi import APIRouter, UploadFile, File
from .service import extract_order_form_from_pdf, extract_order_form_from_image
import tempfile

router = APIRouter()

@router.post("/order-form/extract")
async def extract_order_form(file: UploadFile = File(...)):
    suffix = file.filename.lower().split(".")[-1]
    is_pdf = suffix == "pdf"
    with tempfile.NamedTemporaryFile(suffix="." + suffix, delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    if is_pdf:
        schema = extract_order_form_from_pdf(tmp_path)
    else:
        schema = extract_order_form_from_image(tmp_path)

    return {"ok": True, "data": schema.model_dump()}
