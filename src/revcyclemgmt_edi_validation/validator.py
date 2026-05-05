from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .parser import Segment, all_segments, first_segment, parse_x12_segments
from .rules import ENVELOPE_SEGMENTS, TRANSACTION_RULES, classify_transaction


@dataclass
class ValidationReport:
    valid: bool
    transaction_type: str | None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    segment_count: int = 0
    control_numbers: dict[str, str] = field(default_factory=dict)
    required_segments: list[str] = field(default_factory=list)
    present_segments: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _segment_counts(segments: list[Segment]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for segment in segments:
        counts[segment.tag] = counts.get(segment.tag, 0) + 1
    return counts


def _control_numbers(segments: list[Segment]) -> dict[str, str]:
    isa = first_segment(segments, "ISA")
    gs = first_segment(segments, "GS")
    st = first_segment(segments, "ST")
    se = first_segment(segments, "SE")
    ge = first_segment(segments, "GE")
    iea = first_segment(segments, "IEA")
    return {
        "isa13": isa.value(12) if isa else "",
        "iea02": iea.value(1) if iea else "",
        "gs06": gs.value(5) if gs else "",
        "ge02": ge.value(1) if ge else "",
        "st02": st.value(1) if st else "",
        "se02": se.value(1) if se else "",
    }


def _st_to_se_segment_count(segments: list[Segment]) -> int | None:
    st_index = next((idx for idx, segment in enumerate(segments) if segment.tag == "ST"), None)
    se_index = next((idx for idx, segment in enumerate(segments) if segment.tag == "SE"), None)
    if st_index is None or se_index is None or se_index < st_index:
        return None
    return se_index - st_index + 1


def _validate_control_numbers(segments: list[Segment], report: ValidationReport) -> None:
    controls = report.control_numbers
    if controls["isa13"] and controls["iea02"] and controls["isa13"] != controls["iea02"]:
        report.errors.append("ISA13 does not match IEA02 interchange control number.")
    if controls["gs06"] and controls["ge02"] and controls["gs06"] != controls["ge02"]:
        report.errors.append("GS06 does not match GE02 functional group control number.")
    if controls["st02"] and controls["se02"] and controls["st02"] != controls["se02"]:
        report.errors.append("ST02 does not match SE02 transaction set control number.")

    se = first_segment(segments, "SE")
    counted = _st_to_se_segment_count(segments)
    if se and counted is not None:
        declared = se.value(0)
        if declared.isdigit() and int(declared) != counted:
            report.errors.append(f"SE01 declares {declared} segments, but ST-to-SE count is {counted}.")
        elif not declared.isdigit():
            report.errors.append("SE01 segment count is not numeric.")


def validate_x12_text(x12_text: str) -> ValidationReport:
    segments = parse_x12_segments(x12_text)
    counts = _segment_counts(segments)
    controls = _control_numbers(segments)
    st = first_segment(segments, "ST")
    transaction_type = classify_transaction(st.value(0), counts) if st else None
    required_segments = list(ENVELOPE_SEGMENTS) + list(TRANSACTION_RULES.get(transaction_type or "", ()))

    report = ValidationReport(
        valid=False,
        transaction_type=transaction_type,
        segment_count=len(segments),
        control_numbers=controls,
        required_segments=required_segments,
        present_segments=counts,
    )

    if not segments:
        report.errors.append("No X12 segments found.")
        return report

    if not st:
        report.errors.append("Missing ST transaction set header.")

    for tag in ENVELOPE_SEGMENTS:
        if counts.get(tag, 0) == 0:
            report.errors.append(f"Missing required envelope segment {tag}.")

    if transaction_type not in TRANSACTION_RULES:
        report.errors.append(f"Unsupported or unrecognized transaction type: {transaction_type or 'unknown'}.")
    else:
        for tag in TRANSACTION_RULES[transaction_type]:
            if counts.get(tag, 0) == 0:
                report.errors.append(f"Missing required {transaction_type} segment {tag}.")

    if counts.get("ISA", 0) > 1 or counts.get("IEA", 0) > 1:
        report.warnings.append("Multiple interchange envelopes detected; validate each interchange separately.")

    if all_segments(segments, "CLM") and not (counts.get("SV1", 0) or counts.get("SV2", 0)):
        report.errors.append("Claim segment exists but no professional or institutional service line was found.")

    _validate_control_numbers(segments, report)
    report.valid = not report.errors
    return report


def validate_x12_file(path: str | Path) -> ValidationReport:
    return validate_x12_text(Path(path).read_text(encoding="utf-8", errors="ignore"))
