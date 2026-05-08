from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .validator import validate_x12_file


def _print_report(path: Path) -> bool:
    report = validate_x12_file(path)
    payload = report.to_dict()
    payload["path"] = str(path)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return report.valid


def _folder_summary(path: Path, files: list[Path]) -> dict[str, Any]:
    file_reports: list[dict[str, Any]] = []
    transaction_counts: dict[str, int] = {}
    valid_count = 0

    for file_path in files:
        report = validate_x12_file(file_path)
        transaction_type = report.transaction_type or "unknown"
        transaction_counts[transaction_type] = transaction_counts.get(transaction_type, 0) + 1
        if report.valid:
            valid_count += 1

        file_reports.append(
            {
                "path": str(file_path),
                "valid": report.valid,
                "transaction_type": report.transaction_type,
                "segment_count": report.segment_count,
                "error_count": len(report.errors),
                "warning_count": len(report.warnings),
                "errors": report.errors,
                "warnings": report.warnings,
            }
        )

    return {
        "valid": valid_count == len(files),
        "path": str(path),
        "file_count": len(files),
        "valid_count": valid_count,
        "invalid_count": len(files) - valid_count,
        "transaction_counts": dict(sorted(transaction_counts.items())),
        "files": file_reports,
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="revcyclemgmt-edi-validate")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validate one synthetic X12 file.")
    validate_parser.add_argument("path", type=Path)

    folder_parser = subparsers.add_parser("validate-folder", help="Validate all .edi files in a folder.")
    folder_parser.add_argument("path", type=Path)
    folder_parser.add_argument(
        "--summary",
        action="store_true",
        help="Print one folder-level JSON summary instead of one report per file.",
    )

    args = parser.parse_args(argv)

    if args.command == "validate":
        ok = _print_report(args.path)
        raise SystemExit(0 if ok else 1)

    files = sorted(args.path.glob("*.edi"))
    if not files:
        print(json.dumps({"valid": False, "errors": [f"No .edi files found in {args.path}"]}, indent=2))
        raise SystemExit(1)

    if args.summary:
        summary = _folder_summary(args.path, files)
        print(json.dumps(summary, indent=2, sort_keys=True))
        raise SystemExit(0 if summary["valid"] else 1)

    all_ok = True
    for file_path in files:
        all_ok = _print_report(file_path) and all_ok
    raise SystemExit(0 if all_ok else 1)
