"""Recorded model verdicts are not factual certificates; no live inference."""

import copy
import json
from pathlib import Path

import pytest
from on_knowledge.features.presentations.assembly import (
    approval_marker,
    assemble_presentation,
    outline_snapshot,
)
from on_knowledge.features.presentations.errors import UnsupportedPresentation
from on_knowledge.features.presentations.generator import generate_presentation
from presentation_protocol_fixtures import audit_response, ledger_from_slides


@pytest.mark.parametrize(
    "fixture",
    [
        "meeting-approval-versus-global-change.json",
        "results-not-received-versus-absent.json",
        "inline-evidence-markers.json",
    ],
)
def test_model_critic_acceptance_and_user_approval_are_not_factual_certificates(monkeypatch, fixture):
    path = Path(__file__).parents[1] / "evals/release04/regressions" / fixture
    recorded = json.loads(path.read_text(encoding="utf-8"))
    original = copy.deepcopy(recorded)
    request = recorded.get("writer_data", recorded)
    evidence = recorded.get("evidence", request.get("evidence", []))

    class ReplayProvider:
        def complete(self, system, data):
            if "claims" in data:
                # Preserve the old all-accepted decision in a synthetic new wire
                # response. Its extra quotes/reason were NOT produced by a model.
                return audit_response(data)
            return ledger_from_slides(recorded["writer_response"], evidence)

    monkeypatch.setattr(
        "on_knowledge.features.presentations.generator.completion_provider", lambda _: ReplayProvider()
    )
    generated = generate_presentation(
        {
            "kind": "presentation_outline",
            "language": request.get("answer_language", recorded.get("language", "en")),
            "title": "Recorded model draft",
            "question": request.get("question", ""),
        },
        [{**item, "id": "canonical-" + item["id"]} for item in evidence],
        {},
        lambda: None,
        lambda *args: None,
    )
    assert generated["answer"]["validated"] is False
    assert (
        generated["presentation"]["slides"][1]["notes"] == recorded["writer_response"]["slides"][1]["notes"]
    )
    snapshot = outline_snapshot({"id": "recorded-draft", "context": {}, **generated})
    assembled = assemble_presentation(
        {
            "_outline_snapshot": snapshot,
            "assembly": approval_marker(snapshot),
            "context": {},
            "outline_id": "recorded-draft",
            "outline_revision": 1,
        }
    )
    assert assembled["answer"]["validated"] is False
    assert assembled["presentation"]["slides"] == generated["presentation"]["slides"]
    assert recorded == original


@pytest.mark.parametrize(
    "fixture",
    [
        "meeting-approval-versus-global-change.json",
        "results-not-received-versus-absent.json",
    ],
)
def test_semantically_equivalent_recording_can_be_rejected_without_rewriting_or_retry(monkeypatch, fixture):
    path = Path(__file__).parents[1] / "evals/release04/regressions" / fixture
    original_bytes = path.read_bytes()
    recorded = json.loads(original_bytes)
    request = recorded["writer_data"]
    evidence = request["evidence"]
    ledger = ledger_from_slides(recorded["writer_response"], evidence)
    original_texts = [
        text
        for slide in recorded["writer_response"]["slides"]
        for text in (slide["title"], *slide["bullets"], slide["notes"])
        if text
    ]
    assert [fact["text"] for fact in ledger["claims"]] == original_texts
    calls = []

    class Provider:
        def complete(self, system, data):
            calls.append(copy.deepcopy(data))
            if "claims" in data:
                # Tests the rejection path, not the real model's ability to find C8.
                return audit_response(data, rejected=recorded["expected_rejected_claim_ids"])
            return copy.deepcopy(ledger)

    monkeypatch.setattr(
        "on_knowledge.features.presentations.generator.completion_provider", lambda _: Provider()
    )
    with pytest.raises(UnsupportedPresentation) as caught:
        generate_presentation(
            {
                "kind": "presentation_outline",
                "language": request["answer_language"],
                "title": "Review",
                "question": request["question"],
            },
            [{**item, "id": "canonical-" + item["id"]} for item in evidence],
            {},
            lambda: None,
            lambda *args: None,
        )
    assert caught.value.rejected == ("C8",)
    assert len(calls) == 2
    assert calls[1]["claims"][-1]["text"] == original_texts[-1]
    assert path.read_bytes() == original_bytes
