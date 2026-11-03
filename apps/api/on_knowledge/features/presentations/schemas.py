"""Bounded portable presentation data; no executable model output."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
Bullet = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=220)]
EvidenceId = Annotated[str, StringConstraints(min_length=1, max_length=300)]


class Slide(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[a-zA-Z0-9_-]{1,64}$")
    layout: Literal["title", "section", "bullets"] = "bullets"
    title: Title
    bullets: list[Bullet] = Field(default_factory=list, max_length=5)
    notes: str = Field(default="", max_length=1200)
    evidence_ids: list[EvidenceId] = Field(default_factory=list, max_length=16)
    review_state: Literal["generated", "edited"] = "generated"


class Presentation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[1] = 1
    revision: int = Field(default=1, ge=1, strict=True)
    stage: Literal["outline", "slides"]
    title: Title
    language: Literal["en", "ru"] = "en"
    template: Literal["light", "dark"] = "light"
    slides: list[Slide] = Field(min_length=1, max_length=12)

    @model_validator(mode="after")
    def unique_slides(self):
        if len({slide.id for slide in self.slides}) != len(self.slides):
            raise ValueError("Slide IDs must be unique.")
        return self


class PresentationUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expected_revision: int = Field(ge=1, strict=True)
    presentation: Presentation

    @model_validator(mode="after")
    def matching_revision(self):
        if self.presentation.revision != self.expected_revision:
            raise ValueError("The document and expected revision must match.")
        return self


class DraftSlide(Slide):
    title: str = Field(max_length=160)
    bullets: list[Annotated[str, StringConstraints(max_length=220)]] = Field(
        default_factory=list, max_length=5
    )


class DraftPresentation(Presentation):
    title: str = Field(max_length=160)
    slides: list[DraftSlide] = Field(min_length=1, max_length=12)


class PresentationDraftUpdate(PresentationUpdate):
    presentation: DraftPresentation
