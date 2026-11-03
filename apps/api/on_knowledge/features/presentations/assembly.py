"""Assemble reviewed slide content without rewriting it or certifying its facts."""

import json
from copy import deepcopy
from hashlib import sha256

from .markdown import presentation_markdown
from .schemas import Presentation


def outline_snapshot(material: dict) -> dict:
    """Freeze the approved document and the evidence it was reviewed against."""
    document = Presentation.model_validate(material["presentation"])
    if document.stage != "outline":
        raise ValueError("Only an approved outline can be assembled.")
    return deepcopy(
        {
            "outline_id": material["id"],
            "presentation": document.model_dump(),
            "answer": material["answer"],
            "context": material["context"],
            "context_info": material.get("context_info", {}),
            "instructions": material.get("instructions", ""),
        }
    )


def approval_marker(snapshot: dict) -> dict:
    """An identity/integrity marker for approval, never a factual verdict."""
    encoded = json.dumps(snapshot, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return {
        "schema_version": 1,
        "method": "approved_outline",
        "outline_id": snapshot["outline_id"],
        "outline_revision": snapshot["presentation"]["revision"],
        "content_sha256": sha256(encoded.encode("utf-8")).hexdigest(),
    }


def assemble_presentation(job: dict) -> dict:
    snapshot = deepcopy(job["_outline_snapshot"])
    marker = approval_marker(snapshot)
    if (
        job.get("assembly") != marker
        or job["outline_id"] != marker["outline_id"]
        or job["outline_revision"] != marker["outline_revision"]
        or job["context"] != snapshot["context"]
    ):
        raise ValueError("The approved outline snapshot does not match its approval.")
    outline = Presentation.model_validate(snapshot["presentation"])
    if outline.stage != "outline":
        raise ValueError("Only an approved outline can be assembled.")
    answer = snapshot["answer"]
    citations = answer["citations"]
    references = {citation["id"] for citation in citations}
    if any(key not in references for slide in outline.slides for key in slide.evidence_ids):
        raise ValueError("The approved outline contains an unknown citation.")
    document = outline.model_copy(update={"stage": "slides", "revision": 1})
    # Carry prior verification forward only for unchanged generated content.
    # A user's approval is not an AI or human factual verification certificate.
    if any(slide.review_state == "edited" for slide in document.slides):
        answer.update(validated=False, claims=[])
    answer["mode"] = "presentation_assembled"
    return {
        "body": presentation_markdown(document, citations),
        "answer": answer,
        "instructions": snapshot["instructions"],
        "presentation": document.model_dump(),
        "context_info": snapshot["context_info"],
        "outline_id": marker["outline_id"],
        "outline_revision": marker["outline_revision"],
        "assembly": marker,
    }


def matches_assembled_material(job: dict, material: dict) -> bool:
    """Recover a durable assembly only when it matches the accepted snapshot."""
    try:
        expected = assemble_presentation(job)
        return (
            material.get("kind") == "presentation"
            and material.get("context") == job["context"]
            and material.get("title") == expected["presentation"]["title"]
            and all(material.get(key) == value for key, value in expected.items())
        )
    except (KeyError, TypeError, ValueError):
        return False
