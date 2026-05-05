from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Segment:
    tag: str
    elements: list[str]
    ordinal: int

    def value(self, index: int, default: str = "") -> str:
        return self.elements[index] if len(self.elements) > index else default


def parse_x12_segments(x12_text: str) -> list[Segment]:
    """Parse X12 text into segments using the standard demo delimiters."""
    cleaned = x12_text.replace("\n", "").replace("\r", "").strip()
    raw_segments = [part.strip() for part in cleaned.split("~") if part.strip()]
    segments: list[Segment] = []
    for ordinal, raw in enumerate(raw_segments, start=1):
        parts = raw.split("*")
        tag = parts[0].strip().upper()
        elements = [part.strip() for part in parts[1:]]
        segments.append(Segment(tag=tag, elements=elements, ordinal=ordinal))
    return segments


def first_segment(segments: list[Segment], tag: str) -> Segment | None:
    tag = tag.upper()
    return next((segment for segment in segments if segment.tag == tag), None)


def all_segments(segments: list[Segment], tag: str) -> list[Segment]:
    tag = tag.upper()
    return [segment for segment in segments if segment.tag == tag]
