"""Presentation generation contracts use synthetic providers, never real inference."""

import copy
import time

import pytest
from on_knowledge.features.jobs.schemas import GenerationRequest
from on_knowledge.features.jobs.service import GenerationService
from on_knowledge.features.presentations.assembly import assemble_presentation
from on_knowledge.features.presentations.repository import PresentationRepository
from on_knowledge.storage import ConflictError, Store, now, uid, write_json
from pydantic import ValidationError


def request(**overrides):
    return {"request_id": uid(), "kind": "presentation_outline", "language": "en", **overrides}


def terminal(service, notebook, job):
    deadline = time.monotonic() + 4
    while time.monotonic() < deadline:
        result = service.get(notebook, job["id"])
        if result["status"] not in {"queued", "running"}:
            return result
        time.sleep(0.01)
    pytest.fail("Synthetic presentation generation did not terminate")


class Provider:
    def __init__(self, *, reject=False, output=None):
        self.calls = []
        self.reject = reject
        self.output = output

    def complete(self, system, data):
        self.calls.append((system, copy.deepcopy(data)))
        if "evidence critic" in system:
            return {
                "supported_claim_ids": [] if self.reject else [item["claim_id"] for item in data["claims"]]
            }
        if self.output is not None:
            return self.output
        russian = data["answer_language"] == "ru"
        return {
            "slides": [
                {
                    "title": "Проект Marigold" if russian else "Project Marigold",
                    "layout": "bullets",
                    "bullets": [
                        "Запуск намечен на 18 октября." if russian else "Launch is planned for October 18."
                    ],
                    "notes": "Это план." if russian else "This is a plan.",
                    "evidence_ids": ["E1"],
                }
            ]
        }


@pytest.fixture
def setup(tmp_path, monkeypatch):
    store = Store(tmp_path)
    settings = store.settings()
    settings["profiles"][settings["provider"]]["model"] = "fixture"
    write_json(store.root / "settings.json", settings)
    notebook = store.create_notebook("Slides")["id"]
    source = {"id": uid(), "title": "Project", "status": "ready", "version": "v1", "created_at": now()}
    store.save_source(notebook, source)
    text = "Project Marigold's launch is planned for October 18. This is a plan."
    store.replace_chunks(
        notebook,
        source["id"],
        "v1",
        [
            {
                "id": "original-version-passage",
                "text": text,
                "location": {"page": 2, "element": 0, "offset_start": 0, "offset_end": len(text)},
            }
        ],
    )
    monkeypatch.setattr("on_knowledge.features.jobs.service.provider_key", lambda settings: "fixture-key")
    provider = Provider()
    monkeypatch.setattr(
        "on_knowledge.features.presentations.generator.completion_provider", lambda _: provider
    )
    service = GenerationService(store, object())
    yield store, notebook, source, service, provider
    service.close()
    if service._thread:
        service._thread.join(timeout=2)


def create_outline(service, notebook, **overrides):
    service.start()
    job = terminal(service, notebook, service.submit(notebook, request(**overrides)))
    assert job["status"] == "completed", job
    return service.materials.get(notebook, job["result"]["material_id"])


def deck_request(outline, **overrides):
    return request(
        **{
            "kind": "presentation",
            "outline_id": outline["id"],
            "outline_revision": outline["presentation"]["revision"],
            **overrides,
        }
    )


def test_request_contract_separates_outline_from_explicit_slide_submission():
    assert GenerationRequest.model_validate(request()).kind == "presentation_outline"
    assert GenerationRequest.model_validate(
        request(kind="presentation", outline_id=uid(), outline_revision=1)
    )
    for changes in (
        {"kind": "presentation"},
        {"kind": "presentation", "outline_id": uid()},
        {"outline_id": uid(), "outline_revision": 1},
        {"kind": "summary", "outline_id": uid(), "outline_revision": 1},
        {"kind": "presentation", "outline_id": "../escape", "outline_revision": 1},
        {"kind": "presentation", "outline_id": uid(), "outline_revision": 0},
        {"kind": "presentation", "outline_id": uid(), "outline_revision": True},
        {
            "kind": "presentation",
            "outline_id": uid(),
            "outline_revision": 1,
            "context": {"source_ids": [], "note_ids": []},
        },
    ):
        with pytest.raises(ValidationError):
            GenerationRequest.model_validate(request(**changes))


@pytest.mark.parametrize("language", ["en", "ru"])
def test_outline_approval_generates_separate_deck_with_canonical_sources(setup, language):
    store, notebook, source, service, provider = setup
    outline = create_outline(service, notebook, language=language, template="dark")
    assert len(provider.calls) == 2
    assert outline["answer"]["validated"] is False
    assert outline["presentation"]["stage"] == "outline"
    assert outline["presentation"]["template"] == "dark"
    assert notebook not in store.active_operations
    job = terminal(service, notebook, service.submit(notebook, deck_request(outline)))
    assert job["status"] == "completed", job
    deck = service.materials.get(notebook, job["result"]["material_id"])
    assert deck["answer"]["validated"] is False
    assert deck["presentation"]["stage"] == "slides"
    assert deck["presentation"]["language"] == language
    assert deck["presentation"]["template"] == "dark"
    assert deck["context"] == outline["context"]
    assert deck["presentation"]["slides"][0]["evidence_ids"] == ["original-version-passage"]
    assert deck["answer"]["citations"][0]["version"] == "v1"
    assert deck["answer"]["citations"][0]["source_id"] == source["id"]
    assert deck["id"] != outline["id"] and len(service.materials.list(notebook)) == 2
    assert deck["presentation"] == {**outline["presentation"], "stage": "slides", "revision": 1}
    assert len(provider.calls) == 2
    texts = [claim["text"] for claim in provider.calls[1][1]["claims"]]
    assert ("Проект Marigold" if language == "ru" else "Project Marigold") in texts
    assert ("Это план." if language == "ru" else "This is a plan.") in texts


def test_outline_restart_does_not_replay_and_worker_is_available(setup):
    store, notebook, source, service, provider = setup
    outline = create_outline(service, notebook)
    service.close()
    restarted = GenerationService(store, object())
    try:
        restarted.start()
        assert restarted.materials.get(notebook, outline["id"]) == outline
        assert len(provider.calls) == 2
        second = create_outline(restarted, notebook)
        assert second["id"] != outline["id"]
        deck = terminal(restarted, notebook, restarted.submit(notebook, deck_request(outline)))
        assert deck["status"] == "completed"
        assert len(provider.calls) == 4
    finally:
        restarted.close()
        restarted._thread.join(timeout=2)


def test_stale_outline_and_changed_source_fail_before_any_new_provider_call(setup):
    store, notebook, source, service, provider = setup
    outline = create_outline(service, notebook)
    with pytest.raises(ConflictError):
        service.submit(notebook, deck_request(outline, outline_revision=9))
    source["version"] = "v2"
    store.save_source(notebook, source)
    with pytest.raises(ConflictError):
        service.submit(notebook, deck_request(outline))
    assert len(service.list(notebook)) == 1 and len(provider.calls) == 2


def test_accepted_outline_is_immutable_and_duplicate_remains_idempotent(setup):
    store, notebook, source, service, provider = setup
    outline = create_outline(service, notebook)
    # Keep the accepted deck queued while the saved outline is edited.
    service.close()
    queue = GenerationService(store, object())
    try:
        body = deck_request(outline)
        first = queue.submit(notebook, body)
        changed = copy.deepcopy(outline)
        changed["presentation"]["revision"] = 2
        changed["presentation"]["slides"][0]["title"] = "Later title"
        write_json(queue.materials.path(notebook, outline["id"]), changed)
        assert queue.submit(notebook, body)["id"] == first["id"]
        queue.start()
        result = terminal(queue, notebook, first)
        assert result["status"] == "completed"
        deck = queue.materials.get(notebook, result["result"]["material_id"])
        assert deck["presentation"]["slides"][0]["title"] == "Project Marigold"
        assert len(provider.calls) == 2
    finally:
        queue.close()
        if queue._thread:
            queue._thread.join(timeout=2)


@pytest.mark.parametrize("bad", ["unknown_citation", "oversized", "rejected_title", "wrong_language"])
def test_invalid_or_unverified_presentation_does_not_publish(setup, bad):
    store, notebook, source, service, provider = setup
    if bad == "rejected_title":
        provider.reject = True
    else:
        output = Provider().complete("writer", {"answer_language": "en"})
        if bad == "unknown_citation":
            output["slides"][0]["evidence_ids"] = ["E999"]
        elif bad == "oversized":
            output["slides"][0]["title"] = "x" * 161
        provider.output = output
    service.start()
    job = terminal(
        service,
        notebook,
        service.submit(notebook, request(language="ru" if bad == "wrong_language" else "en")),
    )
    assert job["status"] == "failed" and job["error"] == "unverified_output", job
    assert not service.materials.list(notebook)
    assert len(provider.calls) <= 2


def test_empty_selection_makes_no_model_call(setup):
    store, notebook, source, service, provider = setup
    service.start()
    job = terminal(
        service, notebook, service.submit(notebook, request(context={"source_ids": [], "note_ids": []}))
    )
    assert job["error"] == "no_evidence" and not provider.calls


def test_approved_edited_outline_assembles_offline_without_model_or_credentials(setup, monkeypatch):
    store, notebook, source, service, provider = setup
    outline = create_outline(service, notebook)
    document = copy.deepcopy(outline["presentation"])
    document["slides"][0]["notes"] = "This approved wording must not be rewritten."
    edited = PresentationRepository(store).update(
        notebook, outline["id"], {"expected_revision": 1, "presentation": document}
    )
    settings = store.settings()
    settings["profiles"][settings["provider"]]["model"] = ""
    write_json(store.root / "settings.json", settings)

    def forbidden(*args, **kwargs):
        pytest.fail("Approved slide assembly must not access a model, embeddings or credentials")

    monkeypatch.setattr("on_knowledge.features.jobs.service.provider_key", forbidden)
    monkeypatch.setattr("on_knowledge.features.presentations.generator.completion_provider", forbidden)
    monkeypatch.setattr(service.context, "gather_snapshot", forbidden)
    job = terminal(service, notebook, service.submit(notebook, deck_request(edited)))
    assert job["status"] == "completed", job
    deck = service.materials.get(notebook, job["result"]["material_id"])
    expected = {**edited["presentation"], "stage": "slides", "revision": 1}
    assert deck["presentation"] == expected
    assert deck["answer"]["citations"] == edited["answer"]["citations"]
    assert deck["answer"]["validated"] is False
    assert len(provider.calls) == 2


def test_queued_assembly_ignores_changed_ai_settings_and_credentials(setup, monkeypatch):
    store, notebook, source, service, provider = setup
    outline = create_outline(service, notebook)
    service.close()
    queue = GenerationService(store, object())
    try:
        first = queue.submit(notebook, deck_request(outline))
        settings = store.settings()
        settings["profiles"][settings["provider"]]["model"] = ""
        write_json(store.root / "settings.json", settings)

        def forbidden(*args, **kwargs):
            pytest.fail("Queued assembly cannot read current AI configuration or credentials")

        monkeypatch.setattr(store, "settings", forbidden)
        monkeypatch.setattr(queue, "_credentials", forbidden)
        queue.start()
        assert terminal(queue, notebook, first)["status"] == "completed"
        assert len(provider.calls) == 2
    finally:
        queue.close()
        if queue._thread:
            queue._thread.join(timeout=2)


def test_assembly_cancel_and_explicit_retry_keep_provider_idle(setup):
    store, notebook, source, service, provider = setup
    outline = create_outline(service, notebook)
    service.close()
    queue = GenerationService(store, object())
    try:
        first = queue.submit(notebook, deck_request(outline))
        assert queue.cancel(notebook, first["id"])["status"] == "cancelled"
        assert notebook not in store.active_operations
        retried = queue.retry(notebook, first["id"], uid())
        queue.start()
        done = terminal(queue, notebook, retried)
        assert done["status"] == "completed" and done["retry_of"] == first["id"]
        assert len(queue.materials.list(notebook)) == 2 and len(provider.calls) == 2
    finally:
        queue.close()
        if queue._thread:
            queue._thread.join(timeout=2)


@pytest.mark.parametrize("interruption", ["cancel", "context_change"])
def test_assembly_checkpoint_prevents_publish_after_interruption(setup, monkeypatch, interruption):
    store, notebook, source, service, provider = setup
    outline = create_outline(service, notebook)

    def interrupted(job):
        result = assemble_presentation(job)
        if interruption == "cancel":
            service.cancel(notebook, job["id"])
        else:
            store.save_source(notebook, {**source, "version": "v2"})
        return result

    monkeypatch.setattr("on_knowledge.features.jobs.execution.assemble_presentation", interrupted)
    job = terminal(service, notebook, service.submit(notebook, deck_request(outline)))
    if interruption == "cancel":
        assert job["status"] == "cancelled"
    else:
        assert job["status"] == "failed" and job["error"] == "context_changed"
    assert len(service.materials.list(notebook)) == 1 and len(provider.calls) == 2


@pytest.mark.parametrize(
    "tamper", [None, "marker", "snapshot", "snapshot_missing", "slides", "citations", "context", "legacy"]
)
def test_recover_assembly_requires_matching_snapshot_not_factual_validation(setup, tamper):
    store, notebook, source, service, provider = setup
    outline = create_outline(service, notebook)
    document = copy.deepcopy(outline["presentation"])
    document["slides"][0]["notes"] = "Approved edited text."
    outline = PresentationRepository(store).update(
        notebook, outline["id"], {"expected_revision": 1, "presentation": document}
    )
    service.close()
    queue = GenerationService(store, object())
    try:
        submitted = queue.submit(notebook, deck_request(outline))
        job = queue.jobs.get(notebook, submitted["id"])
        material = {
            "id": job["id"],
            "job_id": job["id"],
            "kind": "presentation",
            "title": job["title"],
            "created_at": now(),
            "context": copy.deepcopy(job["context"]),
            "provider": job["provider"],
            **assemble_presentation(job),
        }
        assert material["answer"]["validated"] is False
        if tamper == "marker":
            material.pop("assembly")
        elif tamper == "snapshot":
            job["_outline_snapshot"]["presentation"]["slides"][0]["notes"] = "Changed accepted text."
        elif tamper == "snapshot_missing":
            job.pop("_outline_snapshot")
        elif tamper == "slides":
            material["presentation"]["slides"][0]["notes"] = "Unapproved rewrite."
        elif tamper == "citations":
            material["answer"]["citations"][0]["quote"] = "Different evidence."
        elif tamper == "context":
            material["context"]["sources"][0]["version"] = "v2"
        elif tamper == "legacy":
            job.pop("_outline_snapshot")
            material.pop("assembly")
            material["answer"]["validated"] = True  # Cannot bypass assembly integrity.
        queue.jobs.save(notebook, job)
        queue.materials.create(notebook, material)  # Crash before terminal job update.
        recovered = GenerationService(store, object())
        recovered.recover()
        status = recovered.get(notebook, job["id"])["status"]
        assert status == ("completed" if tamper is None else "interrupted")
        assert len(provider.calls) == 2
    finally:
        queue.close()


def test_slide_request_cannot_silently_apply_or_ignore_rewrite_instructions(setup):
    store, notebook, source, service, provider = setup
    outline = create_outline(service, notebook)
    with pytest.raises(ValueError, match="Edit and save the outline"):
        service.submit(notebook, deck_request(outline, question="Rewrite every slide in a new style."))
    assert len(provider.calls) == 2 and len(service.list(notebook)) == 1
