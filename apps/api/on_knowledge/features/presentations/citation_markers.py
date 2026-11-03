"""Format generated evidence-label groups using the saved citation numbering."""

import re

from .schemas import Slide

_BRACKETS = re.compile(r"(?<!\\)(?<!\[)\[([^\[\]\r\n]*)\](?!\])")
_LABEL_GROUP = re.compile(r"E[0-9]+(?:[ \t]*,[ \t]*E[0-9]+)*")


def canonical_markers(text: str, numbers: dict[str, int], allowed: set[str]) -> str:
    """Change complete all-E groups only; mixed prose is never rewritten."""

    def replace(match):
        content = match[1].strip(" \t")
        if not _LABEL_GROUP.fullmatch(content):
            return match[0]
        labels = [label.strip(" \t") for label in content.split(",")]
        if any(label not in allowed or label not in numbers for label in labels):
            raise ValueError("An inline citation must reference evidence declared on its slide.")
        return " ".join(f"[{numbers[label]}]" for label in labels)

    return _BRACKETS.sub(replace, text)


def canonicalize_generated_citations(
    slides: list[Slide], references: dict, citations: list[dict]
) -> list[Slide]:
    numbers = {item["id"]: item["number"] for item in citations}
    labels = {label: numbers[item["id"]] for label, item in references.items() if item["id"] in numbers}
    result = []
    for slide in slides:
        if slide.review_state != "generated":
            result.append(slide)
            continue
        allowed = {label for label, item in references.items() if item["id"] in slide.evidence_ids}
        result.append(
            Slide.model_validate(
                {
                    **slide.model_dump(),
                    "title": canonical_markers(slide.title, labels, allowed),
                    "bullets": [canonical_markers(text, labels, allowed) for text in slide.bullets],
                    "notes": canonical_markers(slide.notes, labels, allowed),
                }
            )
        )
    return result
