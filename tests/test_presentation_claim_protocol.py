"""Private ledger and audit boundaries; these are protocol tests, not model evals."""

from copy import deepcopy

import pytest
from on_knowledge.features.presentations.claims import parse_outline
from on_knowledge.features.presentations.errors import PresentationProtocolError, UnsupportedPresentation
from on_knowledge.features.presentations.review import review_facts


def evidence():
    return [
        {
            "id": "E1",
            "title": "Report",
            "quote": "Results have not yet been received. This is a receipt status.",
        },
        {"id": "E2", "title": "Meeting", "quote": "No changes were approved at this meeting."},
    ]


def draft():
    return {
        "claims": [
            {
                "id": "F1",
                "text": "Receipt status",
                "evidence": [{"evidence_id": "E1", "quote": "receipt status"}],
            },
            {
                "id": "F2",
                "text": "Results have not yet been received.",
                "evidence": [{"evidence_id": "E1", "quote": "Results have not yet been received."}],
            },
            {
                "id": "F3",
                "text": "No changes were approved at this meeting.",
                "evidence": [{"evidence_id": "E2", "quote": "No changes were approved at this meeting."}],
            },
        ],
        "slides": [{"layout": "bullets", "title_id": "F1", "bullet_ids": ["F2"], "note_ids": ["F2", "F3"]}],
    }


def verdict():
    return {
        "reviews": [
            {
                "claim_id": f"C{index}",
                "verdict": "supported",
                "support": fact["evidence"],
                "reason": "The cited text preserves this meaning.",
            }
            for index, fact in enumerate(draft()["claims"], 1)
        ]
    }


class Provider:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def complete(self, system, data):
        self.calls.append((system, deepcopy(data)))
        if isinstance(self.response, Exception):
            raise self.response
        return deepcopy(self.response)


def test_ledger_compiles_notes_from_reused_claims_and_preserves_each_support():
    raw, sources = draft(), evidence()
    before = deepcopy((raw, sources))
    facts, slides = parse_outline(raw, sources)
    assert facts == raw["claims"]
    assert slides[0].title == facts[0]["text"]
    assert slides[0].bullets == [facts[1]["text"]]
    assert slides[0].notes == facts[1]["text"] + "\n" + facts[2]["text"]
    assert slides[0].evidence_ids == ["E1", "E2"]
    assert (raw, sources) == before


@pytest.mark.parametrize(
    "path,value",
    [
        (("claims",), []),
        (("claims", 0, "id"), "C1"),
        (("claims", 1, "id"), "F1"),
        (("claims", 1, "text"), "x" * 221),
        (("claims", 0, "text"), "x" * 161),
        (("claims", 1, "text"), " "),
        (("claims", 1, "evidence"), []),
        (("claims", 1, "evidence", 0, "evidence_id"), "E99"),
        (("claims", 1, "evidence", 0, "quote"), "Results do not exist."),
        (("claims", 1, "evidence", 0, "quote"), " "),
        (("claims", 1, "evidence", 0, "quote"), True),
        (("claims", 1, "extra"), "ignored instructions"),
        (("slides",), []),
        (("slides", 0, "title_id"), "F99"),
        (("slides", 0, "bullet_ids"), ["F2"] * 6),
        (("slides", 0, "note_ids"), ["F2"] * 6),
        (("slides", 0, "note_ids"), ["F2"]),  # F3 cannot disappear silently.
        (("slides", 0, "note_ids"), ["F2", "F99"]),
        (("slides", 0, "notes"), "A second invented paraphrase."),
        (("slides", 0, "layout"), "title"),  # Title/section slides cannot conceal bullets.
    ],
)
def test_invalid_writer_contract_fails_before_compilation(path, value):
    raw = draft()
    item = raw
    for key in path[:-1]:
        item = item[key]
    item[path[-1]] = value
    with pytest.raises(PresentationProtocolError):
        parse_outline(raw, evidence())


@pytest.mark.parametrize("field,count", [("claims", 61), ("slides", 13)])
def test_draft_count_bounds_fail_without_truncation(field, count):
    raw = draft()
    raw[field] = [deepcopy(raw[field][0]) for _ in range(count)]
    with pytest.raises(PresentationProtocolError):
        parse_outline(raw, evidence())


def test_maximum_fact_and_slide_counts_are_supported_without_silent_drops():
    raw = {"claims": [], "slides": []}
    for index in range(60):
        raw["claims"].append(
            {
                "id": f"F{index + 1}",
                "text": "x" * (160 if index % 5 == 0 else 220),
                "evidence": [{"evidence_id": "E1", "quote": "receipt status"}],
            }
        )
    for index in range(12):
        ids = [f"F{index * 5 + offset + 1}" for offset in range(5)]
        raw["slides"].append({"layout": "bullets", "title_id": ids[0], "bullet_ids": ids, "note_ids": ids})
    facts, slides = parse_outline(raw, evidence())
    assert len(facts) == 60 and len(slides) == 12
    assert slides[-1].notes == "\n".join(item["text"] for item in facts[-5:])


def test_reviewer_receives_full_cited_context_not_only_highlights_or_other_sources():
    facts = draft()["claims"]
    facts[0]["id"] = "F53"  # Server C IDs do not trust writer numbering.
    provider = Provider(verdict())
    before = deepcopy((facts, evidence()))
    assert review_facts(provider, "Summarize.", facts, evidence()) is None
    assert len(provider.calls) == 1
    claims = provider.calls[0][1]["claims"]
    assert [item["claim_id"] for item in claims] == ["C1", "C2", "C3"]
    assert claims[0]["anchors"] == facts[0]["evidence"]
    assert claims[0]["evidence_ids"] == ["E1"]
    assert claims[1]["anchors"] == facts[1]["evidence"]  # A partial span stays highlighted.
    assert claims[2]["evidence_ids"] == ["E2"]
    assert claims[2]["anchors"] == []  # The entire passage is already supplied once.
    assert provider.calls[0][1]["evidence"] == evidence()
    assert all("evidence" not in claim for claim in claims)
    assert (facts, evidence()) == before


@pytest.mark.parametrize(
    "response",
    [
        {},
        {"reviews": []},
        {"supported_claim_ids": ["C1", "C2", "C3"]},
        {"reviews": [verdict()["reviews"][0]] * 3},
        {"reviews": verdict()["reviews"], "rewritten_text": "Something else"},
    ],
)
def test_malformed_audit_fails_once_without_repair(response):
    provider = Provider(response)
    with pytest.raises(PresentationProtocolError):
        review_facts(provider, "", draft()["claims"], evidence())
    assert len(provider.calls) == 1


@pytest.mark.parametrize(
    "key,value",
    [
        ("claim_id", "F1"),
        ("claim_id", "C99"),
        ("verdict", True),
        ("verdict", "accepted"),
        ("reason", " "),
        ("reason", "x" * 601),
        ("support", []),
        ("support", [{"evidence_id": "E2", "quote": evidence()[1]["quote"]}]),
        ("support", [{"evidence_id": "E1", "quote": "Made up quote"}]),
    ],
)
def test_acceptance_cannot_omit_reason_or_launder_unrelated_support(key, value):
    response = verdict()
    response["reviews"][0][key] = value
    provider = Provider(response)
    with pytest.raises(PresentationProtocolError):
        review_facts(provider, "", draft()["claims"], evidence())
    assert len(provider.calls) == 1


@pytest.mark.parametrize("decision", ["unsupported", "uncertain"])
def test_valid_negative_decision_is_distinct_from_malformed_and_is_final(decision):
    response = verdict()
    response["reviews"][1].update(
        verdict=decision, support=[], reason="The source concerns receipt, not existence."
    )
    provider = Provider(response)
    with pytest.raises(UnsupportedPresentation) as caught:
        review_facts(provider, "", draft()["claims"], evidence())
    assert caught.value.rejected == ("C2",)
    assert len(provider.calls) == 1


def test_provider_failure_is_not_retried_or_mislabeled_semantic_rejection():
    provider = Provider(TimeoutError("transport deadline"))
    with pytest.raises(TimeoutError, match="transport deadline"):
        review_facts(provider, "", draft()["claims"], evidence())
    assert len(provider.calls) == 1


@pytest.mark.parametrize("facts", [[], draft()["claims"] * 21, [{"id": "F1"}]])
def test_invalid_audit_input_makes_no_provider_call(facts):
    provider = Provider(verdict())
    with pytest.raises(PresentationProtocolError):
        review_facts(provider, "", facts, evidence())
    assert provider.calls == []
