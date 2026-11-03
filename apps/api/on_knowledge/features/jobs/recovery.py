"""Recover durable results by their format's integrity contract, not AI certainty."""

from ..presentations.assembly import matches_assembled_material
from ..presentations.markdown import presentation_markdown
from ..presentations.schemas import Presentation


def _outline_identity(job, material, document):
    expected = {
        "id": job["id"],
        "kind": "presentation_outline",
        "title": job["title"],
        "context": job["context"],
        "provider": job["provider"],
        "instructions": job["question"],
    }
    return all(material.get(key) == value for key, value in expected.items()) and (
        document.stage,
        document.title,
        document.language,
        document.template,
    ) == ("outline", job["title"], job["language"], job.get("template", "light"))


def _outline_citations(document, citations):
    if not isinstance(citations, list) or not citations:
        return False
    ids = [citation["id"] for citation in citations]
    if len(set(ids)) != len(ids):
        return False
    if any(citation["number"] != index for index, citation in enumerate(citations, 1)):
        return False
    return all(slide.evidence_ids for slide in document.slides) and {
        key for slide in document.slides for key in slide.evidence_ids
    } == set(ids)


def _matches_outline(job, material):
    document = Presentation.model_validate(material["presentation"])
    citations = material["answer"]["citations"]
    return (
        _outline_identity(job, material, document)
        and _outline_citations(document, citations)
        and material["body"] == presentation_markdown(document, citations)
    )


def matches_saved_material(job: dict, material: dict | None) -> bool:
    """Recognition of a completed write; never semantic approval or file migration."""
    if not material or material.get("job_id") != job["id"]:
        return False
    try:
        if job["kind"] == "presentation":
            return matches_assembled_material(job, material)
        if job["kind"] == "presentation_outline":
            return _matches_outline(job, material)
        return bool(material["answer"].get("validated"))  # Existing 0.3 result contract.
    except (KeyError, TypeError, ValueError):
        return False
