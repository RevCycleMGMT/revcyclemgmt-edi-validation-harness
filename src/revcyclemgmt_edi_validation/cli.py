from __future__ import annotations

import argparse
import json
from pathlib import Path

from .validator import validate_x12_file


def _print_report(path: Path) -> bool:
    report = validate_x12_file(path)
    payload = report.to_dict()
    payload["path"] = str(path)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return report.valid


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="revcyclemgmt-edi-validate")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validate one synthetic X12 file.")
    validate_parser.add_argument("path", type=Path)

    folder_parser = subparsers.add_parser("validate-folder", help="Validate all .edi files in a folder.")
    folder_parser.add_argument("path", type=Path)

    args = parser.parse_args(argv)

    if args.command == "validate":
        ok = _print_report(args.path)
        raise SystemExit(0 if ok else 1)

    files = sorted(args.path.glob("*.edi"))
    if not files:
        print(json.dumps({"valid": False, "errors": [f"No .edi files found in {args.path}"]}, indent=2))
        raise SystemExit(1)

    all_ok = True
    for file_path in files:
        all_ok = _print_report(file_path) and all_ok
    raise SystemExit(0 if all_ok else 1)
