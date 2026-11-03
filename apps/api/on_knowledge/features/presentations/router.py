"""Authenticated editing and offline rendering of an exact saved deck revision."""

from typing import Literal

from fastapi import APIRouter, Query
from fastapi.responses import Response

from ...storage import ConflictError
from .repository import PresentationRepository
from .schemas import Presentation, PresentationDraftUpdate, PresentationUpdate


def create_router(repository: PresentationRepository) -> APIRouter:
    router = APIRouter(prefix="/api/notebooks/{notebook}/materials/{material}/presentation")

    def saved(notebook, material, revision):
        item = repository.get(notebook, material)
        document = Presentation.model_validate(item["presentation"])
        if document.revision != revision:
            raise ConflictError("The saved presentation changed. Refresh before exporting.")
        return document, item["answer"]["citations"]

    @router.patch("")
    def save(notebook: str, material: str, body: PresentationUpdate):
        return repository.update(notebook, material, body)

    @router.get("/draft")
    def draft(notebook: str, material: str):
        return repository.draft(notebook, material)

    @router.put("/draft")
    def save_draft(notebook: str, material: str, body: PresentationDraftUpdate):
        return repository.save_draft(notebook, material, body)

    @router.delete("/draft", status_code=204)
    def discard(notebook: str, material: str, revision: int = Query(ge=1)):
        repository.discard_draft(notebook, material, revision)
        return Response(status_code=204)

    @router.get("/revisions/{revision}")
    def revision_get(notebook: str, material: str, revision: int):
        return repository.revision(notebook, material, revision)

    @router.get("/preview")
    def preview(notebook: str, material: str, revision: int = Query(ge=1)):
        from .exports import presentation_preview

        document, citations = saved(notebook, material, revision)
        return {"pages": presentation_preview(document, citations), "width": 960, "height": 540}

    @router.get("/export")
    def export(notebook: str, material: str, format: Literal["pptx", "pdf"], revision: int = Query(ge=1)):
        from .exports import export_presentation

        document, citations = saved(notebook, material, revision)
        if document.stage != "slides":
            raise ValueError("Generate slides from the approved outline before exporting.")
        data = export_presentation(document, citations, format)
        media = {
            "pdf": "application/pdf",
            "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        }
        return Response(
            data,
            media_type=media[format],
            headers={
                "Content-Disposition": f'attachment; filename="racall-presentation-r{revision}.{format}"'
            },
        )

    return router
