"""Offline recorded-output replay; no new model inference or quality claim."""

import copy
import json
import re
from io import BytesIO
from pathlib import Path

import pytest
from on_knowledge.features.presentations.assembly import (
    approval_marker,
    assemble_presentation,
    outline_snapshot,
)
from on_knowledge.features.presentations.citation_markers import (
    canonical_markers,
    canonicalize_generated_citations,
)
from on_knowledge.features.presentations.exports import export_presentation
from on_knowledge.features.presentations.generator import generate_presentation
from on_knowledge.features.presentations.schemas import Presentation, Slide
from on_knowledge.features.studio.generator import UnverifiedMaterial
from pptx import Presentation as PowerPoint
from presentation_protocol_fixtures import audit_response, ledger_from_slides
from pypdf import PdfReader


def test_recorded_en_writer_markers_are_canonical_in_outline_assembly_and_exports(monkeypatch):
    path = Path(__file__).parents[1] / "evals/release04/regressions/inline-evidence-markers.json"
    recorded = json.loads(path.read_text(encoding="utf-8"))
    before = copy.deepcopy(recorded)
    calls = []

    class ReplayProvider:
        def complete(self, system, data):
            calls.append(copy.deepcopy(data))
            if "claims" in data:
                return audit_response(data)
            return ledger_from_slides(recorded["writer_response"], recorded["evidence"])

    monkeypatch.setattr(
        "on_knowledge.features.presentations.generator.completion_provider", lambda _: ReplayProvider()
    )
    evidence = [{**item, "id": "canonical-" + item["id"], "version": "v1"} for item in recorded["evidence"]]
    generated = generate_presentation(
        {
            "kind": "presentation_outline",
            "language": "en",
            "title": "Station review",
            "question": recorded["question"],
        },
        evidence,
        {},
        lambda: None,
        lambda *args: None,
    )
    assert len(calls) == 2

    assert any("[E1]" in claim["text"] for claim in calls[1]["claims"])
    assert "[E1]" not in generated["body"]
    assert "[E1, E2]" not in generated["body"]
    texts = [claim["text"] for claim in generated["answer"]["claims"]]
    assert all(not re.search(r"\[E\d", text) for text in texts)
    assert any("[1] [2]" in text for text in texts)
    assert generated["answer"]["citations"][0]["id"] == "canonical-E1"
    assert generated["answer"]["citations"][1]["id"] == "canonical-E2"
    assert [item["quote"] for item in generated["answer"]["citations"]] == [
        item["quote"] for item in evidence
    ]
    assert recorded == before

    def forbidden(*args, **kwargs):
        raise AssertionError("Assembly and exports must not invoke a provider")

    monkeypatch.setattr("on_knowledge.features.presentations.generator.completion_provider", forbidden)
    material = {"id": "recorded-outline", "context": {"sources": [], "notes": []}, **generated}
    snapshot = outline_snapshot(material)
    deck = assemble_presentation(
        {
            "_outline_snapshot": snapshot,
            "assembly": approval_marker(snapshot),
            "context": material["context"],
            "outline_id": material["id"],
            "outline_revision": 1,
        }
    )
    assert deck["presentation"]["slides"] == generated["presentation"]["slides"]
    document = Presentation.model_validate(deck["presentation"])
    citations = deck["answer"]["citations"]
    pdf = PdfReader(BytesIO(export_presentation(document, citations, "pdf")))
    pdf_text = "\n".join(page.extract_text() for page in pdf.pages)
    pptx = PowerPoint(BytesIO(export_presentation(document, citations, "pptx")))
    pptx_text = "\n".join(
        [shape.text for slide in pptx.slides for shape in slide.shapes if shape.has_text_frame]
        + [slide.notes_slide.notes_text_frame.text for slide in pptx.slides]
    )
    for text in (pdf_text, pptx_text):
        assert "[E1]" not in text and "[E1, E2]" not in text
        assert "[1] [2]" in text
    assert len(calls) == 2


@pytest.mark.parametrize(
    "text, expected",
    [
        ("Plan [E1]", "Plan [2]"),
        ("План [E2]", "План [1]"),
        ("[E2] then [E1,E2] and [E1, E1]", "[1] then [2] [1] and [2] [2]"),
        ("[ E1,\tE2 ]", "[2] [1]"),
        ("[Appendix E1] [E1, note] [E1, 2]", "[Appendix E1] [E1, note] [E1, 2]"),
        ("[1] E1 is an electrode", "[1] E1 is an electrode"),
        (r"\[E1] [[E2]]", r"\[E1] [[E2]]"),
    ],
)
def test_only_complete_label_groups_use_actual_citation_numbers(text, expected):
    assert canonical_markers(text, {"E1": 2, "E2": 1}, {"E1", "E2"}) == expected


@pytest.mark.parametrize(
    "text, allowed",
    [
        ("[E999]", {"E1", "E999"}),
        ("[E1, E999]", {"E1"}),
        ("[E0]", {"E1"}),
        ("[E01]", {"E1"}),
        ("[E2]", {"E1"}),
    ],
)
def test_unknown_or_undeclared_inline_labels_are_never_assigned_numbers(text, allowed):
    with pytest.raises(ValueError, match="declared on its slide"):
        canonical_markers(text, {"E1": 2, "E2": 1}, allowed)


def test_slide_formatter_preserves_edits_and_citation_quotes_without_mutation():
    generated = Slide(
        id="generated",
        title="Title [E1]",
        bullets=["Point [E2]"],
        notes="Notes [E1, E2]",
        evidence_ids=["source-b", "source-a"],
    )
    edited = Slide(id="edited", title="Keep [E999]", notes="My [E1] text", review_state="edited")
    citations = [
        {"id": "source-b", "number": 1, "quote": "Literal [E2] source quote"},
        {"id": "source-a", "number": 2, "quote": "Literal [E1] source quote"},
    ]
    before = copy.deepcopy((generated, edited, citations))
    result = canonicalize_generated_citations(
        [generated, edited],
        {"E1": {"id": "source-a"}, "E2": {"id": "source-b"}},
        citations,
    )
    assert result[0].title == "Title [2]" and result[0].bullets == ["Point [1]"]
    assert result[0].notes == "Notes [2] [1]"
    assert result[0].evidence_ids == generated.evidence_ids
    assert result[1] == edited
    assert (generated, edited, citations) == before


@pytest.mark.parametrize("marker", ["[E999]", "[E2]"])
def test_real_generator_rejects_unknown_or_other_slide_citation_after_critic(monkeypatch, marker):
    calls = []

    class Provider:
        def complete(self, system, data):
            calls.append(data)
            if "claims" in data:
                return audit_response(data)
            raw = {
                "slides": [
                    {
                        "layout": "bullets",
                        "title": "Plan",
                        "bullets": ["Planned event " + marker],
                        "notes": "",
                        "evidence_ids": ["E1"],
                    }
                ]
            }
            return ledger_from_slides(raw, data["evidence"])

    monkeypatch.setattr(
        "on_knowledge.features.presentations.generator.completion_provider", lambda _: Provider()
    )
    with pytest.raises(UnverifiedMaterial):
        generate_presentation(
            {"kind": "presentation_outline", "language": "en", "title": "User title [E1]", "question": ""},
            [
                {"id": "one", "title": "One", "quote": "Planned event"},
                {"id": "two", "title": "Two", "quote": "Other event"},
            ],
            {},
            lambda: None,
            lambda *args: None,
        )
    assert len(calls) == 2
