from __future__ import annotations

ENVELOPE_SEGMENTS = ("ISA", "GS", "ST", "SE", "GE", "IEA")

TRANSACTION_RULES: dict[str, tuple[str, ...]] = {
    "837P": ("BHT", "NM1", "CLM", "LX", "SV1"),
    "837I": ("BHT", "NM1", "CLM", "LX", "SV2"),
    "835": ("BPR", "TRN", "CLP"),
    "999": ("AK1", "AK2", "IK5", "AK9"),
    "277CA": ("BHT", "HL", "TRN", "STC"),
    "270": ("BHT", "HL", "NM1", "EQ"),
    "271": ("BHT", "HL", "NM1", "EB"),
    "276": ("BHT", "HL", "NM1", "TRN"),
    "277": ("BHT", "HL", "NM1", "TRN", "STC"),
    "275": ("BGN", "NM1"),
}


def classify_transaction(st_code: str, segments_by_tag: dict[str, int]) -> str:
    """Return a RevCycleMGMT transaction label from ST01 plus available segments."""
    if st_code == "837":
        return "837I" if segments_by_tag.get("SV2", 0) else "837P"
    if st_code == "277":
        return "277CA" if segments_by_tag.get("STC", 0) and not segments_by_tag.get("NM1", 0) else "277"
    return st_code
