"""Authenticated source -> outline -> edit -> slides -> offline exports."""

import time
from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from on_knowledge.app import create_app
from on_knowledge.storage import uid, write_json
from pptx import Presentation as PowerPoint
from presentation_protocol_fixtures import audit_response, ledger_from_slides
from pypdf import PdfReader


def test_development_origin_can_save_presentations(tmp_path):
    with TestClient(create_app(tmp_path, "fixture-token")) as client:
        response = client.options(
            "/api/notebooks/test/materials/test/presentation",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "PATCH",
                "Access-Control-Request-Headers": "Authorization, Content-Type",
            },
        )
        assert response.status_code == 200
        assert "PATCH" in response.headers["Access-Control-Allow-Methods"]


@pytest.mark.parametrize("edit_outline", [False, True])
def test_approved_outline_exports_without_certification_or_further_provider_calls(
    tmp_path, monkeypatch, edit_outline
):
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
                        "title": "Marigold plan",
                        "bullets": ["Launch is planned for October 18."],
                        "notes": "The source describes a plan, not a completed launch.",
                        "evidence_ids": ["E1"],
                    }
                ]
            }
            return ledger_from_slides(raw, data["evidence"])

    monkeypatch.setattr(
        "on_knowledge.features.presentations.generator.completion_provider", lambda _: Provider()
    )
    monkeypatch.setattr("on_knowledge.features.jobs.service.provider_key", lambda _: "fixture")
    app = create_app(tmp_path, "fixture-token")
    store = app.state.store
    settings = store.settings()
    settings["profiles"][settings["provider"]]["model"] = "fixture"
    write_json(store.root / "settings.json", settings)
    notebook = store.create_notebook("Presentation")["id"]
    note = store.save_note(
        notebook, "Plan", "Marigold launch is planned for October 18. This is a plan, not a completed launch."
    )
    prefix = f"/api/notebooks/{notebook}"

    with TestClient(app) as client:
        client.headers["Authorization"] = "Bearer fixture-token"

        def generate(body):
            response = client.post(prefix + "/jobs", json={"request_id": uid(), **body})
            assert response.status_code == 202, response.text
            job = response.json()
            deadline = time.monotonic() + 4
            while job["status"] in {"queued", "running"} and time.monotonic() < deadline:
                time.sleep(0.01)
                job = client.get(prefix + "/jobs/" + job["id"]).json()
            assert job["status"] == "completed", job
            return client.get(prefix + "/materials/" + job["result"]["material_id"]).json()

        outline = generate(
            {"kind": "presentation_outline", "context": {"source_ids": [], "note_ids": [note["id"]]}}
        )
        assert len(calls) == 2
        assert outline["answer"]["validated"] is False
        outline_path = prefix + "/materials/" + outline["id"] + "/presentation"
        document = outline["presentation"]
        if edit_outline:
            document["title"] = "My talk"
            document["slides"][0]["title"] = "Launch plan"
        saved = client.patch(outline_path, json={"expected_revision": 1, "presentation": document})
        assert saved.status_code == 200, saved.text
        assert saved.json()["presentation"]["revision"] == 2
        assert not saved.json()["answer"]["validated"]
        assert client.get(outline_path + "/export?format=pdf&revision=2").status_code == 400

        def forbidden(*args, **kwargs):
            raise AssertionError("Assembly and export must not contact any provider")

        monkeypatch.setattr("on_knowledge.features.presentations.generator.completion_provider", forbidden)
        monkeypatch.setattr("on_knowledge.features.jobs.service.provider_key", forbidden)
        deck = generate({"kind": "presentation", "outline_id": outline["id"], "outline_revision": 2})
        assert len(calls) == 2
        assert deck["presentation"] == {**saved.json()["presentation"], "stage": "slides", "revision": 1}
        assert deck["answer"]["validated"] is False
        assert deck["presentation"]["title"] == document["title"]
        assert deck["outline_revision"] == 2
        assert deck["context"] == outline["context"]
        assert deck["answer"]["citations"][0]["version"] == note["revision"]

        path = prefix + "/materials/" + deck["id"] + "/presentation"
        pdf = client.get(path + "/export?format=pdf&revision=1")
        assert pdf.status_code == 200, pdf.text
        assert pdf.headers["Content-Type"] == "application/pdf"
        text = "\n".join(page.extract_text() for page in PdfReader(BytesIO(pdf.content)).pages)
        assert "Launch is planned for October 18." in text
        pptx = client.get(path + "/export?format=pptx&revision=1")
        assert pptx.status_code == 200, pptx.text
        parsed = PowerPoint(BytesIO(pptx.content))
        editable_text = "\n".join(
            shape.text for slide in parsed.slides for shape in slide.shapes if shape.has_text_frame
        )
        assert "Launch is planned for October 18." in editable_text
        assert len(calls) == 2
        persisted = client.get(prefix + "/materials/" + deck["id"]).json()
        assert persisted == deck  # Neither exporter may mutate the saved verdict or text.
        client.headers["Authorization"] = "Bearer wrong"
        assert client.get(path + "/export?format=pdf&revision=1").status_code == 401
