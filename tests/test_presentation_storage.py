from copy import deepcopy

import pytest
from on_knowledge.features.artifacts.repository import Materials
from on_knowledge.features.presentations.repository import PresentationRepository
from on_knowledge.features.presentations.schemas import Presentation, PresentationUpdate
from on_knowledge.storage import ConflictError, Store, now, uid, write_json
from pydantic import ValidationError


@pytest.fixture
def stored(tmp_path):
    store = Store(tmp_path)
    notebook = store.create_notebook("Slides")["id"]
    material = {
        "id": uid(),
        "kind": "presentation",
        "title": "Research",
        "created_at": now(),
        "body": "Original",
        "answer": {
            "claims": [],
            "citations": [
                {
                    "id": "source:v1",
                    "number": 1,
                    "title": "Source",
                    "quote": "A measured result.",
                    "version": "v1",
                    "location": {},
                }
            ],
            "validated": True,
        },
        "presentation": {
            "schema_version": 1,
            "revision": 1,
            "stage": "slides",
            "title": "Research",
            "language": "en",
            "template": "light",
            "slides": [
                {
                    "id": "s1",
                    "layout": "bullets",
                    "title": "First",
                    "bullets": ["A measured result."],
                    "notes": "",
                    "evidence_ids": ["source:v1"],
                    "review_state": "generated",
                },
                {
                    "id": "s2",
                    "layout": "section",
                    "title": "Second",
                    "bullets": [],
                    "notes": "",
                    "evidence_ids": ["source:v1"],
                    "review_state": "generated",
                },
            ],
        },
    }
    Materials(store).create(notebook, material)
    return store, notebook, material


def update(material):
    return {
        "expected_revision": material["presentation"]["revision"],
        "presentation": deepcopy(material["presentation"]),
    }


def test_edits_preserve_baseline_citations_and_survive_restart(stored):
    store, nb, material = stored
    request = update(material)
    request["presentation"]["slides"][0]["title"] = "User correction"
    request["presentation"]["slides"].reverse()
    result = PresentationRepository(store).update(nb, material["id"], request)
    assert result["presentation"]["revision"] == 2
    assert result["presentation"]["slides"][1]["review_state"] == "edited"
    assert not result["answer"]["validated"]
    assert result["answer"]["citations"] == material["answer"]["citations"]
    reopened = PresentationRepository(Store(store.root)).get(nb, material["id"])
    assert reopened == result
    assert PresentationRepository(store).revision(nb, material["id"], 1) == material
    assert "User correction" in reopened["body"]


def test_stale_save_does_not_replace_newer_content(stored):
    store, nb, material = stored
    repo = PresentationRepository(store)
    request = update(material)
    request["presentation"]["title"] = "Updated"
    repo.update(nb, material["id"], request)
    with pytest.raises(ConflictError):
        repo.update(nb, material["id"], update(material))
    assert repo.get(nb, material["id"])["title"] == "Updated"


@pytest.mark.parametrize("change", ["evidence", "slide_id", "language", "stage"])
def test_edits_cannot_forge_provenance_or_identity(stored, change):
    store, nb, material = stored
    request = update(material)
    if change == "evidence":
        request["presentation"]["slides"][0]["evidence_ids"] = ["invented"]
    elif change == "slide_id":
        request["presentation"]["slides"][0]["id"] = "unknown"
    else:
        request["presentation"][change] = "ru" if change == "language" else "outline"
    with pytest.raises(ValueError):
        PresentationRepository(store).update(nb, material["id"], request)
    assert Materials(store).get(nb, material["id"]) == material


@pytest.mark.parametrize("validated", [False, True])
def test_template_and_order_change_preserve_new_and_legacy_answer_flags(stored, validated):
    store, nb, material = stored
    material["answer"]["validated"] = validated
    path = Materials(store).path(nb, material["id"])
    write_json(path, material)
    saved_bytes = path.read_bytes()
    assert PresentationRepository(store).get(nb, material["id"]) == material
    assert path.read_bytes() == saved_bytes  # A read must not migrate historical material.
    request = update(material)
    request["presentation"]["template"] = "dark"
    request["presentation"]["slides"].reverse()
    result = PresentationRepository(store).update(nb, material["id"], request)
    assert result["answer"]["validated"] is validated
    assert all(s["review_state"] == "generated" for s in result["presentation"]["slides"])


def test_crash_draft_and_explicit_save(stored):
    store, nb, material = stored
    request = update(material)
    request["presentation"]["slides"][0]["notes"] = "Unfinished user work"
    repo = PresentationRepository(store)
    repo.save_draft(nb, material["id"], request)
    reopened = PresentationRepository(Store(store.root))
    assert reopened.draft(nb, material["id"])["presentation"] == request["presentation"]
    assert reopened.get(nb, material["id"]) == material
    reopened.update(nb, material["id"], request)
    assert reopened.draft(nb, material["id"]) is None
    with pytest.raises(ConflictError):
        reopened.save_draft(nb, material["id"], request)


def test_failed_material_write_keeps_current_revision(stored, monkeypatch):
    store, nb, material = stored
    import on_knowledge.features.presentations.repository as module

    original_write = module.write_json

    def fail(path, value):
        if path == Materials(store).path(nb, material["id"]):
            raise OSError("disk full")
        original_write(path, value)

    monkeypatch.setattr(module, "write_json", fail)
    request = update(material)
    request["presentation"]["title"] = "Not saved"
    with pytest.raises(OSError):
        PresentationRepository(store).update(nb, material["id"], request)
    assert Materials(store).get(nb, material["id"]) == material


def test_duplicate_slides_and_oversized_text_rejected(stored):
    document = deepcopy(stored[2]["presentation"])
    document["slides"][1]["id"] = document["slides"][0]["id"]
    with pytest.raises(ValidationError):
        Presentation.model_validate(document)
    document = deepcopy(stored[2]["presentation"])
    document["slides"][0]["title"] = "x" * 161
    with pytest.raises(ValidationError):
        PresentationUpdate.model_validate({"expected_revision": 1, "presentation": document})


def test_incomplete_draft_survives_without_becoming_valid_deck(stored):
    store, nb, material = stored
    request = update(material)
    request["presentation"]["title"] = ""
    request["presentation"]["slides"][0]["bullets"] = [""]
    repo = PresentationRepository(store)
    repo.save_draft(nb, material["id"], request)
    assert PresentationRepository(Store(store.root)).draft(nb, material["id"])["presentation"]["title"] == ""
    with pytest.raises(ValidationError):
        repo.update(nb, material["id"], request)
    assert repo.get(nb, material["id"]) == material


def test_authenticated_routes_and_revision_fence(stored):
    from fastapi.testclient import TestClient
    from on_knowledge.app import create_app

    store, nb, material = stored
    endpoint = f"/api/notebooks/{nb}/materials/{material['id']}/presentation"
    with TestClient(create_app(store.root, "test-token")) as client:
        assert client.get(endpoint + "/draft").status_code == 401
        client.headers["Authorization"] = "Bearer test-token"
        assert client.get(endpoint + "/draft").json() is None
        request = update(material)
        request["presentation"]["slides"][0]["title"] = "Corrected"
        assert client.put(endpoint + "/draft", json=request).status_code == 200
        saved = client.patch(endpoint, json=request)
        assert saved.status_code == 200 and saved.json()["presentation"]["revision"] == 2
        assert client.patch(endpoint, json=request).status_code == 409
        assert client.get(endpoint + "/preview?revision=1").status_code == 409
        assert client.get(endpoint + "/export?revision=1&format=pdf").status_code == 409
        assert client.get(endpoint + "/export?revision=2&format=html").status_code == 422
        assert client.get(endpoint + "/revisions/1").json() == material


def test_stale_draft_cleanup_does_not_fail_a_committed_save(stored):
    from on_knowledge.storage import write_json

    store, nb, material = stored
    repo = PresentationRepository(store)
    request = update(material)
    repo.save_draft(nb, material["id"], request)
    draft = repo.draft(nb, material["id"])
    current = repo.update(nb, material["id"], request)
    write_json(repo._draft_path(nb, material["id"]), draft)
    saved = repo.update(nb, material["id"], update(current))
    assert saved["presentation"]["revision"] == 3
    assert repo.draft(nb, material["id"]) == draft
