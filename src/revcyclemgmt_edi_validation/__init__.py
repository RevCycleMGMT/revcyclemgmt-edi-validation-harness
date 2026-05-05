"""Synthetic EDI/X12 validation harness for RevCycleMGMT."""

from .validator import ValidationReport, validate_x12_text

__all__ = ["ValidationReport", "validate_x12_text"]
