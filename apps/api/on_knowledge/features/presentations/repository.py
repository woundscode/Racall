"""Revision-checked edits and crash drafts, with portable files as authority."""

import json
from copy import deepcopy

from ...storage import ConflictError, Store, now, read_text, write_json
from ..artifacts.repository import Materials
from .markdown import presentation_markdown
from .schemas import Presentation, PresentationDraftUpdate, PresentationUpdate


class PresentationRepository:
    def __init__(self, store: Store):
        self.store = store
        self.materials = Materials(store)

    def get(self, notebook: str, material: str) -> dict:
        item = self.materials.get(notebook, material)
        if not item.get("presentation"):
            raise ValueError("This material is not a presentation.")
        Presentation.model_validate(item["presentation"])
        return item

    def _history(self, notebook, material, revision):
        path = self.materials.path(notebook, material)
        return path.parent / "presentation-revisions" / path.stem / f"{revision}.json"

    def revision(self, notebook: str, material: str, revision: int) -> dict:
        with self.store.lock:
            item = self.get(notebook, material)
            if item["presentation"]["revision"] == revision:
                return item
            if revision < 1:
                raise ValueError("Invalid revision.")
            return json.loads(read_text(self._history(notebook, material, revision)))

    def _draft_path(self, notebook, material):
        path = self.materials.path(notebook, material)
        return path.parent / "presentation-drafts" / path.name

    def _prepare(self, item, request, *, draft=False):
        request = (PresentationDraftUpdate if draft else PresentationUpdate).model_validate(request)
        original = Presentation.model_validate(item["presentation"])
        if original.revision != request.expected_revision:
            raise ConflictError("The presentation changed. Reopen it before saving your draft.")
        document = request.presentation.model_copy(deep=True)
        if (document.stage, document.language) != (original.stage, original.language):
            raise ValueError("Presentation stage and language cannot be changed by an edit.")
        originals = {slide.id: slide for slide in original.slides}
        for slide in document.slides:
            previous = originals.get(slide.id)
            if previous is None or slide.evidence_ids != previous.evidence_ids:
                raise ValueError("Editing cannot replace slide identity or evidence references.")
            changed = (slide.title, slide.bullets, slide.notes) != (
                previous.title,
                previous.bullets,
                previous.notes,
            )
            slide.review_state = (
                "edited" if changed or document.title != original.title else previous.review_state
            )
        return document

    def update(self, notebook: str, material: str, request: PresentationUpdate | dict) -> dict:
        with self.store.lock:
            item = self.get(notebook, material)
            document = self._prepare(item, request)
            previous_revision = document.revision
            document.revision += 1
            updated = deepcopy(item)
            updated.update(
                presentation=document.model_dump(),
                title=document.title,
                updated_at=now(),
                body=presentation_markdown(document, item["answer"]["citations"]),
            )
            if any(slide.review_state == "edited" for slide in document.slides):
                updated["answer"].update(validated=False, claims=[], mode="presentation_edited")
            history = self._history(notebook, material, previous_revision)
            if not history.exists():
                write_json(history, item)
            write_json(self.materials.path(notebook, material), updated)
            # A failed cleanup cannot turn a committed save into an apparent failure.
            # Old drafts are harmless and remain visibly stale if deletion is unavailable.
            try:
                draft = self.draft(notebook, material)
                if draft and draft["expected_revision"] == previous_revision:
                    self.discard_draft(notebook, material, previous_revision)
            except OSError:
                pass
            return updated

    def draft(self, notebook: str, material: str) -> dict | None:
        with self.store.lock:
            self.get(notebook, material)
            path = self._draft_path(notebook, material)
            return json.loads(read_text(path)) if path.exists() else None

    def save_draft(self, notebook: str, material: str, request: PresentationDraftUpdate | dict) -> dict:
        with self.store.lock:
            item = self.get(notebook, material)
            document = self._prepare(item, request, draft=True)
            # Drafts retain user data, while review-state changes are applied on Save.
            request = PresentationDraftUpdate.model_validate(request)
            result = {
                "expected_revision": document.revision,
                "presentation": request.presentation.model_dump(),
                "updated_at": now(),
            }
            write_json(self._draft_path(notebook, material), result)
            return result

    def discard_draft(self, notebook: str, material: str, revision: int):
        with self.store.lock:
            draft = self.draft(notebook, material)
            if draft is None:
                return
            if draft["expected_revision"] != revision:
                raise ConflictError("A newer presentation draft exists.")
            self._draft_path(notebook, material).unlink()
