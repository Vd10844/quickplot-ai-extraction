# Integration Guide: Quickplot AI Extraction Service

This guide explains how to integrate the **quickplot-ai-extraction** service with the main Quickplot backend.

## Overview

The extraction service provides two integration patterns:

1. **Option A: Integrated FastAPI Router** (for initial testing & development)
2. **Option B: Separate Microservice** (for production & scaling)

---

## Option A: Integrated FastAPI Router (Recommended for Testing)

Use this approach for **initial testing** with the Quickplot backend.

### Step 1: Clone the extraction service into Quickplot

```bash
cd quickplot-api/src
git clone https://github.com/Vd10844/quickplot-ai-extraction.git ai_extraction
cd ../..
```

Or, if you prefer git submodules:

```bash
cd quickplot-api
git submodule add https://github.com/Vd10844/quickplot-ai-extraction.git src/ai_extraction
git submodule update --init --recursive
```

### Step 2: Update Quickplot's main FastAPI app

In `quickplot-api/src/main.py` (or your entry point):

```python
from fastapi import FastAPI
from ai_extraction.ai_service.router import router as extraction_router

app = FastAPI()

# ... your existing middleware, routes, etc ...

# Mount the extraction service at /api/v1/extract
app.include_router(extraction_router, prefix="/api/v1")
```

### Step 3: Share dependencies (optional but recommended)

Add these to Quickplot's `requirements.txt`:

```
paddleocr>=2.7.0
pillow>=10.1.0
```

### Step 4: Test the endpoint

Start your Quickplot FastAPI server:

```bash
cd quickplot-api
uvicorn src.main:app --reload
```

Visit the interactive docs:

```
http://localhost:8000/docs
```

Find the `/api/v1/extract/order-form` endpoint and test it via the **"Try it out"** button.

---

## Option B: Separate Microservice (Production)

Use this approach for **production deployment** when extraction becomes heavy or needs independent scaling.

### Step 1: Keep services separate

- **Quickplot API** runs on `http://localhost:8000`
- **Extraction Service** runs on `http://localhost:8001`

### Step 2: Deploy extraction service

```bash
cd quickplot-ai-extraction
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn ai_service.router:router --host 0.0.0.0 --port 8001
```

### Step 3: Call from Quickplot via HTTP

In Quickplot's FastAPI app, create a wrapper endpoint:

```python
import httpx
from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter(prefix="/api/v1", tags=["extraction"])

EXTRACTION_SERVICE_URL = "http://localhost:8001"

@router.post("/extract/order-form")
async def extract_order_form(file: UploadFile = File(...)):
    """Proxy endpoint that calls the extraction microservice."""
    try:
        async with httpx.AsyncClient() as client:
            # Forward the file to the extraction service
            files = {"file": (file.filename, await file.read(), file.content_type)}
            response = await client.post(
                f"{EXTRACTION_SERVICE_URL}/extract/order-form",
                files=files,
                timeout=60.0
            )
            return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Extraction service unavailable: {str(e)}"
        )
```

### Step 4: Optional - Use Celery for async processing

For long-running extractions, wrap in a Celery task:

```python
from celery import shared_task
import httpx

@shared_task
def extract_order_form_async(file_id: str, file_path: str):
    """Background task to extract from file."""
    with open(file_path, "rb") as f:
        files = {"file": (f.name, f, "image/png")}
        response = httpx.post(
            f"{EXTRACTION_SERVICE_URL}/extract/order-form",
            files=files,
            timeout=60.0
        )
    
    # Store result in database
    return response.json()
```

---

## Testing Checklist

### Before integration:

- [ ] Local CLI test passes: `python -m ai_service.cli path/to/image.png`
- [ ] Requirements match Quickplot's Python version (3.12+)
- [ ] All dependencies in `requirements.txt` are compatible

### After integration (Option A):

- [ ] FastAPI mounts without errors
- [ ] `/api/v1/extract/order-form` appears in `/docs`
- [ ] Can upload a test image via Swagger UI
- [ ] Response matches `ExtractionResponse` schema
- [ ] Extractred fields (lot_no, block, etc.) are present in JSON

### After integration (Option B):

- [ ] Extraction service runs independently on port 8001
- [ ] Quickplot proxy endpoint calls it successfully
- [ ] Response latency is acceptable (<5s per image)
- [ ] Error handling works (service down → 503 error)
- [ ] (Optional) Celery task processes files in background

---

## Architecture Diagram

### Option A: Integrated

```
┌─────────────────────────────────────────┐
│    Quickplot FastAPI App                │
│  ┌────────────────────────────────────┐ │
│  │  /api/v1/extract/order-form        │ │
│  │  (mounted from ai_service.router)  │ │
│  └────────────────────────────────────┘ │
│  ┌────────────────────────────────────┐ │
│  │  Other Quickplot routes            │ │
│  │  (projects, files, CAD, etc.)      │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
         Single FastAPI App on :8000
```

### Option B: Microservice

```
┌──────────────────────┐         ┌──────────────────────┐
│  Quickplot API       │         │ Extraction Service   │
│  ┌────────────────┐  │         │ ┌────────────────┐   │
│  │ /api/v1/*      │  │         │ │ /extract/*     │   │
│  │ (proxy to 8001)│─────HTTP──→│ │ (PaddleOCR +   │   │
│  └────────────────┘  │         │ │  rules + LLM)  │   │
│                      │         │ └────────────────┘   │
│  (Redis + Celery)    │         │                      │
│  Optional: async     │         │ (Stateless)         │
│  task processing     │         │                      │
└──────────────────────┘         └──────────────────────┘
      Port :8000                       Port :8001
```

---

## Environment Variables (Option B only)

Create `.env` in Quickplot root:

```
EXTRACTION_SERVICE_URL=http://localhost:8001
EXTRACTION_SERVICE_TIMEOUT=60
```

Load in your app:

```python
import os
from dotenv import load_dotenv

load_dotenv()
EXTRACTION_SERVICE_URL = os.getenv("EXTRACTION_SERVICE_URL", "http://localhost:8001")
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'ai_service'"

**Fix:** Make sure the extraction service is in Python path:

```python
import sys
sys.path.insert(0, "src/ai_extraction")
```

Or use relative imports after cloning.

### Issue: "OCR model not found" / slow first request

**Fix:** PaddleOCR downloads models on first run (~500MB). Add this to your startup:

```python
from ai_service.paddle_service import get_ocr

@app.on_event("startup")
async def load_ocr_model():
    """Pre-load OCR model on startup."""
    get_ocr()
    print("✓ OCR model loaded")
```

### Issue: Endpoint returns "address is garbage text"

**Expected:** Current rules are basic. Once LLM refinement is added, accuracy will improve (v2).

**For now:** Review the `rules.py` extraction logic or adjust confidence thresholds.

---

## Next Steps (v2 Planning)

1. **LLM Refinement:** Add Qwen2.5 or similar for fixing extracted fields
2. **PDF Support:** Full multi-page PDF extraction
3. **Confidence Scoring:** Per-field confidence + source tracking
4. **Template Detection:** Auto-detect form type (order form vs. plat vs. custom)
5. **Metrics:** Track extraction accuracy, latency, common errors

---

## Questions?

- Check `README.md` for local testing
- Review `ai_service/` module structure
- Open an issue on GitHub

---

**Branch:** `feature/llm-refinement`
**Status:** Initial OCR + rules working; LLM refinement in progress
```

Now, create this file locally:

```bash
cd D:\10844\Q4\Jan\Week_01\quickplot_ai_poc
```
