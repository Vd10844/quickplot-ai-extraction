# ai_service/cli.py
"""
CLI utility for local testing of extraction on image/PDF files.
Run: python -m ai_service.cli <path_to_image_or_pdf>
"""
import sys
import json
from pathlib import Path

from .service import extract_order_form


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m ai_service.cli <path_to_image_or_pdf>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not Path(file_path).exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    try:
        result = extract_order_form(file_path)
        print(json.dumps(result.model_dump(), indent=2))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
