"""Whole Markdown blocks with offsets into the unchanged saved note body."""

from itertools import accumulate

from ...documents.text import text_elements


def note_ranges(body: str, *, size: int):
    """Pack adjacent blocks up to a soft target, never split an oversized block.

    Reuse the document parser's paragraph/fence boundaries, but derive offsets
    from the original lines so CRLF and whitespace remain exact source data.
    """
    if size <= 0:
        raise ValueError("The note passage size must be positive.")
    lines = body.splitlines(keepends=True)
    offsets = list(accumulate(map(len, lines), initial=0))
    pending = None
    for element in text_elements(body):
        first, last = element.line_start, element.line_end
        start = offsets[first - 1]
        end = offsets[last - 1] + len(lines[last - 1].rstrip("\r\n"))
        if pending is not None and end - pending[0] > size:
            yield pending
            pending = None
        pending = (start, end, first, last) if pending is None else (pending[0], end, pending[2], last)
    if pending is not None:
        yield pending
