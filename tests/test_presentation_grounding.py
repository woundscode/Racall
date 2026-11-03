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
from on_knowledge.features.presentations.generator import generate_presentation


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
            key = "critic_response" if "evidence critic" in system else "writer_response"
            return copy.deepcopy(recorded[key])

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
