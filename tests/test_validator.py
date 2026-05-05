from pathlib import Path

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
