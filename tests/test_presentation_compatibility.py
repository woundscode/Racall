"""The external-render gate must reject plausible damaged conversion results."""

import json
from copy import deepcopy
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest
from on_knowledge.features.presentations.exports import export_presentation
from pptx import Presentation as PowerPoint

from scripts.presentation_compatibility.checks import verify_bbox, verify_roundtrip
from scripts.presentation_compatibility.fixtures import cases
from scripts.presentation_compatibility.runner import run


def bbox_page(words, width=960, height=540):
    root = ET.Element("html")
    page = ET.SubElement(root, "page", width=str(width), height=str(height))
    for text, x, y in words:
        ET.SubElement(page, "word", xMin=str(x), yMin=str(y), xMax=str(x + 30), yMax=str(y + 12)).text = text
    return root


def test_bbox_accepts_unicode_and_order_independent_text():
    root = bbox_page([("План", 60, 80), ("fi", 120, 80)])
    assert verify_bbox(root, [["ﬁ План"]]) == {"pages": 1, "words": 2}


@pytest.mark.parametrize("damage", ["missing", "extra", "outside", "overlap", "page-size", "page-count"])
def test_bbox_rejects_missing_text_clipping_and_overlap(damage):
    root = bbox_page([("Plan", 60, 80), ("ready", 120, 80)])
    page = root.find("page")
    if damage == "missing":
        page.remove(page[-1])
    elif damage == "extra":
        page[-1].text = "changed"
    elif damage == "outside":
        page[-1].set("xMax", "970")
    elif damage == "overlap":
        page[-1].set("xMin", "70")
    elif damage == "page-size":
        page.set("height", "500")
    else:
        root.append(deepcopy(page))
    with pytest.raises(AssertionError):
        verify_bbox(root, [["Plan ready"]])


def test_roundtrip_checks_real_editable_text_and_notes():
    case = cases()[0]
    original = PowerPoint(BytesIO(export_presentation(case.document, case.citations, "pptx")))
    assert verify_roundtrip(original, original)["pages"] == len(original.slides)


@pytest.mark.parametrize("damage", ["text", "notes", "dimensions", "removed-slide"])
def test_roundtrip_rejects_data_loss(damage):
    case = cases()[0]
    raw = export_presentation(case.document, case.citations, "pptx")
    original, changed = PowerPoint(BytesIO(raw)), PowerPoint(BytesIO(raw))
    if damage == "text":
        next(shape for shape in changed.slides[0].shapes if shape.has_text_frame and shape.text).text = "Lost"
    elif damage == "notes":
        changed.slides[0].notes_slide.notes_text_frame.text = "Lost notes"
    elif damage == "dimensions":
        changed.slide_width -= 100000
    else:
        changed.slides._sldIdLst.remove(changed.slides._sldIdLst[-1])
    with pytest.raises(AssertionError):
        verify_roundtrip(original, changed)


def test_compatibility_cases_cover_languages_themes_and_schema_limits():
    fixtures = cases()
    assert {(item.document.language, item.document.template) for item in fixtures} == {
        (language, template) for language in ("en", "ru") for template in ("light", "dark")
    }
    for case in fixtures:
        deck = PowerPoint(BytesIO(export_presentation(case.document, case.citations, "pptx")))
        assert len(deck.slides) > len(case.document.slides), "Notes and evidence appendices must be exercised"
    bounded = [item for item in fixtures if item.name.startswith("limits-")]
    assert len(bounded) == 2
    for case in bounded:
        slide = case.document.slides[0]
        assert len(slide.title) == 160 and len(slide.bullets[0]) == 220 and len(slide.notes) == 1200


def test_missing_renderer_records_failure_and_preserves_existing_evidence(tmp_path, monkeypatch):
    monkeypatch.setattr("scripts.presentation_compatibility.runner.shutil.which", lambda _name: None)
    with pytest.raises(AssertionError, match="Required independent renderer"):
        run(tmp_path, Path(__file__).resolve().parents[1])
    evidence = (tmp_path / "result.json").read_bytes()
    result = json.loads(evidence)
    assert not result["passed"] and result["cases"] == []
    assert "Required independent renderer" in result["error"]
    assert result["visual_review"] == "pending" and result["microsoft_powerpoint"] == "not tested"
    with pytest.raises(AssertionError, match="fresh evidence directory"):
        run(tmp_path, tmp_path)
    assert (tmp_path / "result.json").read_bytes() == evidence
