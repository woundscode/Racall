"""Fenced source blocks retain internal qualifications and exact note ranges."""

import pytest
from on_knowledge.documents.text import text_elements
from on_knowledge.features.context.evidence import bounded_evidence, note_passages


@pytest.mark.parametrize("marker", ["```", "~~~"])
@pytest.mark.parametrize("indent", ["", " ", "  ", "   "])
def test_fences_allow_up_to_three_spaces_and_keep_blank_lines(marker, indent):
    body = f"{indent}{marker}text\nAn apparent result.\n\nNot an established fact.\n{indent}{marker}"
    elements = text_elements(body, page=2)
    assert len(elements) == 1
    block = elements[0]
    assert (block.type, block.text, block.page) == ("code", body, 2)
    assert (block.line_start, block.line_end) == (1, 5)


@pytest.mark.parametrize("inner", ["```", "~~~~", "````text", "    ````"])
def test_closer_requires_same_marker_length_and_only_trailing_whitespace(inner):
    body = f"````text\nA first line.\n{inner}\n\nStill inside the original block.\n````"
    elements = text_elements(body)
    assert [(block.type, block.text) for block in elements] == [("code", body)]
    assert elements[0].line_end == 6


@pytest.mark.parametrize("marker", ["`", "~"])
def test_longer_closer_with_spaces_or_tabs_ends_the_block(marker):
    code = f"{marker * 3}text\nResult\n  {marker * 5} \t"
    body = code + "\n\nFollowing paragraph."
    elements = text_elements(body)
    assert [(block.type, block.text) for block in elements] == [
        ("code", code),
        ("paragraph", "Following paragraph."),
    ]
    assert (elements[1].line_start, elements[1].line_end) == (5, 5)


def test_backtick_in_opening_info_is_not_a_fence():
    body = "```language`invalid\nFirst paragraph.\n\nSecond paragraph."
    elements = text_elements(body)
    assert [(block.type, block.text) for block in elements] == [
        ("paragraph", "```language`invalid\nFirst paragraph."),
        ("paragraph", "Second paragraph."),
    ]


def test_tilde_opening_info_may_contain_backticks():
    body = "~~~language`allowed\nA line\n\nAnother line\n~~~"
    assert [(block.type, block.text) for block in text_elements(body)] == [("code", body)]


def test_four_space_opening_is_not_a_fence_or_a_new_markdown_feature():
    body = "    ```text\nFirst paragraph.\n\nSecond paragraph."
    assert [block.type for block in text_elements(body)] == ["paragraph", "paragraph"]


@pytest.mark.parametrize("marker", ["```", "~~~"])
def test_unclosed_fence_keeps_every_following_line(marker):
    body = f"{marker}text\nFirst line\n\n# This is code, not a heading\nLast line"
    assert [(block.type, block.text) for block in text_elements(body)] == [("code", body)]


def test_paragraphs_headings_and_section_metadata_keep_existing_behavior():
    body = "Intro\n\n## Section\nFirst line\nSecond line\n\n```\n# Code\n```\n\nAfter code."
    elements = text_elements(body)
    assert [(block.type, block.section, block.line_start, block.line_end) for block in elements] == [
        ("paragraph", "", 1, 1),
        ("heading", "Section", 3, 3),
        ("paragraph", "Section", 4, 5),
        ("code", "Section", 7, 9),
        ("paragraph", "Section", 11, 11),
    ]


@pytest.mark.parametrize("marker", ["   ```", "~~~"])
def test_note_crlf_ranges_and_budget_keep_whole_fenced_blocks(marker):
    block = f"{marker}text\r\nAllowed when authorized.\r\n\r\nNot otherwise.\r\n{marker}"
    body = "\r\n" + block + "\r\n\r\nFinal paragraph."
    note = {"id": "note", "revision": "v1", "title": "Example", "body": body}
    passages = note_passages("notebook", note, size=20)
    assert [item["quote"] for item in passages] == [block, "Final paragraph."]
    location = passages[0]["location"]
    assert (location["line_start"], location["line_end"]) == (2, 6)
    assert body[location["offset_start"] : location["offset_end"]] == block
    selected, truncated = bounded_evidence(passages, max_chars=len(block) - 1)
    assert selected == [passages[1]] and truncated is True
