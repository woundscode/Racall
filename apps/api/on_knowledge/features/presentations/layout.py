"""One measured layout for editable PPTX, PDF and the browser's SVG preview."""

from dataclasses import dataclass, field

from .font_support import text_width
from .schemas import Presentation, Slide

WIDTH, HEIGHT = 960, 540
MARGIN = 56
CONTENT_WIDTH = WIDTH - MARGIN * 2


class LayoutOverflow(ValueError):
    """A slide needs shorter text, instead of silently clipping its content."""


@dataclass(frozen=True)
class TextLine:
    text: str
    x: float
    baseline: float
    size: float
    color: str
    bold: bool = False


@dataclass
class Page:
    background: str
    foreground: str
    muted: str
    lines: list[TextLine] = field(default_factory=list)
    notes: str = ""


def _theme(document: Presentation) -> Page:
    if document.template == "dark":
        return Page("#171717", "#FAFAFA", "#B7B7B7")
    return Page("#FFFFFF", "#202020", "#666666")


def wrap_text(text: str, size: float, width: float = CONTENT_WIDTH, *, bold=False) -> list[str]:
    """Wrap at words; split long URLs/tokens without discarding any characters."""
    result = []
    for paragraph in text.expandtabs(4).split("\n"):
        line = ""
        for word in paragraph.split(" "):
            candidate = f"{line} {word}" if line else word
            if text_width(candidate, size, bold) <= width:
                line = candidate
                continue
            if line:
                result.append(line)
                line = ""
            for character in word:
                if text_width(line + character, size, bold) > width:
                    if not line:
                        raise LayoutOverflow("A presentation character exceeds the available width.")
                    result.append(line)
                    line = ""
                line += character
        result.append(line)
    return result


def _add_lines(page: Page, text: list[str], y: float, size: float, *, x=MARGIN, bold=False, color=None):
    for line in text:
        page.lines.append(TextLine(line, x, y, size, color or page.foreground, bold))
        y += size * 1.3
    return y


def _citation_index(citations: list[dict]) -> dict[str, tuple[int, dict]]:
    result = {}
    for index, citation in enumerate(citations, 1):
        key = citation["id"]
        if key in result:
            raise ValueError("Duplicate presentation citation.")
        result[key] = (index, citation)
    return result


def _reference_text(citation: dict, index: int, language: str) -> str:
    location = citation.get("location") or {}
    page = location.get("page")
    prefix = "стр." if language == "ru" else "page"
    metadata = f"{citation.get('source_id', '')} · {citation.get('version', '')}"
    if page is not None:
        metadata += f" · {prefix} {page}"
    return f"[{index}] {citation.get('title', '')}\n{metadata}\n{citation.get('quote', '')}"


def _content_page(document: Presentation, slide: Slide, index: dict, number: int) -> Page:
    page = _theme(document)
    label = "План" if document.stage == "outline" and document.language == "ru" else "Outline"
    if document.stage != "outline":
        label = "Racall"
    _add_lines(page, [label], 43, 12, color=page.muted)
    title_size = 40 if slide.layout in {"title", "section"} else 34
    title_lines = wrap_text(slide.title, title_size, bold=True)
    if len(title_lines) > 3:
        raise LayoutOverflow("Shorten the slide title: it does not fit the presentation layout.")
    y = _add_lines(page, title_lines, 116, title_size, bold=True) + 24
    body_size, groups = _body_layout(slide.bullets, y)
    for lines in groups:
        _add_lines(page, ["•"], y, body_size)
        y = _add_lines(page, lines, y, body_size, x=MARGIN + 24) + 14
    refs = _slide_references(slide, index)
    review = "Изменено вручную" if document.language == "ru" else "Edited manually"
    footer = " ".join(refs)
    if slide.review_state == "edited":
        footer = f"{footer} · {review}".strip(" ·")
    _add_lines(page, [footer], 489, 12, color=page.muted)
    _add_lines(page, [str(number)], 513, 12, x=WIDTH - MARGIN - 20, color=page.muted)
    references = [
        _reference_text(index[key][1], index[key][0], document.language) for key in slide.evidence_ids
    ]
    page.notes = "\n\n".join([slide.notes, *references]).strip()
    return page


def _body_layout(bullets: list[str], y: float) -> tuple[int, list[list[str]]]:
    for size in (24, 22, 20, 18):
        groups = [wrap_text(bullet, size, CONTENT_WIDTH - 24) for bullet in bullets]
        height = sum(len(lines) * size * 1.3 + 14 for lines in groups)
        if y + height <= 450:
            return size, groups
    raise LayoutOverflow("Shorten the slide text: it does not fit at the minimum readable font size.")


def _slide_references(slide: Slide, index: dict) -> list[str]:
    refs = []
    for evidence_id in slide.evidence_ids:
        if evidence_id not in index:
            raise ValueError("A presentation citation is missing from the saved evidence.")
        refs.append(f"[{index[evidence_id][0]}]")
    return refs


def _appendix(document: Presentation, heading: str, paragraphs: list[str]) -> list[Page]:
    pages = []
    page = _theme(document)

    def begin():
        nonlocal page
        page = _theme(document)
        _add_lines(page, [heading], 74, 25, bold=True)
        pages.append(page)

    begin()
    y = 116
    for paragraph in paragraphs:
        for line in wrap_text(paragraph, 16):
            if y > 480:
                begin()
                y = 116
            _add_lines(page, [line], y, 16)
            y += 22
        y += 14
    return pages


def layout_presentation(document: Presentation, citations: list[dict]) -> list[Page]:
    """Lay out slides first, then printable notes and exact evidence appendices."""
    index = _citation_index(citations)
    if sum(len(str(item)) for item in citations) > 200_000:
        raise ValueError("Presentation citation text exceeds the export limit.")
    pages = [_content_page(document, slide, index, i) for i, slide in enumerate(document.slides, 1)]
    notes = [
        f"{i}. {slide.title}\n{slide.notes}" for i, slide in enumerate(document.slides, 1) if slide.notes
    ]
    if notes:
        heading = "Заметки докладчика" if document.language == "ru" else "Speaker notes"
        pages.extend(_appendix(document, heading, notes))
    used = set(key for slide in document.slides for key in slide.evidence_ids)
    references = [
        _reference_text(citation, i, document.language) for key, (i, citation) in index.items() if key in used
    ]
    if references:
        heading = "Источники" if document.language == "ru" else "Sources"
        pages.extend(_appendix(document, heading, references))
    return pages
