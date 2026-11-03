from io import BytesIO
from xml.etree import ElementTree

import pytest
from on_knowledge.features.presentations.exports import export_presentation, presentation_preview
from on_knowledge.features.presentations.layout import LayoutOverflow
from on_knowledge.features.presentations.schemas import Presentation
from pptx import Presentation as PowerPoint
from pypdf import PdfReader


@pytest.fixture
def citations():
    return [
        {
            "id": "passage-1",
            "source_id": "source-1",
            "title": "Project / Проект",
            "version": "version-2026-11-03",
            "quote": "The launch is planned. Запуск запланирован.",
            "location": {"page": 3, "element": 0, "offset_start": 0, "offset_end": 49},
        }
    ]


def deck(language="en", **updates):
    data = {
        "title": "Project / Проект",
        "stage": "slides",
        "revision": 1,
        "language": language,
        "template": "light",
        "slides": [
            {
                "id": "slide-1",
                "layout": "bullets",
                "title": "Plan / План",
                "bullets": ["The launch is planned.", "Запуск запланирован."],
                "notes": "A plan is not a completed event. План ещё не выполнен.",
                "evidence_ids": ["passage-1"],
                "review_state": "generated",
            }
        ],
    }
    data.update(updates)
    return Presentation.model_validate(data)


@pytest.mark.parametrize("language", ["en", "ru"])
@pytest.mark.parametrize("template", ["light", "dark"])
def test_pdf_and_pptx_keep_editable_text_notes_and_evidence(citations, language, template):
    document = deck(language, template=template)
    pdf = PdfReader(BytesIO(export_presentation(document, citations, "pdf")))
    text = "\n".join(page.extract_text() for page in pdf.pages)
    for expected in ["Запуск запланирован.", "План ещё не выполнен.", "version-2026-11-03", "source-1"]:
        assert expected in text
    pptx = PowerPoint(BytesIO(export_presentation(document, citations, "pptx")))
    slide = pptx.slides[0]
    editable = "\n".join(shape.text for shape in slide.shapes if shape.has_text_frame)
    assert "Запуск запланирован." in editable
    assert "Plan / План" in editable
    assert "План ещё не выполнен." in slide.notes_slide.notes_text_frame.text
    assert "version-2026-11-03" in slide.notes_slide.notes_text_frame.text
    assert len(pptx.slides) == len(pdf.pages)
    assert not any(shape.shape_type == 13 for shape in slide.shapes)  # no rasterized slide
    # Embedded TrueType fonts make the PDF independent of the machine's font installation.
    assert any(
        "/FontFile2" in str(font.get_object().get("/FontDescriptor", {}))
        for page in pdf.pages
        for font in page["/Resources"]["/Font"].values()
    )


def test_preview_escapes_untrusted_text_and_has_the_same_pages(citations):
    document = deck(title="<script>alert('x')</script> & Пример")
    document.slides[0].title = document.title
    pages = presentation_preview(document, citations)
    assert len(pages) == len(PdfReader(BytesIO(export_presentation(document, citations, "pdf"))).pages)
    for svg in pages:
        root = ElementTree.fromstring(svg)
        assert root.attrib["viewBox"] == "0 0 960 540"
        assert not root.findall(".//{http://www.w3.org/2000/svg}script")
        assert "https://" not in svg
    assert "&lt;script&gt;" in pages[0]
    assert "data:font/ttf;base64," in pages[0]


def test_dense_content_rejects_overflow_instead_of_clipping(citations):
    document = deck()
    document.slides[0].title = "W" * 160
    document.slides[0].bullets = ["W" * 220] * 5
    with pytest.raises(LayoutOverflow):
        export_presentation(document, citations, "pdf")
    with pytest.raises(LayoutOverflow):
        export_presentation(document, citations, "pptx")


def test_long_notes_and_quotes_paginate_without_data_loss(citations):
    document = deck()
    document.slides[0].notes = "Beginning " + "длинное примечание " * 55 + "END-NOTES"
    citations[0]["quote"] = "Exact evidence " * 250 + "END-QUOTE"
    pdf = PdfReader(BytesIO(export_presentation(document, citations, "pdf")))
    text = "\n".join(page.extract_text() for page in pdf.pages)
    assert "END-NOTES" in text and "END-QUOTE" in text
    assert len(pdf.pages) >= 4


def test_export_requires_completed_deck_and_known_evidence(citations):
    with pytest.raises(ValueError, match="outline"):
        export_presentation(deck(stage="outline"), citations, "pptx")
    with pytest.raises(ValueError, match="citation"):
        export_presentation(deck(), [], "pdf")
    with pytest.raises(ValueError, match="format"):
        export_presentation(deck(), citations, "exe")


def test_export_is_repeatable_and_does_not_mutate_the_document(citations):
    document = deck()
    before = document.model_dump()
    first = export_presentation(document, citations, "pdf")
    second = export_presentation(document, citations, "pdf")
    assert first == second
    assert document.model_dump() == before
