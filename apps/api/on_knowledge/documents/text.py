"""Markdown/text block boundaries, headings, code fences and source lines."""

import re

from .models import Element

_FENCE = re.compile(r" {0,3}(`{3,}|~{3,})(.*)")


def _opening_fence(line: str) -> str | None:
    match = _FENCE.fullmatch(line)
    if match and not (match[1][0] == "`" and "`" in match[2]):
        return match[1]
    return None


def _closes_fence(line: str, opening: str) -> bool:
    match = _FENCE.fullmatch(line)
    return bool(
        match and match[1][0] == opening[0] and len(match[1]) >= len(opening) and not match[2].strip(" \t")
    )


def text_elements(text: str, page: int | None = None) -> list[Element]:
    result, lines, heading, start, fence = [], [], "", 1, None

    def flush(end):
        if lines:
            result.append(
                Element(
                    text="\n".join(lines),
                    page=page,
                    section=heading,
                    type="code" if fence else "paragraph",
                    line_start=start,
                    line_end=end,
                )
            )
            lines.clear()

    for i, line in enumerate(text.splitlines(), 1):
        if fence is not None:
            lines.append(line)
            if _closes_fence(line, fence):
                flush(i)
                fence = None
        elif (opening := _opening_fence(line)) is not None:
            flush(i - 1)
            fence, start = opening, i
            lines.append(line)
        elif re.match(r"^#{1,6}\s", line):
            flush(i - 1)
            heading = line.lstrip("# ")
            result.append(
                Element(type="heading", text=line, page=page, section=heading, line_start=i, line_end=i)
            )
        elif not line.strip():
            flush(i - 1)
        else:
            if not lines:
                start = i
            lines.append(line)
    flush(len(text.splitlines()))
    return result
