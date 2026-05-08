import json
from pathlib import Path

import pytest

from revcyclemgmt_edi_validation.cli import main
from revcyclemgmt_edi_validation.proof_artifacts import run as proof_artifacts_run
from revcyclemgmt_edi_validation.validator import validate_x12_file, validate_x12_text


FIXTURES = Path(__file__).parent / "fixtures"


def test_valid_fixture_transaction_types():
    expected = {
        "valid_837p.edi": "837P",
        "valid_837i.edi": "837I",
        "valid_835.edi": "835",
        "valid_999.edi": "999",
        "valid_277ca.edi": "277CA",
        "valid_270.edi": "270",
        "valid_271.edi": "271",
        "valid_276.edi": "276",
        "valid_277.edi": "277",
        "valid_275.edi": "275",
    }

    for filename, transaction_type in expected.items():
        report = validate_x12_file(FIXTURES / filename)
        assert report.valid, f"{filename}: {report.errors}"
        assert report.transaction_type == transaction_type


def test_missing_claim_segment_is_actionable():
    report = validate_x12_file(FIXTURES / "invalid_837p_missing_clm.edi")

    assert report.valid is False
    assert report.transaction_type == "837P"
    assert "Missing required 837P segment CLM." in report.errors


def test_control_number_mismatches_are_actionable():
    report = validate_x12_file(FIXTURES / "invalid_control_numbers.edi")

    assert report.valid is False
    assert "ISA13 does not match IEA02 interchange control number." in report.errors
    assert "GS06 does not match GE02 functional group control number." in report.errors
    assert "ST02 does not match SE02 transaction set control number." in report.errors
    assert "SE01 declares 7 segments, but ST-to-SE count is 8." in report.errors


def test_empty_input_fails_cleanly():
    report = validate_x12_text("")

    assert report.valid is False
    assert report.transaction_type is None
    assert "No X12 segments found." in report.errors


def test_folder_summary_reports_validation_mix(capsys):
    with pytest.raises(SystemExit) as exit_info:
        main(["validate-folder", str(FIXTURES), "--summary"])

    assert exit_info.value.code == 1

    payload = json.loads(capsys.readouterr().out)
    fixture_count = len(list(FIXTURES.glob("*.edi")))

    assert payload["valid"] is False
    assert payload["file_count"] == fixture_count
    assert payload["valid_count"] == fixture_count - 2
    assert payload["invalid_count"] == 2
    assert payload["transaction_counts"]["837P"] >= 2
    assert any(
        "invalid_control_numbers.edi" in file_report["path"] and file_report["error_count"] >= 3
        for file_report in payload["files"]
    )


def test_public_proof_artifacts_show_coverage_and_failures(tmp_path):
    output_dir = tmp_path / "output_demo"

    result = proof_artifacts_run(FIXTURES, output_dir)

    assert result["file_count"] == len(list(FIXTURES.glob("*.edi")))
    assert result["valid_count"] == result["file_count"] - 2
    assert result["invalid_count"] == 2
    assert result["transaction_family_count"] == 10
    assert result["artifact_count"] == 2

    report_path = output_dir / "edi_validation_report.json"
    svg_path = output_dir / "edi_validation_coverage.svg"
    assert report_path.exists()
    assert svg_path.exists()

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["summary"]["transaction_counts"]["837P"] >= 2
    assert any(item["transaction_type"] == "275" and item["valid"] for item in report["coverage"])
    assert any(item["file"] == "invalid_control_numbers.edi" for item in report["invalid_files"])

    svg = svg_path.read_text(encoding="utf-8")
    assert "X12 files tested before the route goes live" in svg
    assert "837P" in svg
    assert "277CA" in svg
    assert "invalid_control_numbers.edi" in svg
    assert "without public PHI" in svg
