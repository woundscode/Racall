"""Recorded review text survives assembly without another semantic writer."""

import copy
import json
from pathlib import Path

import pytest
from on_knowledge.features.jobs.execution import generate_payload
from on_knowledge.features.presentations.assembly import approval_marker, outline_snapshot
from on_knowledge.features.presentations.generator import generate_presentation


def test_recorded_safe_outline_cannot_be_rewritten_into_bad_c8(monkeypatch):
    path = (
        Path(__file__).parents[1] / "evals/release04/regressions/meeting-approval-versus-global-change.json"
    )
    recorded = json.loads(path.read_text(encoding="utf-8"))
    approved = copy.deepcopy(recorded["writer_data"]["outline"])
    # The recording uses request-local labels; durable material uses canonical IDs.
    ids = {"E1": "station-source-v1-passage", "E2": "meeting-note-revision-1"}
    for slide in approved["slides"]:
        slide["evidence_ids"] = [ids[label] for label in slide["evidence_ids"]]
    citations = [
        {**item, "id": ids[item["id"]], "version": "v1", "number": number}
        for number, item in enumerate(recorded["writer_data"]["evidence"], 1)
    ]
    material = {
        "id": "recorded-approved-outline",
        "presentation": approved,
        "answer": {"validated": False, "claims": [], "citations": citations},
        "context": {"sources": [{"id": "station", "version": "v1"}], "notes": []},
        "instructions": recorded["writer_data"]["question"],
    }
    snapshot = outline_snapshot(material)
    job = {
        "kind": "presentation",
        "outline_id": material["id"],
        "outline_revision": approved["revision"],
        "context": material["context"],
        "assembly": approval_marker(snapshot),
        "_outline_snapshot": snapshot,
    }

    def forbidden(*args, **kwargs):
        pytest.fail("Assembly must never invoke another writer, critic, or retrieval")

    class NoContextGather:
        gather_snapshot = forbidden

    monkeypatch.setattr("on_knowledge.features.presentations.generator.completion_provider", forbidden)
    steps = []
    result, research = generate_payload(
        "notebook",
        job,
        {},
        context=NoContextGather(),
        knowledge=None,
        checkpoint=lambda: None,
        progress=steps.append,
    )
    assert research is None and steps == ["assembling"]
    assert result["presentation"] == {**approved, "stage": "slides", "revision": 1}
    assert result["answer"]["citations"] == citations
    assert result["answer"]["validated"] is False
    bad_c8 = next(claim["text"] for claim in recorded["critic_data"]["claims"] if claim["claim_id"] == "C8")
    assert bad_c8 == recorded["writer_response"]["slides"][1]["notes"]
    assert bad_c8 not in result["body"]
    assert approved["slides"][1]["notes"] in result["body"]
    assert material["presentation"]["stage"] == "outline"
    assert snapshot["answer"] == material["answer"]  # No mutation of approval evidence.


def test_outline_generator_refuses_a_second_writer_before_opening_provider(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Slide assembly cannot open a provider")

    monkeypatch.setattr("on_knowledge.features.presentations.generator.completion_provider", forbidden)
    with pytest.raises(ValueError, match="Only outlines"):
        generate_presentation({"kind": "presentation"}, [], {}, forbidden, forbidden)
