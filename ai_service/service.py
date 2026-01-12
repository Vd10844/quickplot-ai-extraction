# ai_service/service.py
"""
Core extraction pipeline: OCR → layout → rules → validation → response.
Handles both images and PDFs (PDF logic added later with pdf2image).
"""
import tempfile
import time
from pathlib import Path
from typing import Optional

from .paddle_service import ocr_image
from .rules import run_all_field_extractors
from .validator import validate_fields
from .schemas import OrderFormSchema, ExtractionResponse

def extract_order_form_from_image(image_path: str) -> OrderFormSchema:
    """
    Extract order form fields from a single image file.
    
    Args:
        image_path: Path to image (PNG, JPG, etc.)
    
    Returns:
        OrderFormSchema with extracted fields
    
    Raises:
        ValueError: If file is unsupported or OCR fails
    """
    start_ms = time.time() * 1000
    
    try:
        # Step 1: Run OCR to get tokens
        ocr_tokens = ocr_image(image_path)
        if not ocr_tokens:
            raise ValueError("OCR returned no tokens; image may be blank or unsupported.")
        
        # Step 2: Run field extractors on OCR output
        fields_dict = run_all_field_extractors(ocr_tokens)
        
        # Step 3: Validate and clean fields
        validated_dict = validate_fields(fields_dict)
        
        # Step 4: Build response
        schema = OrderFormSchema(**validated_dict)
        return schema
    
    except Exception as e:
        raise ValueError(f"Image extraction failed: {str(e)}") from e


def extract_order_form_from_pdf(pdf_path: str) -> OrderFormSchema:
    """
    Extract order form fields from a PDF file.
    
    Converts each page to an image, runs OCR on each, aggregates results.
    
    Args:
        pdf_path: Path to PDF file
    
    Returns:
        OrderFormSchema with extracted fields from the entire PDF
    
    Raises:
        ValueError: If PDF is corrupted, has no pages, or OCR fails
    """
    try:
        import pdfplumber
        from pdf2image import convert_from_path
    except ImportError:
        raise ImportError(
            "PDF support requires 'pdfplumber' and 'pdf2image'. "
            "Install with: pip install pdfplumber pdf2image"
        )
    
    start_ms = time.time() * 1000
    
    try:
        # Convert PDF pages to images
        images = convert_from_path(pdf_path)
        if not images:
            raise ValueError("PDF has no pages or is corrupted.")
        
        # Run OCR on each page and aggregate
        all_tokens = []
        for page_num, image in enumerate(images):
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                image.save(tmp.name)
                tokens = ocr_image(tmp.name)
                # Tag tokens with page number for later debugging
                for token in tokens:
                    token["page"] = page_num
                all_tokens.extend(tokens)
                Path(tmp.name).unlink()  # cleanup
        
        if not all_tokens:
            raise ValueError("No OCR tokens extracted from any page in the PDF.")
        
        # Step 2: Run field extractors
        fields_dict = run_all_field_extractors(all_tokens)
        
        # Step 3: Validate
        validated_dict = validate_fields(fields_dict)
        
        # Step 4: Build response
        schema = OrderFormSchema(**validated_dict)
        return schema
    
    except Exception as e:
        raise ValueError(f"PDF extraction failed: {str(e)}") from e


def extract_order_form(file_path: str) -> OrderFormSchema:
    """
    Auto-detect file type and route to appropriate extractor.
    
    Args:
        file_path: Path to image or PDF
    
    Returns:
        OrderFormSchema
    
    Raises:
        ValueError: If file type unsupported or extraction fails
    """
    suffix = Path(file_path).suffix.lower()
    
    if suffix == ".pdf":
        return extract_order_form_from_pdf(file_path)
    elif suffix in {".png", ".jpg", ".jpeg", ".bmp", ".tiff"}:
        return extract_order_form_from_image(file_path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")
