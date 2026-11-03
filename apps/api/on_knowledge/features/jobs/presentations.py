"""Pin an approved outline without holding a worker while a person reviews it."""

from copy import deepcopy

from ...storage import ConflictError
from ..presentations.assembly import approval_marker, outline_snapshot
from ..presentations.schemas import Presentation


def approved_outline(notebook, request, materials, context):
    material = materials.get(notebook, request.outline_id)
    if material.get("kind") != "presentation_outline":
        raise ValueError("Choose a saved presentation outline.")
    outline = Presentation.model_validate(material["presentation"])
    if outline.stage != "outline":
        raise ValueError("Choose a saved presentation outline.")
    if outline.revision != request.outline_revision:
        raise ConflictError("The outline changed. Review it before generating slides.")
    if request.question and request.question != material.get("instructions", ""):
        raise ValueError("Edit and save the outline before assembling slides.")
    snapshot = deepcopy(material["context"])
    context.validate_snapshot(notebook, snapshot)
    accepted = outline_snapshot(material)
    return {
        "context": snapshot,
        "title": outline.title,
        "question": material.get("instructions", ""),
        "language": outline.language,
        "template": outline.template,
        "outline_id": material["id"],
        "outline_revision": outline.revision,
        "provider": deepcopy(material.get("provider", {})),
        "assembly": approval_marker(accepted),
        "_outline_snapshot": accepted,
    }
