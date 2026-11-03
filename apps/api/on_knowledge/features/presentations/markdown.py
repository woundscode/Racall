"""Readable note copies preserve source quotations alongside editable slide text."""

from ..studio.markdown import location_label
from .schemas import Presentation


def presentation_markdown(document: Presentation, citations: list[dict]) -> str:
    numbers = {item["id"]: item.get("number", index) for index, item in enumerate(citations, 1)}
    lines = ["# " + document.title, ""]
    for index, slide in enumerate(document.slides, 1):
        refs = " ".join(f"[{numbers[value]}]" for value in slide.evidence_ids if value in numbers)
        lines.extend([f"## {index}. {slide.title} {refs}".rstrip(), ""])
        lines.extend("- " + bullet for bullet in slide.bullets)
        if slide.notes:
            lines.extend(
                [
                    "",
                    ("Заметки докладчика" if document.language == "ru" else "Speaker notes") + ":",
                    slide.notes,
                ]
            )
        lines.append("")
    lines.extend(["## " + ("Источники" if document.language == "ru" else "Sources"), ""])
    for index, item in enumerate(citations, 1):
        lines.extend(
            [
                f"[{item.get('number', index)}] {item['title']} — "
                + location_label(item.get("location", {}), document.language),
                f"{item.get('version', '')}",
                "",
                "\n".join("> " + line for line in item["quote"].splitlines()),
                "",
            ]
        )
    return "\n".join(lines)
