"""Check Racall exports in real LibreOffice; no models or desktop installation."""

import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("test-results/presentation-compatibility"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    sys.path[:0] = [str(root), str(root / "apps/api")]
    from scripts.presentation_compatibility.runner import run

    print(json.dumps(run(args.output, root), ensure_ascii=False))


if __name__ == "__main__":
    main()
