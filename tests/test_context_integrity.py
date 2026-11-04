"""Context budgets must not turn a qualified passage into a stronger quotation."""

import copy

import pytest
from on_knowledge.features.context.evidence import bounded_evidence, note_passages


def passage(text, key="source"):
    return {
        "id": key,
        "quote": text,
        "location": {"element": 0, "offset_start": 0, "offset_end": len(text)},
    }


@pytest.mark.parametrize(
    "text,cut",
    [
        ("Response time rose after the update. The cause has not been established.", 35),
        ("Открытие запланировано на май, если испытания завершатся успешно.", 29),
    ],
)
def test_budget_omits_a_whole_passage_instead_of_removing_its_qualification(text, cut):
    evidence = [passage(text)]
    original = copy.deepcopy(evidence)
    selected, truncated = bounded_evidence(evidence, max_chars=cut)
    assert selected == []
    assert truncated is True
    assert evidence == original


def test_budget_can_include_later_whole_passages_without_reusing_a_cut_citation_id():
    first = passage("One intact block.", "first")
    too_long = passage("A second block with an essential qualification at its end.", "long")
    last = passage("Final block.", "last")
    selected, truncated = bounded_evidence(
        [first, too_long, last], max_chars=len(first["quote"]) + len(last["quote"])
    )
    assert selected == [first, last]
    assert truncated is True
    assert bounded_evidence([first, last], max_chars=sum(len(p["quote"]) for p in (first, last))) == (
        [first, last],
        False,
    )


@pytest.mark.parametrize("newline", ["\n", "\r\n"])
def test_note_preserves_complete_paragraphs_offsets_and_line_locations(newline):
    first = "Measurements increased after the update." + newline + "The cause is unknown."
    second = "Результаты пока не получены; это не означает, что их нет."
    body = first + newline * 2 + second
    note = {"id": "note-id", "revision": "v1", "title": "Results", "body": body}
    chunks = note_passages("notebook", note, size=35)
    assert len(chunks) == 2
    assert chunks[0]["quote"].rstrip("\r\n") == first
    assert chunks[1]["quote"] == second
    assert chunks[0]["location"]["line_start"] == 1
    assert chunks[0]["location"]["line_end"] == 2
    assert chunks[1]["location"]["line_start"] == 4
    assert chunks[1]["location"]["line_end"] == 4
    for chunk in chunks:
        location = chunk["location"]
        assert body[location["offset_start"] : location["offset_end"]] == chunk["quote"]
    assert note_passages("notebook", note, size=35) == chunks
    changed = note_passages("notebook", {**note, "revision": "v2"}, size=35)
    assert {p["id"] for p in changed}.isdisjoint(p["id"] for p in chunks)


def test_note_keeps_fenced_blocks_with_internal_blank_lines_intact():
    body = "```text\nAn apparent result\n\nNot an established fact\n```"
    chunks = note_passages(
        "notebook", {"id": "note", "revision": "v1", "title": "Code", "body": body}, size=20
    )
    assert [p["quote"] for p in chunks] == [body]


def test_oversize_note_paragraph_is_neither_cut_nor_sent_past_the_budget():
    body = "x " * 13000 + "This report is conditional, not final."
    note = {"id": "note", "revision": "v1", "title": "Large", "body": body}
    chunks = note_passages("notebook", note)
    assert len(chunks) == 1 and chunks[0]["quote"] == body
    assert bounded_evidence(chunks) == ([], True)


def test_note_can_pack_short_paragraphs_without_losing_blank_lines():
    body = "First paragraph.\n\nSecond paragraph."
    note = {"id": "note", "revision": "v1", "title": "Small", "body": body}
    assert [p["quote"] for p in note_passages("notebook", note)] == [body]
