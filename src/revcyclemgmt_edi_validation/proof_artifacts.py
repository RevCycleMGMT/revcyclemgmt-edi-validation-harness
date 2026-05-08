from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
from typing import Any

from .rules import TRANSACTION_RULES
from .validator import validate_x12_file


FIXTURE_BY_TRANSACTION = {
    "837P": "valid_837p.edi",
    "837I": "valid_837i.edi",
    "835": "valid_835.edi",
    "999": "valid_999.edi",
    "277CA": "valid_277ca.edi",
    "270": "valid_270.edi",
    "271": "valid_271.edi",
    "276": "valid_276.edi",
    "277": "valid_277.edi",
    "275": "valid_275.edi",
}

WORKFLOW_LABELS = {
    "837P": "Professional claim",
    "837I": "Institutional claim",
    "835": "Electronic remittance",
    "999": "Implementation ACK",
    "277CA": "Claim acknowledgment",
    "270": "Eligibility request",
    "271": "Eligibility response",
    "276": "Claim-status request",
    "277": "Claim-status response",
    "275": "Claim attachment",
}


def _svg_text(value: Any) -> str:
    return escape(str(value), quote=True)


def _fixture_records(fixtures_dir: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for fixture in sorted(fixtures_dir.glob("*.edi")):
        report = validate_x12_file(fixture)
        records.append(
            {
                "path": str(fixture),
                "file": fixture.name,
                "valid": report.valid,
                "transaction_type": report.transaction_type or "unknown",
                "segment_count": report.segment_count,
                "error_count": len(report.errors),
                "warning_count": len(report.warnings),
                "errors": report.errors,
                "warnings": report.warnings,
            }
        )
    return records


def build_proof_model(fixtures_dir: Path) -> dict[str, Any]:
    records = _fixture_records(fixtures_dir)
    transaction_counts: dict[str, int] = {}
    for record in records:
        transaction_type = record["transaction_type"]
        transaction_counts[transaction_type] = transaction_counts.get(transaction_type, 0) + 1

    coverage: list[dict[str, Any]] = []
    for transaction_type, required_segments in TRANSACTION_RULES.items():
        fixture_name = FIXTURE_BY_TRANSACTION.get(transaction_type, "")
        match = next((record for record in records if record["file"] == fixture_name), None)
        coverage.append(
            {
                "transaction_type": transaction_type,
                "workflow": WORKFLOW_LABELS.get(transaction_type, transaction_type),
                "fixture": fixture_name,
                "required_segments": list(required_segments),
                "valid": bool(match and match["valid"]),
                "segment_count": match["segment_count"] if match else 0,
            }
        )

    invalid_files = [record for record in records if not record["valid"]]
    valid_count = sum(1 for record in records if record["valid"])
    error_count = sum(record["error_count"] for record in records)

    return {
        "headline": "Synthetic EDI validation proof: ten transaction families checked before a clearinghouse route.",
        "summary": {
            "valid": valid_count == len(records),
            "file_count": len(records),
            "valid_count": valid_count,
            "invalid_count": len(records) - valid_count,
            "transaction_family_count": len(TRANSACTION_RULES),
            "error_count": error_count,
            "transaction_counts": dict(sorted(transaction_counts.items())),
        },
        "workflow_steps": [
            "File intake",
            "Parse X12",
            "Detect ST01",
            "Check envelope",
            "Check rules",
            "Control numbers",
            "Action report",
        ],
        "coverage": coverage,
        "invalid_files": invalid_files,
        "buyer_readout": [
            f"{len(TRANSACTION_RULES)} synthetic transaction families are covered by fixture-backed validation.",
            f"{valid_count} files pass; {len(invalid_files)} intentionally fail so implementation errors are visible.",
            "Control-number mismatches and missing required segments become clear action items before go-live.",
        ],
    }


def _metric_card(x: int, y: int, label: str, value: str, note: str) -> str:
    return f"""
      <g>
        <rect x="{x}" y="{y}" width="178" height="104" rx="10" fill="#081012" stroke="#164e53"/>
        <text x="{x + 16}" y="{y + 28}" class="kicker">{_svg_text(label)}</text>
        <text x="{x + 16}" y="{y + 62}" class="metric">{_svg_text(value)}</text>
        <text x="{x + 16}" y="{y + 86}" class="muted">{_svg_text(note)}</text>
      </g>
    """


def _workflow_node(x: int, y: int, label: str, index: int) -> str:
    return f"""
      <g>
        <circle cx="{x}" cy="{y}" r="22" fill="#00B3A4"/>
        <text x="{x}" y="{y + 6}" class="node-number" text-anchor="middle">{index}</text>
        <text x="{x}" y="{y + 48}" class="tiny strong" text-anchor="middle">{_svg_text(label)}</text>
      </g>
    """


def _coverage_cell(x: int, y: int, item: dict[str, Any]) -> str:
    status = "PASS" if item["valid"] else "FAIL"
    status_color = "#83f7f4" if item["valid"] else "#f97316"
    required = ", ".join(item["required_segments"][:5])
    return f"""
      <g>
        <rect x="{x}" y="{y}" width="222" height="74" rx="10" fill="#081012" stroke="#173f43"/>
        <circle cx="{x + 18}" cy="{y + 22}" r="7" fill="{status_color}"/>
        <text x="{x + 34}" y="{y + 25}" class="small strong">{_svg_text(item['transaction_type'])}</text>
        <text x="{x + 174}" y="{y + 25}" class="tiny strong" fill="{status_color}">{status}</text>
        <text x="{x + 18}" y="{y + 47}" class="tiny">{_svg_text(item['workflow'])}</text>
        <text x="{x + 18}" y="{y + 64}" class="muted">{_svg_text(required)}</text>
      </g>
    """


def _invalid_row(y: int, item: dict[str, Any]) -> str:
    first_error = item["errors"][0] if item["errors"] else "Validation failed."
    if len(first_error) > 74:
        first_error = first_error[:71] + "..."
    return f"""
      <g>
        <rect x="58" y="{y}" width="1164" height="44" rx="9" fill="#081012" stroke="#173f43"/>
        <circle cx="84" cy="{y + 22}" r="7" fill="#f97316"/>
        <text x="106" y="{y + 19}" class="small strong">{_svg_text(item['file'])}</text>
        <text x="106" y="{y + 36}" class="tiny">{_svg_text(item['transaction_type'])} | {item['error_count']} error(s)</text>
        <text x="404" y="{y + 27}" class="small">{_svg_text(first_error)}</text>
      </g>
    """


def render_validation_svg(model: dict[str, Any]) -> str:
    summary = model["summary"]
    cards = [
        ("Files", str(summary["file_count"]), "synthetic fixtures"),
        ("Valid", str(summary["valid_count"]), "ready examples"),
        ("Invalid", str(summary["invalid_count"]), "actionable failures"),
        ("Families", str(summary["transaction_family_count"]), "X12 workflows"),
        ("Errors", str(summary["error_count"]), "caught early"),
        ("Output", "JSON", "CI/dashboard ready"),
    ]
    card_markup = "\n".join(
        _metric_card(46 + index * 196, 158, label, value, note)
        for index, (label, value, note) in enumerate(cards)
    )

    workflow_xs = [98, 278, 458, 638, 818, 998, 1178]
    workflow_markup = []
    for index, (x, label) in enumerate(zip(workflow_xs, model["workflow_steps"], strict=True), start=1):
        workflow_markup.append(_workflow_node(x, 326, label, index))
        if index < len(workflow_xs):
            next_x = workflow_xs[index]
            workflow_markup.append(
                f'<path d="M{x + 30} 326 L{next_x - 30} 326" stroke="#83f7f4" stroke-width="5" stroke-linecap="round" opacity=".72"/>'
            )

    coverage_markup = []
    for index, item in enumerate(model["coverage"]):
        col = index % 5
        row = index // 5
        coverage_markup.append(_coverage_cell(58 + col * 236, 436 + row * 88, item))

    invalid_rows = "\n".join(_invalid_row(642 + index * 52, item) for index, item in enumerate(model["invalid_files"][:2]))
    readout_lines = "".join(
        f'<text x="58" y="{766 + index * 18}" class="readout">{_svg_text(line)}</text>'
        for index, line in enumerate(model["buyer_readout"][:2])
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="840" viewBox="0 0 1280 840" role="img" aria-labelledby="title desc">
  <title id="title">RevCycleMGMT synthetic EDI validation coverage proof</title>
  <desc id="desc">Synthetic X12 transaction coverage, validation flow, pass/fail summary, and actionable error report.</desc>
  <defs>
    <radialGradient id="tealGlow" cx="18%" cy="6%" r="68%">
      <stop offset="0%" stop-color="#83f7f4" stop-opacity=".17"/>
      <stop offset="58%" stop-color="#00B3A4" stop-opacity=".06"/>
      <stop offset="100%" stop-color="#020607" stop-opacity="1"/>
    </radialGradient>
    <linearGradient id="panel" x1="0" x2="1">
      <stop offset="0%" stop-color="#071012" stop-opacity=".98"/>
      <stop offset="100%" stop-color="#0b1416" stop-opacity=".88"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="4" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <style>
      .title {{ font: 900 42px Inter, Arial, sans-serif; fill: #f8fafc; }}
      .subtitle {{ font: 500 18px Inter, Arial, sans-serif; fill: #cbd5e1; }}
      .kicker {{ font: 900 12px Inter, Arial, sans-serif; fill: #83f7f4; letter-spacing: .12em; text-transform: uppercase; }}
      .metric {{ font: 900 30px Inter, Arial, sans-serif; fill: #ffffff; }}
      .node-number {{ font: 900 17px Inter, Arial, sans-serif; fill: #031719; }}
      .small {{ font: 700 15px Inter, Arial, sans-serif; fill: #d9fffd; }}
      .tiny {{ font: 600 12px Inter, Arial, sans-serif; fill: #cbd5e1; }}
      .muted {{ font: 600 11px Inter, Arial, sans-serif; fill: #94a3b8; }}
      .readout {{ font: 700 16px Inter, Arial, sans-serif; fill: #e2e8f0; }}
      .strong {{ font-weight: 900; fill: #f8fafc; }}
    </style>
  </defs>
  <rect width="1280" height="840" fill="#020607"/>
  <rect width="1280" height="840" fill="url(#tealGlow)"/>
  <path d="M0 764 C160 700 300 824 490 758 C690 692 840 812 1068 746 C1186 712 1230 720 1280 680 L1280 840 L0 840 Z" fill="#00B3A4" opacity=".06"/>
  <rect x="28" y="28" width="1224" height="784" rx="18" fill="url(#panel)" stroke="#164e53"/>
  <text x="56" y="78" class="kicker">Synthetic EDI Validation Proof</text>
  <text x="56" y="124" class="title">X12 files tested before the route goes live.</text>
  <text x="56" y="154" class="subtitle">Coverage for claims, remits, acknowledgments, eligibility, claim status, and attachments without public PHI.</text>
  <g filter="url(#glow)">
    <circle cx="1178" cy="84" r="7" fill="#83f7f4"/>
    <circle cx="1204" cy="84" r="7" fill="#00B3A4"/>
    <circle cx="1230" cy="84" r="7" fill="#facc15"/>
  </g>
  {card_markup}
  <rect x="46" y="292" width="1188" height="104" rx="14" fill="#061012" stroke="#164e53"/>
  <text x="68" y="316" class="kicker">Validation Flow</text>
  {"".join(workflow_markup)}
  <rect x="46" y="410" width="1188" height="202" rx="14" fill="#061012" stroke="#164e53"/>
  <text x="68" y="432" class="kicker">Transaction Coverage</text>
  {"".join(coverage_markup)}
  <rect x="46" y="626" width="1188" height="124" rx="14" fill="#061012" stroke="#164e53"/>
  <text x="68" y="650" class="kicker">Actionable Failure Examples</text>
  {invalid_rows}
  <rect x="46" y="754" width="1188" height="58" rx="14" fill="#071012" stroke="#164e53"/>
  {readout_lines}
</svg>
"""


def run(fixtures_dir: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    model = build_proof_model(fixtures_dir)
    svg = render_validation_svg(model)
    (output_dir / "edi_validation_report.json").write_text(
        json.dumps(model, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "edi_validation_coverage.svg").write_text(svg, encoding="utf-8")
    return {
        "file_count": model["summary"]["file_count"],
        "valid_count": model["summary"]["valid_count"],
        "invalid_count": model["summary"]["invalid_count"],
        "transaction_family_count": model["summary"]["transaction_family_count"],
        "artifact_count": 2,
        "svg": str(output_dir / "edi_validation_coverage.svg"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build RevCycleMGMT EDI validation proof artifacts.")
    parser.add_argument("--fixtures", type=Path, default=Path("tests/fixtures"))
    parser.add_argument("--out", type=Path, default=Path("output_demo"))
    args = parser.parse_args()
    print(json.dumps(run(args.fixtures, args.out), indent=2))


if __name__ == "__main__":
    main()
