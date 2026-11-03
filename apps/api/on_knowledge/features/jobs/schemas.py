from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ...storage import identifier
from ..context.schemas import ContextSelection

GenerationKind = Literal[
    "research", "summary", "study_guide", "review_questions", "presentation_outline", "presentation"
]


class GenerationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str
    kind: GenerationKind
    question: str = Field(default="", max_length=8000)
    title: str = Field(default="", max_length=200)
    language: Literal["en", "ru"] = "en"
    context: ContextSelection = Field(default_factory=ContextSelection)
    template: Literal["light", "dark"] = "light"
    outline_id: str | None = None
    outline_revision: int | None = Field(default=None, ge=1, strict=True)

    @field_validator("request_id")
    @classmethod
    def request(cls, value):
        return identifier(value)

    @field_validator("outline_id")
    @classmethod
    def outline_identifier(cls, value):
        return identifier(value) if value is not None else None

    @field_validator("question", "title")
    @classmethod
    def clean(cls, value):
        return value.strip()

    @model_validator(mode="after")
    def research_question(self):
        if self.kind == "research" and not self.question:
            raise ValueError("A research question is required.")
        if self.kind == "presentation":
            if self.outline_id is None or self.outline_revision is None:
                raise ValueError("A saved outline and its approved revision are required.")
            if self.context != ContextSelection():
                raise ValueError("Slide generation uses the approved outline's context.")
        elif self.outline_id is not None or self.outline_revision is not None:
            raise ValueError("Outline approval is only valid for slide generation.")
        if self.kind.startswith("presentation") and len(self.title) > 160:
            raise ValueError("Presentation titles must not exceed 160 characters.")
        return self


class RetryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str

    @field_validator("request_id")
    @classmethod
    def request(cls, value):
        return identifier(value)
