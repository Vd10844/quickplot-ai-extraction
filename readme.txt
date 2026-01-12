# Quickplot AI/ML Document Extraction Service

Production-ready extraction service for order forms and plat documents using OCR + layout rules + LLM refinement.

## Quick Start

```bash
# Setup
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Run FastAPI server
uvicorn ai_service.router:router --reload

# Test locally
python -m ai_service.cli path/to/image.png
