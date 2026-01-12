# ai_service/cli.py
import sys
import json
from pathlib import Path

from .service import extract_order_form


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m ai_service.cli <file_path>")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(1)

    try:
        result = extract_order_form(str(path))
        print(json.dumps(result.model_dump(), indent=2))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
