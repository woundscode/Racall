"""Verify independently rendered text geometry and office round-trip editability."""

import math
import unicodedata
from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from xml.etree import ElementTree as ET

from on_knowledge.features.presentations.layout import HEIGHT, WIDTH
from pptx.enum.shapes import MSO_SHAPE_TYPE


def canonical(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).split())


def tokens(lines) -> Counter:
    return Counter(word for line in lines for word in canonical(line).split())


def elements(root: ET.Element, tag: str):
    return (item for item in root.iter() if item.tag.rsplit("}", 1)[-1] == tag)


@dataclass(frozen=True)
class Word:
    text: str
    left: float
    top: float
    right: float
    bottom: float


def words(page: ET.Element) -> list[Word]:
    return [
        Word("".join(item.itertext()), *(float(item.attrib[key]) for key in ("xMin", "yMin", "xMax", "yMax")))
        for item in elements(page, "word")
    ]


def verify_geometry(items: list[Word], label: str):
    for word in items:
        box = (word.left, word.top, word.right, word.bottom)
        assert all(math.isfinite(value) for value in box), f"{label}: non-finite word geometry"
        assert -0.5 <= word.left < word.right <= WIDTH + 0.5, f"{label}: horizontal clipping: {word}"
        assert -0.5 <= word.top < word.bottom <= HEIGHT + 0.5, f"{label}: vertical clipping: {word}"
    # Compare actual glyph-word rectangles, not text-box extents (which can
    # legitimately contain padding). One-point tolerance handles PDF rounding.
    for first, second in combinations(items, 2):
        overlap_x = min(first.right, second.right) - max(first.left, second.left)
        overlap_y = min(first.bottom, second.bottom) - max(first.top, second.top)
        assert min(overlap_x, overlap_y) <= 1.0, (
            f"{label}: overlapping words: {first.text!r}, {second.text!r}"
        )


def verify_bbox(root: ET.Element, expected_pages: list[list[str]]) -> dict:
    pages = list(elements(root, "page"))
    assert len(pages) == len(expected_pages), "Rendered page count differs from the exported deck"
    count = 0
    for index, (page, expected) in enumerate(zip(pages, expected_pages, strict=True), 1):
        label = f"Page {index}"
        assert abs(float(page.attrib["width"]) - WIDTH) <= 0.5, f"{label}: width changed"
        assert abs(float(page.attrib["height"]) - HEIGHT) <= 0.5, f"{label}: height changed"
        actual = words(page)
        wanted, found = tokens(expected), tokens(item.text for item in actual)
        assert wanted == found, f"{label}: text changed; missing={wanted - found}, extra={found - wanted}"
        verify_geometry(actual, label)
        count += len(actual)
    return {"pages": len(pages), "words": count}


def text_shapes(shapes):
    for shape in shapes:
        assert shape.shape_type != MSO_SHAPE_TYPE.PICTURE, "Office round-trip rasterized slide content"
        if shape.has_text_frame and canonical(shape.text):
            yield canonical(shape.text)
        if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
            yield from text_shapes(shape.shapes)


def signature(deck):
    return [
        {
            "text": Counter(text_shapes(slide.shapes)),
            "notes": canonical(slide.notes_slide.notes_text_frame.text),
        }
        for slide in deck.slides
    ]


def verify_roundtrip(original, converted) -> dict:
    assert abs(original.slide_width - converted.slide_width) < 127, "Office round-trip changed width"
    assert abs(original.slide_height - converted.slide_height) < 127, "Office round-trip changed height"
    assert signature(original) == signature(converted), "Office round-trip changed editable text or notes"
    return {"pages": len(converted.slides), "editable_text_and_notes_preserved": True}
