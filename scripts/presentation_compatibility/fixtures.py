"""Synthetic, bounded export fixtures derived from the EN/RU release records."""

from dataclasses import dataclass

from on_knowledge.features.presentations.schemas import Presentation

from scripts.evaluate_presentations import FIXTURES


@dataclass(frozen=True)
class Case:
    name: str
    document: Presentation
    citations: list[dict]


def regular(language: str, template: str) -> Case:
    fixture = FIXTURES[language]
    facts = [sentence.rstrip(".") + "." for sentence in fixture["source"].split(". ")]
    headings = (
        ["План станции «Лис»", "Результаты и решения совещания"]
        if language == "ru"
        else ["Marigold station plan", "Results and review meeting"]
    )
    citations = [
        {
            "id": key,
            "source_id": f"compatibility-{language}-{key}",
            "version": "v-" + "0123456789abcdef" * 4,
            "title": title,
            "quote": fixture[field],
            "location": {"page": number},
        }
        for key, title, field, number in (
            ("source", f"station-{language}.md", "source", 3),
            ("note", "Meeting record / Запись совещания", "note", 4),
        )
    ]
    document = Presentation.model_validate(
        {
            "stage": "slides",
            "title": fixture["title"],
            "language": language,
            "template": template,
            "slides": [
                {
                    "id": "plan",
                    "layout": "title",
                    "title": headings[0],
                    "bullets": [" ".join(facts[:2]), facts[2]],
                    "notes": " ".join(facts[:3]),
                    "evidence_ids": ["source"],
                },
                {
                    "id": "results",
                    "layout": "bullets",
                    "title": headings[1],
                    "bullets": [facts[3], fixture["note"]],
                    "notes": facts[3] + " " + fixture["note"],
                    "evidence_ids": ["source", "note"],
                    "review_state": "edited",
                },
            ],
        }
    )
    return Case(f"{language}-{template}", document, citations)


def limits(language: str, template: str) -> Case:
    case = regular(language, template)
    document = case.document.model_copy(deep=True)
    slide = document.slides[0]
    # Maximum schema lengths that still fit. Narrow unbroken tokens test the
    # layout's character wrapping; this is a typography fixture, not a claim.
    prefix = "Предел " if language == "ru" else "Limit "
    slide.title = "i" * 160
    slide.layout = "section"
    slide.bullets = [prefix + "i" * (220 - len(prefix))]
    slide.notes = ((FIXTURES[language]["note"] + " ") * 20)[:1200]
    document.slides = [slide]
    return Case(
        f"limits-{language}-{template}", Presentation.model_validate(document.model_dump()), case.citations
    )


def cases() -> list[Case]:
    return [regular(language, template) for language in ("en", "ru") for template in ("light", "dark")] + [
        limits("en", "light"),
        limits("ru", "dark"),
    ]
