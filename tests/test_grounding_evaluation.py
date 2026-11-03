"""A rejected batch cannot hide false accepts or an always-rejecting reviewer."""

import pytest

from scripts.evaluate_grounding04 import evaluate_case, score_review


def verdicts(*values):
    return {"reviews": [{"claim_id": f"C{i}", "verdict": v} for i, v in enumerate(values, 1)]}


def test_scores_both_positive_and_negative_controls():
    correct = score_review(verdicts("supported", "unsupported", "uncertain"), ["C1"], 3)
    assert correct["passed"] and not correct["false_acceptances"] and not correct["false_rejections"]
    all_yes = score_review(verdicts("supported", "supported"), ["C1"], 2)
    assert not all_yes["passed"] and all_yes["false_acceptances"] == ["C2"]
    all_no = score_review(verdicts("unsupported", "uncertain"), ["C1"], 2)
    assert not all_no["passed"] and all_no["false_rejections"] == ["C1"]


@pytest.mark.parametrize(
    "raw",
    [
        None,
        {},
        {"reviews": []},
        {"reviews": [None]},
        verdicts("yes"),
        {"reviews": [{"claim_id": "E1", "verdict": "supported"}]},
    ],
)
def test_missing_or_invalid_verdict_cannot_be_a_pass(raw):
    result = score_review(raw, ["C1"], 1)
    assert not result["passed"] and result["unscorable"]


def test_duplicate_verdict_cannot_replace_a_missing_claim():
    raw = {"reviews": [{"claim_id": "C1", "verdict": "supported"}] * 2}
    assert score_review(raw, ["C1"], 2)["unscorable"]


def test_invalid_gold_stops_the_evaluation():
    with pytest.raises(ValueError, match="Gold labels"):
        score_review(verdicts("supported"), ["C2"], 1)


def test_preflight_rejection_cannot_reuse_the_previous_case_response(monkeypatch):
    from types import SimpleNamespace

    from on_knowledge.features.presentations.errors import PresentationProtocolError

    def reject(*args):
        raise PresentationProtocolError("Invalid input")

    monkeypatch.setattr("on_knowledge.features.presentations.review.review_facts", reject)
    guard = SimpleNamespace(calls=[{"result": verdicts("supported")}])
    result = evaluate_case(
        None,
        guard,
        {
            "id": "invalid",
            "question": "q",
            "facts": [{}],
            "evidence": [],
            "expected_supported_claim_ids": ["C1"],
        },
    )
    assert not result["passed"]
    assert result["protocol"] == "protocol_error"
    assert "exactly one" in result["unscorable"]
