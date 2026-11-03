"""Parse source-anchored facts once; slide fields only reuse those exact texts."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, ValidationError

from ...storage import uid
from .errors import PresentationProtocolError
from .schemas import Slide

FactId = Annotated[str, StringConstraints(pattern=r"^F[1-9][0-9]{0,2}$")]
FactText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=220)]


class ProtocolRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Anchor(ProtocolRecord):
    evidence_id: str = Field(min_length=1, max_length=300)
    quote: str = Field(min_length=1, max_length=24000)


class Fact(ProtocolRecord):
    id: FactId
    text: FactText
    evidence: list[Anchor] = Field(min_length=1, max_length=16)


class DraftSlide(ProtocolRecord):
    layout: Literal["title", "section", "bullets"]
    title_id: FactId
    bullet_ids: list[FactId] = Field(max_length=5)
    note_ids: list[FactId] = Field(max_length=5)


class OutlineDraft(ProtocolRecord):
    claims: list[Fact] = Field(min_length=1, max_length=60)
    slides: list[DraftSlide] = Field(min_length=1, max_length=12)


def validate_anchors(anchors: list[Anchor], passages: dict[str, dict]) -> None:
    """An exact substring proves provenance only, never semantic support."""
    seen = set()
    for anchor in anchors:
        passage = passages.get(anchor.evidence_id)
        key = (anchor.evidence_id, anchor.quote)
        if passage is None or not anchor.quote.strip() or anchor.quote not in passage["quote"] or key in seen:
            raise PresentationProtocolError("Invalid or repeated exact source anchor.")
        seen.add(key)


def _compile_slide(item: DraftSlide, facts: dict[str, Fact]) -> Slide:
    ids = [item.title_id, *item.bullet_ids, *item.note_ids]
    if any(key not in facts for key in ids):
        raise PresentationProtocolError("Slide refers to an unknown fact.")
    if item.layout != "bullets" and item.bullet_ids:
        raise PresentationProtocolError("Title and section layouts cannot contain bullets.")
    if any(len(set(group)) != len(group) for group in (item.bullet_ids, item.note_ids)):
        raise PresentationProtocolError("A slide field repeats a fact.")
    references = dict.fromkeys(anchor.evidence_id for key in ids for anchor in facts[key].evidence)
    return Slide(
        id=uid(),
        layout=item.layout,
        title=facts[item.title_id].text,
        bullets=[facts[key].text for key in item.bullet_ids],
        notes="\n".join(facts[key].text for key in item.note_ids),
        evidence_ids=list(references),
    )


def parse_outline(raw: object, evidence: list[dict]) -> tuple[list[dict], list[Slide]]:
    """Reject malformed drafts without truncating facts, anchors or slide fields."""
    try:
        draft = OutlineDraft.model_validate(raw)
        facts = {fact.id: fact for fact in draft.claims}
        if len(facts) != len(draft.claims):
            raise PresentationProtocolError("Fact IDs must be unique.")
        passages = {item["id"]: item for item in evidence}
        for fact in draft.claims:
            validate_anchors(fact.evidence, passages)
        slides = [_compile_slide(item, facts) for item in draft.slides]
        used = {key for item in draft.slides for key in [item.title_id, *item.bullet_ids, *item.note_ids]}
        if used != set(facts):
            raise PresentationProtocolError("Every fact must appear in a slide.")
        return [fact.model_dump() for fact in draft.claims], slides
    except ValidationError as error:
        raise PresentationProtocolError("Invalid presentation writer contract.") from error
